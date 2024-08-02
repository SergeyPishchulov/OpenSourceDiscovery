import json
from contextlib import asynccontextmanager

from peewee import InternalError
from fastapi import FastAPI, APIRouter
import uvicorn

from api.db.models import ProjectStat
from api.db.session import SessionHandler
from api.domain.project_repo import ProjectRepo
from gh_api.gh import GHClient
from omegaconf import DictConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    handler: SessionHandler = app.session_handler
    await handler.init_models()
    yield
    # Clean up the ML models and release the resources


app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get("/gh")
async def gh():
    repo = await GHClient().get_repo("http://api.github.com/repos/siglens/siglens")
    return json.loads(repo)
    return {"message": "Hello World"}


def run(cfg: DictConfig):
    session_handler = SessionHandler(cfg)
    app.__setattr__("session_handler", session_handler)
    repo = ProjectRepo(session_handler)
    app.include_router(api_router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
