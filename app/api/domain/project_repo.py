from sqlalchemy.ext.asyncio import AsyncSession

from app.api.db.models import ProjectStat, Issue
from app.api.db.session import SessionHandler
from app.gh_api.gh import ProjectName


async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with SessionHandler().async_session() as session:
        yield session
        await session.commit()


class ProjectStatRepo:
    def __init__(self, session_handler):
        self.session_handler = session_handler

    async def get(self, name: ProjectName):
        async with self.session_handler.async_session() as s:
            return await s.get(ProjectStat, name)

    async def add(self, stat: ProjectStat):
        async with self.session_handler.async_session() as s:
            s.add(stat)
            await s.commit()


class IssueRepo:
    def __init__(self, session_handler):
        self.session_handler = session_handler

    async def add(self, i: Issue):
        async with self.session_handler.async_session() as s:
            s.add(i)
            await s.commit()
