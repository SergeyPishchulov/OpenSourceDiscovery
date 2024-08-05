import json
import os.path
import shutil
import subprocess
import uuid
from pathlib import Path

from api.db.models import ProjectStat
from api.domain.project_repo import ProjectStatRepo
from conf.config import CFG
from gh_api.gh import ProjectName, ProjectNameBuilder, GHClient

N_FILES = 'n_files'
N_LINES = 'n_lines'


class Wizard:

    def __init__(self, repo: ProjectStatRepo):
        self.repo = repo
        self.gh_client = GHClient()

    async def get_stat(self, name: ProjectName) -> ProjectStat:
        ps = await self.repo.get(name)
        if ps:
            return ps
        stat_json = self.compute_stat_json(name)
        ps: ProjectStat = self.parse_stat_json(name, stat_json)
        await self.add_gh_info(ps)
        await self.repo.add(ps)
        return ps

    async def add_gh_info(self, ps: ProjectStat):
        response: dict = await self.gh_client.get_repo(
            url=ProjectNameBuilder.get_api_url(ps.url))
        ps.forks_cnt = response["forks_count"]
        ps.stars_cnt = response["stargazers_count"]
        ps.language = response["language"]
        # raise Exception(f"THIS IS RESP: {response}")
        return ps

    def parse_stat_json(self, name: ProjectName, j) -> ProjectStat:
        h = j.get('header', None)
        if not h:
            raise Exception("Cloc returned json with no header")
        n_lines = h.get(N_LINES, None)
        if not n_lines:
            raise Exception("Cloc returned json with no n_lines")
        n_files = h.get(N_FILES, None)
        if not n_files:
            raise Exception("Cloc returned json with no n_lines")

        ps = ProjectStat(url=name,
                         n_lines=n_lines, n_files=n_files,
                         info=json.dumps(j))
        return ps

    def compute_stat_json(self, name: ProjectName):
        dir_path = Path(CFG.local_space.dir)
        path = str(dir_path / str(uuid.uuid4()))
        os.mkdir(path)
        full_project_url = ProjectNameBuilder.get_url_by_name(name)
        x = subprocess.run([f"cd {path} && git clone {full_project_url} && cloc . --exclude-dir=venv,osd --json"]
                           , capture_output=True, shell=True)
        ds = x.stdout.decode()
        j = json.loads(ds)
        shutil.rmtree(path)
        return j
