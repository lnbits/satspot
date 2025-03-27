from fastapi import APIRouter, Depends, Request
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


@satspot_generic_router.get("/{satspot_id}", response_class=HTMLResponse)
async def display_satspot(request: Request, satspot_id: str):
    satspot = await get_satspot(satspot_id)
    if satspot.completed:
        winner = satspot.players
    else:
        winner = None
    satspot = await get_satspot(satspot_id)
    amount = satspot.buy_in - (satspot.buy_in * (satspot.haircut / 100))
    players = satspot.players.split(",")
    if players[0] == "":
        amount = 0
    else:
        amount = amount * len(satspot.players.split(","))
    return satspot_renderer().TemplateResponse(
        "satspot/satspot.html",
        {
            "satspot_id": satspot_id,
            "winner": winner,
            "request": request,
            "pot": amount,
        },
    )
