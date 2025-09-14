from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.core.services import create_invoice
from lnbits.decorators import require_admin_key
from lnurl import LnurlPayResponse
from lnurl import handle as lnurl_handle
from loguru import logger
from starlette.exceptions import HTTPException

from .crud import (
    create_satspot,
    delete_satspot,
    get_satspot,
    get_satspots,
)
from .models import CreateSatspot, Getgame, JoinSatspotGame

satspot_api_router = APIRouter()


@satspot_api_router.post("/api/v1/satspot", status_code=HTTPStatus.OK)
async def api_create_satspot(
    data: CreateSatspot, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    if data.haircut < 0 or data.haircut > 50:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Haircut must be between 0 and 50",
        )
    satspot = await create_satspot(data, key_info.wallet.id, key_info.wallet.user)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to create satspot"
        )
    return satspot


@satspot_api_router.get("/api/v1/satspot")
async def api_get_satspots(
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    user = await get_user(key_info.wallet.user)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get user"
        )
    satspots = await get_satspots(user.id)
    return satspots


@satspot_api_router.post("/api/v1/satspot/join/", status_code=HTTPStatus.OK)
async def api_join_satspot(data: JoinSatspotGame):
    satspot_game = await get_satspot(data.satspot_id)
    logger.debug(satspot_game)
    if not satspot_game:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No game found")
    if satspot_game.completed:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Game already ended"
        )
    try:
        res = await lnurl_handle(data.ln_address)
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=f"lnaddress error: {exc!s}"
        ) from exc
    if not isinstance(res, LnurlPayResponse):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="lnaddress return wrong response type",
        )
    payment = await create_invoice(
        wallet_id=satspot_game.wallet,
        amount=satspot_game.buy_in,
        memo=f"Satspot {satspot_game.name} for {data.ln_address}",
        extra={
            "tag": "satspot",
            "ln_address": data.ln_address,
            "satspot_id": data.satspot_id,
        },
    )
    return {"payment_hash": payment.payment_hash, "payment_request": payment.bolt11}


@satspot_api_router.delete("/api/v1/satspot/{satspot_id}")
async def api_satspot_delete(
    satspot_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    satspot = await get_satspot(satspot_id)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Satspot does not exist."
        )

    if satspot.wallet != key_info.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your satspot."
        )

    await delete_satspot(satspot_id)


@satspot_api_router.get(
    "/api/v1/satspot/satspot/{satspot_id}", status_code=HTTPStatus.OK
)
async def api_get_satspot(satspot_id: str):
    satspot = await get_satspot(satspot_id)
    if not satspot:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Satspot game does not exist."
        )
    if satspot.closing_date.timestamp() < datetime.now().timestamp():
        satspot.completed = True
    return Getgame(
        id=satspot.id,
        name=satspot.name,
        closing_date=satspot.closing_date,
        buy_in=satspot.buy_in,
        haircut=satspot.haircut,
        completed=satspot.completed,
    )
