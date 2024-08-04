import json
import os.path
import shutil
import subprocess
import uuid
from pathlib import Path

from api.db.models import ProjectStat
from api.domain.project_repo import ProjectStatRepo
from conf.config import CFG

N_FILES = 'n_files'
N_LINES = 'n_lines'


class Wizard:

    def __init__(self, repo: ProjectStatRepo):
        self.repo = repo

    async def get_stat(self, url: str) -> ProjectStat:
        # ps = await self.repo.get(url)
        # if ps:
        #     return ps
        stat_json = self.compute_stat_json(url)
        ps = self.parse_stat_json(url, stat_json)
        await self.repo.add(ps)
        return ps

    def parse_stat_json(self, url, j) -> ProjectStat:
        h = j.get('header', None)
        if not h:
            raise Exception("Cloc returned json with no header")
        n_lines = h.get(N_LINES, None)
        if not n_lines:
            raise Exception("Cloc returned json with no n_lines")
        n_files = h.get(N_FILES, None)
        if not n_files:
            raise Exception("Cloc returned json with no n_lines")

        ps = ProjectStat(url=url,
                         n_lines=n_lines, n_files=n_files,
                         info=json.dumps(j))
        return ps

    def compute_stat_json(self, url):
        dir_path = Path(CFG.local_space.dir)
        path = str(dir_path / str(uuid.uuid4()))
        os.mkdir(path)
        x = subprocess.run([f"cd {path} && git clone {url} && cloc . --exclude-dir=venv,osd --json"]
                           , capture_output=True, shell=True)
        ds = x.stdout.decode()
        j = json.loads(ds)
        shutil.rmtree(path)
        return j


Wizard(1).compute_stat_json('https://github.com/SergeyPishchulov/MixnetBot')
