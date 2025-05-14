import random
from datetime import datetime

import httpx
from lnbits.core.services import pay_invoice
from lnbits.core.views.api import api_lnurlscan

from .crud import (
    update_satspot,
)


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
    if (
        datetime.now().timestamp() > satspot.closing_date.timestamp()
        and not satspot.completed
    ):
        satspot_players = satspot.players.split(",")
        if satspot_players[0] == "":
            satspot.completed = True
            satspot.players = "No players"
            await update_satspot(satspot)
            return
        winner = random.choice(satspot_players)
        # Calculate the total amount of winnings
        total_amount = satspot.buy_in * len(satspot_players)
        # Calculate the haircut amount
        haircut_amount = total_amount * (satspot.haircut / 100)
        # Calculate the winnings minus haircut
        max_sat = int(total_amount - haircut_amount)
        pr = await get_pr(winner, max_sat)
        if not pr:
            satspot.completed = False
            await update_satspot(satspot)
            return
        try:
            await pay_invoice(
                wallet_id=satspot.wallet,
                payment_request=pr,
                max_sat=max_sat,
                description=f"({winner}) won the satspot {satspot.name}!",
            )
            satspot.players = winner
            satspot.completed = True
            await update_satspot(satspot)
            # Pay the tribute to LNbits Inc, because you're nice and like LNbits.
            await pay_tribute(int(haircut_amount), satspot.wallet)
        except Exception:
            satspot.completed = False
            await update_satspot(satspot)
        return
    return


async def pay_tribute(haircut_amount: int, wallet_id: str) -> None:
    try:
        tribute = int(2 * (haircut_amount / 100))
        pr = await get_pr("lnbits@nostr.com", tribute)
        if not pr:
            return
        await pay_invoice(
            wallet_id=wallet_id,
            payment_request=pr,
            max_sat=tribute,
            description="Tribute to help support LNbits",
        )
    except Exception:
        pass
    return
