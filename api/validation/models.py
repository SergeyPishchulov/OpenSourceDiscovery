import json
from typing import Any, Optional
from typing_extensions import Self
import pydantic_core
from pydantic import BaseModel, Field

from api.db.models import ProjectStat
from sqlalchemy.inspection import inspect


class ProjectStatDTO(BaseModel):
    url: str
    forks_cnt: int
    stars_cnt: int
    size: int
    language: Optional[str] = None
    issue_cnt: int = 0
    commit_cnts: list
    median_tt_merge_pr: Optional[int] = None
    times_to_merge_days: Optional[list] = None

    @classmethod
    def from_orm(cls, ps: ProjectStat) -> Self:
        d = {}
        print(ps.__table__.columns)
        for column in ps.__table__.columns:
            d[column.name] = getattr(ps, column.name)
        try:
            res = ProjectStatDTO(**d)
        except pydantic_core._pydantic_core.ValidationError:
            raise ValueError(f"Error creating pydantic. \n Fields:{d}, \n ProjectStat:{ps}")
        return res
