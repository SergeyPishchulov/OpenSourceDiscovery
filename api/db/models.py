import uuid

from sqlalchemy import Column, String, INT
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

    url = Column(String, nullable=False, unique=True, primary_key=True)
    n_files = Column(INT, nullable=False)
    n_lines = Column(INT, nullable=False)
    forks_cnt = Column(INT, nullable=False)
    info = Column(String)
