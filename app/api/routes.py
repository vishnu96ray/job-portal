from fastapi import APIRouter

from .v1 import route as v1_route

parent_router = APIRouter(prefix="/api")

parent_router.include_router(v1_route)
