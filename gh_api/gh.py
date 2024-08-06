import json

import aiohttp

from conf.config import CFG

URL_PREFIX = 'https://'
GH_BASE_URL = "github.com"

ProjectName = str  # in style org/project


class ProjectNameBuilder(str):
    @staticmethod
    def get_url(owner, repo):
        return f"{GH_BASE_URL}/{owner}/{repo}"

    @staticmethod
    def get_api_url(name):
        return f"https://api.github.com/repos/{name}"

    @staticmethod
    def get_url_by_name(name: ProjectName):
        return f"{URL_PREFIX}{GH_BASE_URL}/{name}"

    @staticmethod
    def get_full_url(owner, repo):
        return f"{URL_PREFIX}{ProjectNameBuilder.get_url(owner, repo)}"

    @staticmethod
    def get_name(owner, repo):
        return f"{owner}/{repo}"


class GHApiClient:
    async def get_url(self, url: str):
        assert url.startswith("https")
        async with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   headers={"Authorization": f"Bearer {CFG.github.token}"}) as response:
                text = await response.text()
                return json.loads(text)
