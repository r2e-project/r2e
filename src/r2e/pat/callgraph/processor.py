import os
import ast
import json
from typing import TYPE_CHECKING

from r2e.models.callgraph import CallGraph
from r2e.models.repo import Repo
from r2e.models.identifier import Identifier
from r2e.pat.modules.explorer import ModuleExplorer
from r2e.pat.imports.resolver import ImportResolver
from r2e.utils.models import get_module_from_identifier, get_type_from_identifier


from r2e.paths import REPOS_DIR
from r2e.logger import logger

if TYPE_CHECKING:
    from r2e.models.module import Module
    from r2e.utils.models import CodeElemType


class CallGraphProcessor:

    @staticmethod
    def normalize_callee_ids(repo: Repo):
        """normalize callee ids in the callgraph to be resolvable."""
        cgraph = repo.callgraph
        stats = {
            "retained": set(),
            "normalized": set(),
            "unresolved_import": set(),
            "unnormalized": set(),
        }

        for caller, callees in cgraph.items():
            caller_file = get_module_from_identifier(caller, repo).local_path

            pkg_root = ModuleExplorer.get_package_root(caller_file)
            pkg_start = os.path.dirname(pkg_root)
            if pkg_start == str(REPOS_DIR):
                pkg_start = pkg_root

            # find unnormalized (hence unresolvable) callees
            unresolved_callees = CallGraphProcessor.get_unresolvable_ids(callees, repo)
            stats["retained"].update(set(callees) - set(unresolved_callees))

            for callee in unresolved_callees:
                callee_parts = callee.identifier.split(".")
                module_parts, function_name = callee_parts[:-1], callee_parts[-1]

                # use caller file and a temp import stmt to resolve callee's id
                temp_node = ast.Import(
                    names=[ast.alias(name=".".join(module_parts), asname=None)]
                )
                callee_file = ImportResolver.resolve_import_path(caller_file, temp_node)

                # if resolved, normalize the callee's id
                if os.path.exists(callee_file):
                    relative_module_path = os.path.relpath(callee_file, start=pkg_start)
                    module_notation = relative_module_path.replace(os.sep, ".")[:-3]

                    # verify that the callee is now resolvable (if not flagged as in_init_file)
                    try:
                        callee.identifier = f"{module_notation}.{function_name}"
                        get_module_from_identifier(callee, repo)
                        stats["normalized"].add(callee)
                    except ValueError as e:
                        stats["unnormalized"].add(callee)
                        pass

                else:
                    stats["unresolved_import"].add(callee)

        return stats

    @staticmethod
    def remove_empty_callees(repo: Repo):
        """remove empty callees from the callgraph."""
        callers_to_check = list(repo.callgraph.keys())

        for caller in callers_to_check:
            callees = repo.callgraph[caller]
            if len(callees) == 0:
                del repo.callgraph[caller]

    @staticmethod
    def remove_unresolvable_callers(repo: Repo):
        """remove unresolvable callers from the callgraph.

        NOTE: these are *rare* callers that are difficult to resolve
        to a module. e.g., a file's __main__ or a deep nested function.
        """

        # find unresolvable callers
        unresolvable_callers = CallGraphProcessor.get_unresolvable_ids(
            list(repo.callgraph.keys()), repo
        )

        for caller in unresolvable_callers:
            del repo.callgraph[caller]

    @staticmethod
    def get_id2type_map(repo: Repo) -> dict[Identifier, "CodeElemType"]:
        cgraph = repo.callgraph
        id2type_map: dict[Identifier, "CodeElemType"] = {}

        unique_ids = set()
        for caller, callees in cgraph.items():
            unique_ids.add(caller)
            unique_ids.update(callees)

        for uid in unique_ids:
            id2type_map[uid] = get_type_from_identifier(uid, repo)

        return id2type_map

    # helper methods

    @staticmethod
    def get_unresolvable_ids(
        identifiers: list[Identifier], repo: Repo
    ) -> list[Identifier]:
        unresolvable_identifiers = []
        for identifier in identifiers:
            try:
                module: Module = get_module_from_identifier(identifier, repo)
            except ValueError:
                unresolvable_identifiers.append(identifier)

        return unresolvable_identifiers
