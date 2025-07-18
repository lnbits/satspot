import random
from datetime import datetime

from lnbits.core.services import pay_invoice
from lnbits.settings import settings
from lnurl import LnurlPayResponse
from lnurl import execute_pay_request as lnurlp
from lnurl import handle as lnurl_handle

from .crud import (
    update_satspot,
)


async def get_pr(ln_address: str, amount_msat: int) -> str | None:
    try:
        res = await lnurl_handle(ln_address)
        if not isinstance(res, LnurlPayResponse):
            return None
        res2 = await lnurlp(
            res,
            msat=str(amount_msat),
            user_agent=settings.user_agent,
            timeout=5,
        )
        return res2.pr
    except Exception as e:
        print(f"Error handling LNURL: {e}")
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
