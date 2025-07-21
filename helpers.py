import random
from datetime import datetime

from lnbits.core.services import get_pr_from_lnurl, pay_invoice
from lnurl import LnurlPayResponse
from lnurl import handle as lnurl_handle

from .crud import (
    update_satspot,
)


async def check_lnaddress(address: str) -> bool:
    try:
        res = lnurl_handle(address)
    except Exception:
        return False
    if not isinstance(res, LnurlPayResponse):
        return False
    return True


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
        try:
            pr = await get_pr_from_lnurl(winner, max_sat)
        except Exception:
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
        try:
            pr = await get_pr_from_lnurl("lnbits@nostr.com", tribute)
        except Exception:
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
