import typing_extensions

from r2e.models.identifier import Identifier
from r2e.models.repo import Repo

# from r2e.models.function import Function
# from r2e.models.method import Method
# from r2e.models.classes import Class
from r2e.models.callgraph import CodeElemType
from r2e.models.file import File
from r2e.models.callgraph import CallGraph

from r2e.logger import logger

# FuncMethClass: typing_extensions.TypeAlias = "Function | Method | Class"


class CallGraphExplorer:
    def __init__(self, repo: Repo):
        self.repo = repo
        self.callgraph: CallGraph = repo.callgraph

    def merge_callgraphs(self, callers: list[Identifier]) -> list[Identifier]:
        merged_callgraph = set()
        for caller_id in callers:
            callees_ids = self.callgraph.get(caller_id, [])
            merged_callgraph.update(callees_ids)

        return list(merged_callgraph)

    def get_callees_from_identifier(self, caller_id: str) -> list:
        from r2e.models import Function, Method, Class

        caller_identifier = Identifier(identifier=caller_id)
        caller_type = self.callgraph.get_type(caller_identifier)
        callees_ids = self.callgraph.get(caller_identifier, [])

        if caller_type == CodeElemType.CLASS:
            class_ = Class.from_id_and_repo(caller_identifier, self.repo)
            class_methods_ids = class_.method_ids
            callees_ids = self.merge_callgraphs([caller_identifier] + class_methods_ids)

        callees: list = []
        for cid in callees_ids:
            callee_type = self.callgraph.get_type(cid)
            try:
                if callee_type == CodeElemType.METHOD:
                    callee = Method.from_id_and_repo(cid, self.repo)

                elif callee_type == CodeElemType.CLASS:
                    callee = Class.from_id_and_repo(cid, self.repo)

                else:
                    callee = Function.from_id_and_repo(cid, self.repo)

                callees.append(callee)
            except ValueError as e:
                # logger.warning(e)
                ## TODO : handle this and add counts...
                pass

        return callees

    def get_callee_count(self, caller_id: str) -> int:
        caller_identifier = Identifier(identifier=caller_id)
        caller_type = self.callgraph.get_type(caller_identifier)
        callees_ids = self.callgraph.get(caller_identifier, [])
        return len(callees_ids)

    def get_callees(self, file: File, function_name: str) -> list:
        module_id = file.file_module.module_id
        function_id = f"{module_id}.{function_name}"
        return self.get_callees_from_identifier(function_id)
