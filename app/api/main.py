from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, APIRouter, HTTPException, status, Response, Form, Cookie
import uvicorn

from app.api.auth import authenticate_user, create_access_token, auth_by_jwt
from app.api.db.models import ProjectStat
from app.api.db.session import SessionHandler
from app.api.domain.project_repo import ProjectStatRepo, IssueRepo
from app.api.domain.wizard import Wizard
from app.conf.config import CFG
from app.gh_api.gh import GHApiClient, ProjectNameBuilder
from app.api.validation.models import ProjectStatDTO


@asynccontextmanager
async def lifespan(app: FastAPI):
    handler: SessionHandler = app.session_handler
    await handler.init_models()
    yield


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
wizard: Wizard
api_router = APIRouter(prefix="/api")
COOKIE_NAME = "jwt"


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get('/stat/{owner}/{repo}')
async def get_stat(owner, repo, jwt: Annotated[str | None, Cookie()] = None):
    auth_by_jwt(jwt)
    if not owner or not repo:
        raise HTTPException(status_code=404, detail="owner and repo must be specified")
    name = ProjectNameBuilder.get_name(owner, repo)
    ps: ProjectStat = await wizard.get_stat(name)
    await wizard.repo.add(ps)
    return ProjectStatDTO.from_orm(ps)


@api_router.get('/stat/{owner}/{repo}/issues')
async def get_issues(owner, repo):
    if not owner or not repo:
        raise HTTPException(status_code=404, detail="owner and repo must be specified")
    name = ProjectNameBuilder.get_name(owner, repo)
    ps: ProjectStat = await wizard.get_stat(name)
    issues = await wizard.get_latest_n_open_true_issue(ps, n=5)
    return issues


@api_router.get('/stat/{owner}/{repo}/issues/{issue_num}')
async def get_issue(owner, repo, issue_num):
    if not owner or not repo:
        raise HTTPException(status_code=404, detail="owner and repo must be specified")
    name = ProjectNameBuilder.get_name(owner, repo)
    ps: ProjectStat = await wizard.get_stat(name)
    res = await wizard.get_issue(ps, issue_num)
    return res


@api_router.get("/gh")
async def gh():
    repo = await GHApiClient().get_url("https://api.github.com/repos/siglens/siglens")
    return repo


@api_router.post("/auth")
async def auth(password: Annotated[str, Form()], response: Response):
    authenticated = authenticate_user(password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CFG.jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "main_user"}, expires_delta=access_token_expires
    )
    response.set_cookie(key=COOKIE_NAME, value=access_token)
    return "OK"


cfg = CFG
session_handler = SessionHandler(cfg)
app.__setattr__("session_handler", session_handler)
repo = ProjectStatRepo(session_handler)
issue_repo = IssueRepo(session_handler)
# global wizard
wizard = Wizard(repo, issue_repo)
app.include_router(api_router)


def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)
