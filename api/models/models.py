from pydantic import BaseModel, Field


class ProjectStat(BaseModel):
    url: str
    forks_cnt: int
    loc_info: str
