import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import run_by_the_minute_task, wait_for_paid_invoices
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

scheduled_tasks: list[asyncio.Task] = []


def satspot_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def satspot_start():
    task1 = create_permanent_unique_task("ext_satspot", wait_for_paid_invoices)
    task2 = create_permanent_unique_task(
        "ext_satspot_time_check", run_by_the_minute_task
    )
    scheduled_tasks.append(task1)
    scheduled_tasks.append(task2)


__all__ = ["db", "satspot_ext", "satspot_start", "satspot_static_files", "satspot_stop"]
