from datetime import datetime, timezone, timedelta
from typing import Optional

from pydantic import BaseModel

class CreateSatspot(BaseModel):
    name: str
    haircut: int = 0 # This is a percentage
    closing_date: datetime = datetime.now(timezone.utc) + timedelta(days=1)
    buy_in: int = 0


class Satspot(BaseModel):
    id: Optional[str] = None
    wallet: Optional[str] = None
    name: str
    closing_date: datetime = datetime.now(timezone.utc) + timedelta(days=1)
    buy_in: int = 0
    haircut: int = 0 # This is a percentage
    players: str = ""
    completed: bool = False
    created_at: datetime = datetime.now(timezone.utc)
