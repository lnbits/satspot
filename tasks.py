import asyncio
from datetime import datetime
from lnbits.core.models import Payment
from lnbits.core.services import pay_invoice
from lnbits.tasks import register_invoice_listener

from .crud import (
    get_satspot,
    update_satspot,
)
from .helpers import get_pr, calculate_winner


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_satspot")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") == "satspot":
        ln_address = payment.extra["ln_address"]
        satspot_id = payment.extra["satspot_id"]
        # fetch details
        satspot = await get_satspot(satspot_id)
        if not satspot:
            return
        # Check they are not trying to scam the system.
        if (payment.amount / 1000) != satspot.buy_in:
            return
        await calculate_winner(satspot)
        # If player joins late send a refund
        if int(datetime.now().timestamp()) > satspot.closing_date:
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
            await calculate_winner(satspot)
            return

        # Add the player to the game.
        if satspot.players == "":
            satspot.players = ln_address
        else:
            satspot.players = f"{satspot.players},{ln_address}"
        await update_satspot(satspot)
