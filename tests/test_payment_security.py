from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from lnbits.core.models import Payment, PaymentState

from .. import tasks


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def paid_entry(monkeypatch):
    game = SimpleNamespace(wallet="game-wallet", buy_in=100, players="")
    payment = Payment(
        checking_id="checking-id",
        payment_hash="payment-hash",
        wallet_id=game.wallet,
        amount=100_000,
        fee=0,
        bolt11="invoice",
        status=PaymentState.SUCCESS,
        extra={
            "tag": "satspot",
            "satspot_id": "game-id",
            "ln_address": "alice@pay.example",
        },
    )
    update = AsyncMock()
    payout = AsyncMock()
    monkeypatch.setattr(tasks, "get_satspot", AsyncMock(return_value=game))
    monkeypatch.setattr(tasks, "update_satspot", update)
    monkeypatch.setattr(tasks, "calculate_winner", payout)
    return game, payment, update, payout


@pytest.mark.anyio
async def test_payment_to_another_wallet_cannot_join_game(paid_entry):
    game, payment, update, payout = paid_entry
    payment.wallet_id = "attacker-wallet"

    await tasks.on_invoice_paid(payment)

    assert game.players == ""
    update.assert_not_awaited()
    payout.assert_not_awaited()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "address",
    [
        ",".join(["alice@pay.example"] * 2000),
        "alice@pay.example,",
        ",alice@pay.example",
        "",
        " ",
        None,
        ["alice@pay.example"],
    ],
    ids=[
        "many-players",
        "trailing-comma",
        "leading-comma",
        "empty",
        "blank",
        "null",
        "list",
    ],
)
async def test_invalid_player_address_cannot_join_game(paid_entry, address):
    game, payment, update, payout = paid_entry
    payment.extra["ln_address"] = address

    await tasks.on_invoice_paid(payment)

    assert game.players == ""
    update.assert_not_awaited()
    payout.assert_not_awaited()


@pytest.mark.anyio
@pytest.mark.parametrize("players", ["", "bob@pay.example"])
async def test_valid_payment_adds_one_player(paid_entry, players):
    game, payment, update, payout = paid_entry
    game.players = players

    await tasks.on_invoice_paid(payment)

    expected = ([players] if players else []) + [payment.extra["ln_address"]]
    assert game.players.split(",") == expected
    update.assert_awaited_once_with(game)
    payout.assert_awaited_once_with(game)


@pytest.mark.anyio
async def test_wrong_buy_in_cannot_join_game(paid_entry):
    game, payment, update, payout = paid_entry
    payment.amount = 1_000

    await tasks.on_invoice_paid(payment)

    assert game.players == ""
    update.assert_not_awaited()
    payout.assert_not_awaited()
