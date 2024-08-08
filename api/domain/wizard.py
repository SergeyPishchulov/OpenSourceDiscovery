import asyncio
import json
import os.path
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import List

from api.db.models import ProjectStat, Issue
from api.domain.GPTAnalyzer import GPTAnalyzer
from api.domain.project_repo import ProjectStatRepo, IssueRepo
from conf.config import CFG
from gh_api.gh import ProjectName, ProjectNameBuilder, GHApiClient, GHProcessor

N_FILES = 'n_files'
N_LINES = 'n_lines'


class Wizard:

    def __init__(self, repo: ProjectStatRepo, issue_repo: IssueRepo):
        self.repo = repo
        self.issue_repo = issue_repo
        self.gh_api_client = GHApiClient()
        self.gpt_analyzer = GPTAnalyzer()
        self.gh_processor = GHProcessor()

    async def get_stat(self, name: ProjectName) -> ProjectStat:
        ps = await self.repo.get(name)
        if ps:
            return ps
        ps = ProjectStat(url=name)
        await self.add_gh_info(ps)
        # await self.repo.add(ps)
        return ps

    async def add_gh_info(self, ps: ProjectStat):
        query = ProjectNameBuilder.get_api_url(ps.url)
        response: dict = await self.gh_api_client.get_url(
            url=query)
        ps.forks_cnt = response["forks_count"]
        ps.stars_cnt = response["stargazers_count"]
        ps.language = response["language"]
        res = await asyncio.gather(
            self.get_issue_cnt(ps),
            self.get_commits_cnts(ps),
            self.gh_processor.get_median_tt_merge_pr(ps)
        )
        (ps.issue_cnt, ps.commit_cnts, ps.median_tt_merge_pr) = res
        # raise Exception(f"THIS IS RESP: {response}")
        return ps

    async def get_commits_cnts(self, ps):
        full_url = f"{ProjectNameBuilder.get_api_url(ps.url)}/stats/participation"
        response = await self.gh_api_client.get_url(
            url=full_url)
        return response["all"]

    async def get_issue_cnt(self, ps):
        issue_url = f"{ProjectNameBuilder.get_api_url(ps.url)}/issues"
        # TODO for paging see Link header
        response = await self.gh_api_client.get_url(
            url=issue_url)
        return len(response)

    def add_loc_info(self, ps, j):
        h = j.get('header', None)
        if not h:
            raise Exception("Cloc returned json with no header")
        n_lines = h.get(N_LINES, None)
        if not n_lines:
            raise Exception("Cloc returned json with no n_lines")
        n_files = h.get(N_FILES, None)
        if not n_files:
            raise Exception("Cloc returned json with no n_lines")
        ps.n_lines = n_lines
        ps.n_files = n_files
        ps.info = json.dumps(j)

    def get_loc_json(self, name: ProjectName):
        dir_path = Path(CFG.local_space.dir)
        path = str(dir_path / str(uuid.uuid4()))
        os.mkdir(path)
        full_project_url = ProjectNameBuilder.get_url_by_name(name)
        # TODO asyncio.create_subprocess_exec()
        x = subprocess.run([f"cd {path} && git clone {full_project_url} && cloc . --exclude-dir=venv,osd --json"]
                           , capture_output=True, shell=True)
        ds = x.stdout.decode()
        j = json.loads(ds)
        shutil.rmtree(path)
        return j

    def _parse_issue_id(self, url):
        return int(url.split('/')[-1])

    async def get_issue(self, ps: ProjectStat, issue_num: int) -> Issue:
        full_issue_url = f"{ProjectNameBuilder.get_api_url(ps.url)}/issues/{issue_num}"
        body = await self.get_issue_body(full_issue_url)
        new_issue = Issue(id=int(issue_num),
                          body=body,
                          project_url=ps.url,
                          comments=None)
        await self.gpt_analyzer.set_marks_by_body(new_issue)
        await self.issue_repo.add(new_issue)
        return new_issue

    async def get_latest_n_open_true_issue(self, ps: ProjectStat, n: int) -> List[Issue]:
        query = f"{ProjectNameBuilder.get_api_url(ps.url)}/issues?state=open&sort=created&direction=desc"
        response: list = await self.gh_api_client.get_url(url=query)
        res = []
        while response and len(res) < n:
            i = response.pop(0)
            full_issue_url = i["url"]
            is_true_issue = "pull_request" not in i
            if not is_true_issue:
                continue
            body, comments = asyncio.gather(self.get_issue_body(full_issue_url),
                                            self.get_comments(full_issue_url),
                                            )
            new_issue = Issue(id=self._parse_issue_id(full_issue_url),
                              body=body,
                              project_url=ps.url,
                              comments=comments)
            await self.issue_repo.add(new_issue)
            res.append(new_issue)

        return res

    async def get_issue_body(self, full_issue_url):
        response: dict = await self.gh_api_client.get_url(url=full_issue_url)
        return response["body"]

    async def get_comments(self, issue_url):
        query = f"{issue_url}/comments"
        response: list = await self.gh_api_client.get_url(url=query)
        return [c["body"] for c in response]
