from api.domain.project_repo import ProjectStatRepo
from api.models.models import ProjectStat


class Stat:

    def __init__(self, repo: ProjectStatRepo):
        self.repo = repo

    async def get_stat(self, url: str) -> ProjectStat:
        ps = await self.repo.get(url)
        if ps:
            return ps


    def compute_stat(self, url):


