import json
from typing import Any
from typing_extensions import Self

from pydantic import BaseModel, Field


class ProjectStatDTO(BaseModel):
    url: str
    n_files: int
    n_lines: int
    info: dict

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        return ProjectStatDTO(url=obj.url,
                              n_files=obj.n_files,
                              n_lines=obj.n_lines,
                              info=json.loads(obj.info))
