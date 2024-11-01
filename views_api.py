from http import HTTPStatus

from fastapi import APIRouter, Depends
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import create_invoice
from lnbits.decorators import require_admin_key
from starlette.exceptions import HTTPException

from .crud import (
    create_satspot,
    get_satspot
)
from .helpers import get_pr
from .models import (
    CreateSatspot,
    JoinSatspotGame,
)

satspot_api_router = APIRouter()

@satspot_api_router.post("/api/v1/satspot", status_code=HTTPStatus.OK)
async def api_create_satspot(
    data: CreateSatspot, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    if data.haircut < 0 or data.haircut > 50:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Haircut must be between 0 and 50"
        )
    satspot.wallet = key_info.id
    satspot = await create_satspot(data)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to create satspot"
        )
    return satspot.id


@satspot_api_router.post("/api/v1/satspot/join/", status_code=HTTPStatus.OK)
async def api_join_satspot(data: JoinSatspotGame):
    satspot_game = await get_satspot(data.game_id)
    if not satspot_game:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No game found")
    if satspot_game.completed:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="This game is already full"
        )
    pay_req = await get_pr(data.ln_address, satspot_game.buy_in)
    if not pay_req:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="lnaddress check failed"
        )
    payment = await create_invoice(
        wallet_id=satspot_game.wallet,
        amount=satspot_game.buy_in,
        memo=f"Satspot {satspot_game.name} for {data.ln_address}",
        extra={
            "tag": "satspot_satspot",
            "ln_address": data.ln_address,
            "game_id": data.game_id,
        },
    )
    return {"payment_hash": payment.payment_hash, "payment_request": payment.bolt11}


@satspot_api_router.get(
    "/api/v1/satspot/satspot/{satspot_id}", status_code=HTTPStatus.OK
)
async def api_get_satspot(satspot_id: str):
    satspot = await get_satspot(satspot_id)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Satspot game does not exist."
        )
    if satspot.closing_date < db.timestamp_now:
        satspot.completed = True
    return satspot
