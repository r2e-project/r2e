import json
from collections import ChainMap

from r2e.paths import REPOS_DIR
from r2e.models import FunctionUnderTest, MethodUnderTest


def get_fut_data(
    futs: list[FunctionUnderTest | MethodUnderTest], local: bool = False
) -> tuple[str, str, str]:
    repos = {fut.repo for fut in futs}
    assert len(repos) == 1, "All functions must belong to the same repo"

    repo = repos.pop()
    repo_data = repo.execution_repo_data

    if local:
        repo_path = str(REPOS_DIR / repo.repo_id)
        repo_data = json.dumps({"repo_id": None, "repo_path": repo_path})
    else:
        repo_data = json.dumps(repo.execution_repo_data)

    fut_data = [fut.execution_fut_data for fut in futs]
    fut_names = [x[0] for x in fut_data]
    fut_files = {x[1] for x in fut_data}
    assert len(fut_files) == 1, "All functions must belong to the same file"

    file_path = fut_files.pop()
    fut_data = json.dumps({"funclass_names": fut_names, "file_path": file_path})

    tests = dict(ChainMap(*[fut.tests for fut in futs]))
    test_data = json.dumps({"generated_tests": tests})

    return repo_data, fut_data, test_data
