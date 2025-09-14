from datetime import datetime, timedelta, timezone

from fastapi import Query
from pydantic import BaseModel


class CreateSatspot(BaseModel):
    name: str
    haircut: int = 0
    closing_date: datetime = datetime.now(timezone.utc) + timedelta(days=1)
    buy_in: int = 0


class Satspot(BaseModel):
    id: str | None = None
    wallet: str
    user_id: str | None = None
    name: str
    closing_date: datetime
    buy_in: int = 0
    haircut: int = 0
    players: str = ""
    completed: bool = False
    created_at: datetime = datetime.now(timezone.utc)


class Getgame(BaseModel):
    id: str | None = None
    name: str
    closing_date: datetime
    buy_in: int = 0
    haircut: int = 0
    completed: bool = False


class JoinSatspotGame(BaseModel):
    satspot_id: str = Query(None)
    ln_address: str = Query(None)
