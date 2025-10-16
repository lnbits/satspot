from datetime import datetime, timezone

from fastapi import Query
from pydantic import BaseModel, validator


class CreateSatspot(BaseModel):
    name: str
    haircut: int = 0
    closing_date: datetime
    buy_in: int = 0

    @validator("closing_date", pre=True, always=True)
    def force_utc(cls, v):  # noqa: N805
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return datetime.fromtimestamp(int(v), tz=timezone.utc)


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

    @validator("closing_date", pre=True, always=True)
    def force_utc(cls, v):  # noqa: N805
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return datetime.fromtimestamp(int(v), tz=timezone.utc)


class Getgame(BaseModel):
    id: str | None = None
    name: str
    closing_date: datetime
    buy_in: int = 0
    haircut: int = 0
    completed: bool = False

    @validator("closing_date", pre=True, always=True)
    def force_utc(cls, v):  # noqa: N805
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return datetime.fromtimestamp(int(v), tz=timezone.utc)


class JoinSatspotGame(BaseModel):
    satspot_id: str = Query(None)
    ln_address: str = Query(None)
