import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from r2e.paths import REPOS_DIR, GRAPHS_DIR
from r2e.models.identifier import Identifier
from r2e.models.callgraph import CallGraph


class Repo(BaseModel):
    repo_org: str
    repo_name: str
    repo_id: str
    local_repo_path: str

    _cached_callgraph: Optional[CallGraph] = None

    @property
    def callgraph_path(self) -> str:
        return os.path.join(GRAPHS_DIR, self.repo_id + "_cgraph.json")

    @classmethod
    def from_file_path(cls, file_path: Path | str) -> "Repo":
        if isinstance(file_path, Path):
            file_path = str(file_path)
        # NOTE: this is a hacky way to get the repo path
        repo_path = file_path.split(str(REPOS_DIR))[1].split("/")[1]
        try:
            repo_org, repo_name = repo_path.split("___")
        except:
            repo_org = repo_path
            repo_name = repo_path

        return cls(
            repo_org=repo_org,
            repo_name=repo_name,
            repo_id=repo_path,
            local_repo_path=repo_path,
        )

    @property
    def repo_path(self) -> str:
        return os.path.join(REPOS_DIR, self.repo_id)

    @property
    def callgraph(self) -> CallGraph:
        if self._cached_callgraph is None:
            self._cached_callgraph = CallGraph.from_json(self.callgraph_path)
        return self._cached_callgraph

    def __hash__(self) -> int:
        return hash(self.repo_id)

    def list_repo_files(self) -> list[str]:
        all_files = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                all_files.append(os.path.join(root, file))
        return all_files

    @property
    def execution_repo_data(self) -> dict[str, str]:
        return {
            "repo_id": self.repo_id,
            "repo_path": self.repo_id,
        }
