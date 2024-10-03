from enum import Enum

from pydantic import BaseModel


class Context(BaseModel):
    context_type: str
    context: str
