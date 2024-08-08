from dataclasses import dataclass
import asyncio
import json
from datetime import datetime
from typing import Optional

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


@dataclass
class PR:
    created_at: datetime
    closed_at: datetime
    created_by: str
    closed_by: str
    requested_review: bool


time_format = "%Y-%m-%dT%H:%M:%SZ"


class GHProcessor:
    def __init__(self):
        self.gh_api_client = GHApiClient()

    async def get_median_tt_merge_pr(self, ps: ProjectStat):
        latest_prs = await self.get_latest_merged_prs(ps, n=100)
        if not latest_prs:
            return None, None
        tt_merge = [(pr.closed_at - pr.created_at).days for pr in latest_prs]
        res = int(np.median(tt_merge))
        print(f"Calculating tt_merge for {ps.url}: {tt_merge}, res = {res}")

        return res, sorted(tt_merge)

    async def get_latest_merged_prs(self, ps: ProjectStat, n: int):
        assert n <= 100
        url_list = f"{ProjectNameBuilder.get_api_url(ps.url)}/pulls?per_page={n}&state=closed"
        response = await self.gh_api_client.get_url(url=url_list)
        urls = [pr["url"] for pr in response]
        coros = [self.gh_api_client.get_url(url=url) for url in urls]
        prs = await asyncio.gather(*coros)
        res = []
        for pr_data in prs:
            if not pr_data["merged_by"]:
                continue
            try:
                pr = PR(
                    created_at=datetime.strptime(pr_data['created_at'], time_format),
                    closed_at=datetime.strptime(pr_data['closed_at'], time_format),
                    created_by=pr_data["user"]["login"],
                    closed_by=pr_data["merged_by"]["login"],
                    requested_review=bool(pr_data['requested_reviewers'])
                )
            except KeyError as e:
                raise KeyError(pr_data) from e
            except TypeError as e:
                raise KeyError(pr_data) from e
            # if pr.requested_review and pr.created_by != pr.closed_by:
            if pr.created_by != pr.closed_by:
                res.append(pr)
                if len(res) == n:
                    break

        return res
