from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import ProjectStat
from api.db.session import SessionHandler


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with SessionHandler().async_session() as session:
        yield session
        await session.commit()


class ProjectRepo:
    def __init__(self, session_handler):
        self.session_handler = session_handler

    async def get(self, url: str):
        async with self.session_handler.async_session() as s:
            return s.query(ProjectStat).filter_by(url=url).first()

    async def add(self, stat: ProjectStat):
        async with self.session_handler.async_session() as s:
            s.add(stat)
            s.commit()
