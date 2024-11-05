import httpx
import random
from lnbits.core.views.api import api_lnurlscan
from datetime import datetime
from .crud import (
    update_satspot,
)
from lnbits.core.services import pay_invoice
from .helpers import pay_invoice

async def get_pr(ln_address, amount):
    data = await api_lnurlscan(ln_address)
    if data.get("status") == "ERROR":
        return
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{data['callback']}?amount={amount* 1000}")
            if response.status_code != 200:
                return
            return response.json()["pr"]
    except Exception:
        return None

async def calculate_winner(satspot):
    if datetime.now().timestamp() > satspot.closing_date.timestamp() and satspot.completed == False:
        satspot_players = satspot.players.split(",")
        winner = random.choice(satspot_players)
        satspot.players = winner
        satspot.completed = True
        await update_satspot(satspot)
        # Calculate the total amount of winnings
        total_amount = satspot.buy_in * len(satspot_players)
        # Calculate the haircut amount
        haircut_amount = total_amount * (satspot.haircut / 100)
        # Calculate the winnings minus haircut
        max_sat = int(total_amount - haircut_amount)
        pr = await get_pr(winner, max_sat)
        if not pr:
            return
        await pay_invoice(
            wallet_id=satspot.wallet_id,
            payment_request=pr,
            max_sat=max_sat,
            description=f"You flipping won the satspot {satspot.name}!",
        )
        return