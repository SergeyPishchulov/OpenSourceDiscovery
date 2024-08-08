import asyncio
import json
from datetime import datetime
import aiohttp
import numpy as np
from api.db.models import ProjectStat
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
    ITEMS_ON_PAGE = 30

    async def get_url(self, url: str):
        assert url.startswith("https")
        async with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   headers={"Authorization": f"Bearer {CFG.github.token}"}) as response:
                text = await response.text()
                return json.loads(text)


class GHProcessor:
    def __init__(self):
        self.gh_api_client = GHApiClient()

    async def get_median_tt_merge_pr(self, ps: ProjectStat):
        latest_prs = await self.get_latest_merged_prs(ps, n=50)
        tt_merge = [(pr["closed_at"] - pr["created_at"]).days for pr in latest_prs]
        res = int(np.median(tt_merge))
        print(f"Calculating tt_merge: {tt_merge}, res = {res}")

        return res

    async def get_latest_merged_prs(self, ps: ProjectStat, n: int):
        assert n <= 100
        url_list = f"{ProjectNameBuilder.get_api_url(ps.url)}/pulls?per_page={n}&state=closed"
        response = await self.gh_api_client.get_url(url=url_list)
        urls = [pr["url"] for pr in response]
        coros = [self.gh_api_client.get_url(url=url) for url in urls]
        prs = await asyncio.gather(*coros)
        res = []
        for pr in prs:
            try:
                pr["closed_by"] = pr.get("closed_by", pr.get("merged_by", None))
                if not pr["closed_by"]:
                    continue
                if pr['requested_reviewers'] and pr["user"] != pr["closed_by"]:
                    copy_fields = ["created_at", "closed_at", "closed_by", "user"]
                    required_info = {k: pr[k] for k in copy_fields}
                    time_format = "%Y-%m-%dT%H:%M:%SZ"

                    required_info["closed_at"] = datetime.strptime(pr['closed_at'], time_format)
                    required_info["created_at"] = datetime.strptime(pr['created_at'], time_format)
                    res.append(required_info)
                    if len(res) == n:
                        break
            except KeyError as e:
                raise KeyError(pr) from e
        return res
