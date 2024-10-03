from pydantic import BaseModel


class Identifier(BaseModel):
    identifier: str

    @classmethod
    def from_relative_path(cls, relative_path: str) -> "Identifier":
        """
        Create an identifier from a path relative to the repo
        """
        if relative_path.endswith(".py"):
            relative_path = relative_path[:-3]
        return cls(identifier=relative_path.replace("/", "."))

    @classmethod
    def from_absolute_path_repo_path(
        cls, absolute_path: str, repo_path: str
    ) -> "Identifier":
        """
        Create an identifier from a absolute path and the repo path
        """
        relative_path = absolute_path.replace(repo_path, "")
        return cls.from_relative_path(relative_path)

    def __str__(self):
        return self.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if isinstance(other, Identifier):
            return self.identifier == other.identifier
        return False
