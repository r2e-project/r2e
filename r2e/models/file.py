from pydantic import BaseModel
from typing import Optional

from r2e.models.module import Module
from r2e.models.repo import Repo
from r2e.paths import REPOS_DIR


class File(BaseModel):
    file_module: Module
    _file_content: Optional[str] = None

    @property
    def file_path(self) -> str:
        return self.file_module.local_path

    @property
    def relative_file_path(self) -> str:
        return self.file_module.relative_module_path

    @property
    def file_id(self) -> str:
        return self.file_module.module_id.identifier

    @property
    def repo(self) -> Repo:
        return self.file_module.repo

    @property
    def _repo_name(self) -> str:
        return self.file_module._repo_name

    @property
    def repo_id(self) -> str:
        return self.file_module.repo_id

    @property
    def file_content(self) -> str:
        if self._file_content is None:
            with open(self.file_path, "r") as file:
                self._file_content = file.read()
        return self._file_content

    def __hash__(self) -> int:
        return hash((self.file_path, self._repo_name, self.file_content))

    @classmethod
    def from_file_path(cls, file_path: str, repo: Repo | None) -> "File":
        file_module = Module.from_file_path(file_path, repo=repo)
        return cls(file_module=file_module)

    def __str__(self) -> str:
        return self.file_path.split(str(REPOS_DIR))[1][1:]

    def __repr__(self) -> str:
        return f"File({self.file_path})"
