import json
from peewee import InternalError
from fastapi import FastAPI, APIRouter
import uvicorn

from api.db.handle import dbhandle
from api.db.models import ProjectStat
from gh_api.gh import GHClient

app = FastAPI()

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get("/gh")
async def gh():
    repo = await GHClient().get_repo("http://api.github.com/repos/siglens/siglens")
    return json.loads(repo)
    return {"message": "Hello World"}


app.include_router(api_router)
if __name__ == "__main__":
    try:
        dbhandle.connect()
        ProjectStat.create_table()
    except InternalError as px:
        print(str(px))
    uvicorn.run(app, host="0.0.0.0", port=8000)
