import json
from contextlib import asynccontextmanager

from peewee import InternalError
from fastapi import FastAPI, APIRouter, HTTPException
import uvicorn

from api.db.models import ProjectStat
from api.db.session import SessionHandler
from api.domain.project_repo import ProjectStatRepo
from api.domain.wizard import Wizard
from conf.config import CFG
from gh_api.gh import GHApiClient, ProjectNameBuilder
from omegaconf import DictConfig
from api.validation.models import ProjectStatDTO


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    handler: SessionHandler = app.session_handler
    await handler.init_models()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(lifespan=lifespan)
wizard: Wizard
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get('/stat/{owner}/{repo}')
async def get_stat(owner, repo):
    if not owner or not repo:
        raise HTTPException(status_code=404, detail="owner and repo must be specified")
    name = ProjectNameBuilder.get_name(owner, repo)
    ps: ProjectStat = await wizard.get_stat(name)
    return ProjectStatDTO.from_orm(ps)


@api_router.get("/gh")
async def gh():
    repo = await GHApiClient().get_url("http://api.github.com/repos/siglens/siglens")
    return repo


def run():
    cfg = CFG
    session_handler = SessionHandler(cfg)
    app.__setattr__("session_handler", session_handler)
    repo = ProjectStatRepo(session_handler)
    global wizard
    wizard = Wizard(repo)
    app.include_router(api_router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
