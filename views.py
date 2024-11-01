from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_satspot

satspot_generic_router: APIRouter = APIRouter()


def satspot_renderer():
    return template_renderer(["satspot/templates"])


@satspot_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return satspot_renderer().TemplateResponse(
        "satspot/index.html", {"request": request, "user": user.json()}
    )

@satspot_generic_router.get(
    "/satspot/{game}", response_class=HTMLResponse
)
async def display_satspot(request: Request, game: str):
    satspot = await get_satspot(game)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Satspot game does not exist."
        )
    return satspot_renderer().TemplateResponse(
        "satspot/satspot.html",
        {
            "request": request,
        },
    )
