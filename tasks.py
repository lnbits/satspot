import asyncio
from datetime import datetime
import random

from lnbits.core.models import Payment
from lnbits.core.services import pay_invoice
from lnbits.tasks import register_invoice_listener

from .crud import (
    get_satspot,
    update_satspot,
    get_all_pending_satspots,
)
from .helpers import calculate_winner, get_pr
from loguru import logger

async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_satspot")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)

async def run_by_the_minute_task():
    minute_counter = 0
    while True:
        try:
            satspots = await get_all_pending_satspots()
            for satspot in satspots:
                logger.error("Found pending satspot, caluclateing winner")
                await calculate_winner(satspot)
        except Exception as ex:
            logger.error(ex)

        minute_counter += 1
        await asyncio.sleep(60 + random.randint(-3, 3)) # to avoid herd effect

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
        # Add the player to the game.
        if satspot.players == "":
            satspot.players = ln_address
        else:
            satspot.players = f"{satspot.players},{ln_address}"
        await update_satspot(satspot)
        await calculate_winner(satspot)
