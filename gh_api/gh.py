import aiohttp

URL_PREFIX = 'https://'
GH_BASE_URL = "github.com"


def get_url(owner, repo):
    return f"{GH_BASE_URL}/{owner}/{repo}"


def get_full_url(owner, repo):
    return f"{URL_PREFIX}{get_url(owner, repo)}"


class GHClient:
    async def get_repo(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
