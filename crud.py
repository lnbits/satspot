from typing import List

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateSatspot, Satspot

db = Database("ext_satspot")


async def create_satspot(data: CreateSatspot, wallet, user) -> List[Satspot]:
    satspot = Satspot(**data.dict(), id=urlsafe_short_hash(), wallet=wallet, user=user)
    await db.insert("satspot.satspot", satspot)
    return await get_satspots(user)


async def update_satspot(satspot: Satspot) -> Satspot:
    await db.update("satspot.satspot", satspot)
    return satspot


async def get_satspot(satspot_id: str) -> Satspot:
    return await db.fetchone(
        "SELECT * FROM satspot.satspot WHERE id = :id",
        {"id": satspot_id},
        Satspot,
    )


async def get_satspots(user: str) -> List[Satspot]:
    return await db.fetchall(
        "SELECT * FROM satspot.satspot WHERE user = :user",
        {"user": user},
        Satspot,
    )

async def get_all_pending_satspots() -> List[Satspot]:
    return await db.fetchall(
        "SELECT * FROM satspot.satspot WHERE completed = :completed",
        {"completed": 0},
        Satspot,
    )

async def delete_satspot(satspot_id: str) -> None:
    await db.execute("DELETE FROM satspot.satspot WHERE id = :id", {"id": satspot_id})
