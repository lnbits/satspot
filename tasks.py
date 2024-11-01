import asyncio
import random

from lnbits.core.models import Payment
from lnbits.core.services import pay_invoice, websocket_updater
from lnbits.tasks import register_invoice_listener

from .crud import (
    get_satspot,
    update_satspot,
)
from .helpers import get_pr


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_satspot")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") == "satspot":
        ln_address = payment.extra["ln_address"]
        game_id = payment.extra["game_id"]
        # fetch details
        satspot = await get_satspot(game_id)
        if not satspot:
            return
        # Check they are not trying to scam the system.
        if (payment.amount / 1000) != satspot.buy_in:
            return
        # If the game is full set as completed and refund the player.
        satspot_players = satspot.players.split(",")
        if len(satspot_players) + 1 > satspot.number_of_players:
            satspot.completed = True
            await update_satspot(satspot)

            # Calculate the haircut amount
            haircut_amount = satspot.buy_in * (satspot.haircut / 100)
            # Calculate the refund amount
            max_sat = int(satspot.buy_in - haircut_amount)
            pr = await get_pr(ln_address, max_sat)
            if not pr:
                return
            await pay_invoice(
                wallet_id=satspot.wallet,
                payment_request=pr,
                max_sat=max_sat,
                description="Refund. Satspot game was full.",
            )
            await websocket_updater(payment.payment_hash, "refund")
            return

        # Add the player to the game.
        if satspot.players == "":
            satspot.players = ln_address
        else:
            satspot.players = f"{satspot.players},{ln_address}"
        await update_satspot(satspot)

        # If last to join flip, calculate winner and pay them.
        satspot_players = satspot.players.split(",")
        if satspot.closing_date > db.timestamp_now:
            satspot.completed = True
            winner = random.choice(satspot_players)
            satspot.players = winner
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
            if winner == ln_address:
                await websocket_updater(payment.payment_hash, f"won,{winner}")
                await pay_invoice(
                    wallet_id=satspot.wallet_id,
                    payment_request=pr,
                    max_sat=max_sat,
                    description="You flipping won the satspot!",
                )
            if winner != ln_address:
                await websocket_updater(payment.payment_hash, f"lost,{winner}")
            return

        await websocket_updater(payment.payment_hash, "paid")
