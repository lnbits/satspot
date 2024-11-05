import asyncio

from fastapi import APIRouter

from .crud import db
from .views import satspot_generic_router
from .views_api import satspot_api_router

satspot_ext: APIRouter = APIRouter(prefix="/satspot", tags=["satspot"])
satspot_ext.include_router(satspot_generic_router)
satspot_ext.include_router(satspot_api_router)

satspot_static_files = [
    {
        "path": "/satspot/static",
        "name": "satspot_static",
    }
]

__all__ = ["db", "satspot_ext", "satspot_static_files"]
