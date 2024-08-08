import uuid

from sqlalchemy import Column, String, INT, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class ProjectStat(Base):
    __tablename__ = "projectstat"

    url = Column(String, nullable=False, unique=True, primary_key=True)  # in format owner/repo
    forks_cnt = Column(INT, nullable=False)
    stars_cnt = Column(INT, nullable=False)
    size = Column(INT, nullable=False)  # in kBytes
    language = Column(String, nullable=True)
    issue_cnt = Column(INT, nullable=False, default=0)
    commit_cnts = Column(JSON, nullable=False)
    median_tt_merge_pr = Column(INT, nullable=True)  # median time from PR opening to merge (in days)
    times_to_merge_days = Column(JSON, nullable=True)
    info = Column(String, default="")


class Issue(Base):
    __tablename__ = "issue"
    id = Column(INT, nullable=False, unique=True, primary_key=True)
    body = Column(String)
    project_url = Column(String)  # , ForeignKey("projectstat.url"))
    comments = Column(JSON, nullable=True)
    gpt_analysis = Column(String)
