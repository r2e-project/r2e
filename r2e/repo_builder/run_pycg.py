import os
import json
from pathlib import Path

from r2e.models import Repo
from r2e.paths import REPOS_DIR, GRAPHS_DIR
from r2e.repo_builder.repo_args import RepoArgs
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.pat.callgraph import CallGraphGenerator, CallGraphProcessor


def construct_pycg(repo: Repo):
    cgraph = CallGraphGenerator.construct_call_graph(repo.repo_path)
    with open(GRAPHS_DIR / f"{repo.repo_id}_cgraph.json", "w") as f:
        json.dump(cgraph, f, indent=4)

    CallGraphProcessor.remove_unresolvable_callers(repo)
    CallGraphProcessor.normalize_callee_ids(repo)

    id2type = CallGraphProcessor.get_id2type_map(repo)
    id2type = {str(k): v.name for k, v in id2type.items()}
    cgdict = repo.callgraph.to_dict()

    new_cgraph = {"graph": cgdict, "id2type": id2type}

    with open(GRAPHS_DIR / f"{repo.repo_id}_cgraph.json", "w") as f:
        json.dump(new_cgraph, f, indent=4)

    return new_cgraph


def run_pycg(repo_args: RepoArgs):
    """
    Runs pycg on all repos in repos_dir except where pycg has already been run
    Also modifies the call graphs using the call-grpah processor storing metadata
    """
    all_repos_clones: list[str] = sorted(os.listdir(REPOS_DIR))
    all_repos = [
        Repo.from_file_path(REPOS_DIR / repo_clone_name)
        for repo_clone_name in all_repos_clones
    ]
    print(f"Running pycg on {len(all_repos)} repos")
    if repo_args.pycg_multiprocess == 0:
        for repo in all_repos:
            if not Path(repo.callgraph_path).exists():
                construct_pycg(repo)
    else:
        outputs = run_tasks_in_parallel_iter(
            construct_pycg,
            all_repos,
            num_workers=repo_args.pycg_multiprocess,
            timeout_per_task=repo_args.pycg_timeout * 60,
            use_progress_bar=True,
            max_mem=8 * 1024 * 1024 * 1024,
        )

        for repo_id, output in zip(all_repos, outputs):
            if output.is_success():
                pass
            else:
                print(f"Failed to run pycg on {repo_id}: {output.exception_tb}")
                continue
