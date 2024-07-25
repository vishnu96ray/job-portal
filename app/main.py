import copy
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationError

from app.api.error import HTTPException, http_exception_error, UserAuthenticationError, auth_user_error
from app.api.middleware.auth import BasicAuthBackend


from .api.routes import parent_router
from .conf.config import REDIS_URL
from .conf.logs import setup_logging
from .db import init_db, stop_db

# from app.api.middleware.auth import BasicAuthBackend

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_connection = redis.from_url(REDIS_URL)
    await init_db()
    yield
    await stop_db()


app = FastAPI(
    debug=False,
    title="Job Portal",
    version="0.1.0",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/")
def test(request: Request):
    print(request.user.is_authenticated)
    return JSONResponse(status_code=status.HTTP_200_OK, content="pong:)")


def add_router():
    app.include_router(parent_router)


def mount():
    _path = Path("static")
    if not _path.exists():
        _path.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")


def add_except_handler():
    app.add_exception_handler(HTTPException, http_exception_error)
    app.add_exception_handler(UserAuthenticationError,
                                     handler=auth_user_error)


add_router()
mount()
add_except_handler()  # lifespan=lifespan,

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=auth_user_error)
