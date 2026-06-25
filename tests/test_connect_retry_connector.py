"""Regression test: ``Connection._connect`` must use bleak-retry-connector.

The old raw ``BleakClient.connect()`` path wedged Home Assistant's BLE link
(``org.bluez InProgress`` / ``br-connection-canceled`` at ~1 failed connect/sec)
because it never reserved a connection slot via HA's central manager. ``_connect``
now goes through :func:`bleak_retry_connector.establish_connection`.

This test pins that wiring without touching real hardware: given a discovered
``BLEDevice``, ``_connect`` must call ``establish_connection`` (passing the
device and the disconnect callback), store the returned client, mark the
connection CONNECTED, and start notifications on the notify characteristic.
"""

import asyncio

import pymadoka.connection as connection
from pymadoka.connection import Connection, ConnectionStatus


def test_connect_uses_establish_connection(monkeypatch):
    conn = Connection("00:11:22:33:44:55", adapter="hci0", reconnect=True)
    # Pretend _select_device already found the device in the scan cache.
    conn.ble_device = object()

    class _FakeClient:
        is_connected = True

        def __init__(self):
            self.started = []

        async def start_notify(self, uuid, handler):
            self.started.append(uuid)

    fake_client = _FakeClient()
    calls = {}

    async def _fake_establish(
        client_class, device, name, disconnected_callback=None, **kwargs
    ):
        calls["device"] = device
        calls["disconnected_callback"] = disconnected_callback
        return fake_client

    # If _connect ever regresses to a raw BleakClient.connect(), it won't go
    # through establish_connection and this monkeypatch won't be exercised.
    monkeypatch.setattr(connection, "establish_connection", _fake_establish)

    asyncio.run(conn._connect())

    assert calls["device"] is conn.ble_device
    assert calls["disconnected_callback"] == conn.on_disconnect
    assert conn.client is fake_client
    assert conn.connection_status == ConnectionStatus.CONNECTED
    assert fake_client.started == [connection.NOTIFY_CHAR_UUID]
