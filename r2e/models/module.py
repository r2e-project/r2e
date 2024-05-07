import os
from enum import Enum
from pydantic import BaseModel

from r2e.models.repo import Repo
from r2e.models.identifier import Identifier


class ModuleTypeEnum(str, Enum):
    FILE = "file"
    PACKAGE = "package"


class Module(BaseModel):
    module_id: Identifier
    module_type: ModuleTypeEnum = ModuleTypeEnum.FILE
    repo: Repo

    # TODO: maybe don't use . representation for modules/ids

    @property
    def local_path(self) -> str:
        path = self.module_id.identifier.replace(".", "/")
        if self.module_type == ModuleTypeEnum.PACKAGE:
            return f"{self.repo.repo_path}/{path}"
        else:
            return f"{self.repo.repo_path}/{path}.py"

    @property
    def relative_module_path(self) -> str:
        if self.module_type == ModuleTypeEnum.PACKAGE:
            return self.module_id.identifier.replace(".", "/")
        else:
            return f"{self.module_id.identifier.replace('.', '/')}.py"

    @property
    def _repo_name(self) -> str:
        return self.repo.repo_name

    @property
    def repo_id(self) -> str:
        return self.repo.repo_id

    # helper functions

    def exists(self) -> bool:
        return os.path.exists(self.local_path)

    @classmethod
    def from_file_path(cls, file_path: str, repo: Repo | None) -> "Module":
        if repo is None:
            repo = Repo.from_file_path(file_path)
        module_id = Identifier(
            identifier=file_path.replace(repo.repo_path, "")[1:]
            .replace(".py", "")
            .replace("/", ".")
        )
        return cls(module_id=module_id, repo=repo)
