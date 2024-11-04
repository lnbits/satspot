from typing import Optional

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash
from loguru import logger

from .models import Satspot, CreateSatspot

db = Database("ext_satspot")

async def create_satspot(data: CreateSatspot) -> Satspot:
    satspot = Satspot(**data.dict(), id=urlsafe_short_hash())
    await db.insert("satspot.satspot", satspot)
    return satspot

async def update_satspot(satspot: Satspot) -> Satspot:
    await db.update("satspot.satspot", satspot)
    return satspot

async def get_satspot(satspot_id: str) -> Optional[Satspot]:
    return await db.fetchone(
        "SELECT * FROM satspot.satspot WHERE id = :id",
        {"id": satspot_id},
        Satspot,
    )

async def get_satspots(user: str) -> Optional[Satspot]:
    return await db.fetchone(
        "SELECT * FROM satspot.satspot WHERE user = :user",
        {"user": user},
        Satspot,
    )
