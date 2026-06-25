"""Regression test: ``Connection.start()`` must be cancellable.

Previously the retry loop in :meth:`Connection.start` swallowed
``asyncio.CancelledError`` (it logged it and kept looping), so
``asyncio.wait_for()`` — used by the Home Assistant integration's
``async_setup_entry`` — could not stop it. When the thermostat was visible in
the BLE scan but not actually connectable, the loop span forever and hung Home
Assistant's entire startup.

This test reproduces that scenario with a no-op ``_connect`` and asserts that a
bounded ``wait_for`` can now actually cancel the loop instead of hanging.
"""

import asyncio

import pytest

from pymadoka.connection import Connection, ConnectionStatus


async def _scenario():
    conn = Connection("00:11:22:33:44:55", adapter="hci0", reconnect=True)

    # "Discoverable but never connects": a device was found (so start()'s loop
    # takes the _connect branch) and _connect is a no-op that never reaches
    # CONNECTED, so the loop would otherwise spin forever. wait_for() must be
    # able to cancel it.
    conn.ble_device = object()

    async def _never_connects():
        return

    conn._connect = _never_connects

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(conn.start(), timeout=0.5)

    # The loop must have exited on cancellation rather than reporting CONNECTED.
    assert conn.connection_status != ConnectionStatus.CONNECTED


def test_start_is_cancellable_when_never_connects():
    # If the CancelledError swallow regresses, wait_for() can't cancel the loop
    # and this call hangs (CI times out) instead of completing quickly.
    asyncio.run(_scenario())
