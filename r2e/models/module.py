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
        parts = self.module_id.identifier.split(".")
        path = self.repo.repo_path
        segment = ""

        for i, part in enumerate(parts):
            # accumulate a path segment until full path exists
            segment = f"{segment}.{part}" if segment else part
            current_path = os.path.join(path, segment)

            # if the path exists, reset segment
            if os.path.exists(current_path):
                path = current_path
                segment = ""

            elif i == len(parts) - 1:
                # if module is a file, check if it exists
                if self.module_type != ModuleTypeEnum.PACKAGE:
                    py_path = f"{current_path}.py"
                    if os.path.exists(py_path):
                        return py_path

                # if a package, return directory
                return os.path.join(path, segment)

        return path

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
