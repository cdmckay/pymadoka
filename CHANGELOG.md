# Changelog

## v0.2.16 - June 2026

### Fixes

- **Connect via `bleak-retry-connector` to stop the BLE connection wedge.**
  `Connection._connect()` previously called a raw `BleakClient.connect()`. Under
  Home Assistant this did not reserve a connection slot via HA's central manager,
  so attempts collided (`org.bluez InProgress` + `br-connection-canceled`) and the
  link wedged at ~1 failed connect/sec — the `daikin_madoka` climate platform
  could no longer poll and HA showed stale state. `_connect()` now uses
  `bleak_retry_connector.establish_connection()`, which serializes/retries
  connection setup and cooperates with HA's slot manager (and still works
  standalone against vanilla bleak). `_select_device()` now caches the
  `BLEDevice` (the connector builds the client) and the `start()` loop gates on
  it. Adds a `bleak-retry-connector` runtime dependency. Regression test in
  `tests/test_connect_retry_connector.py`; `tests/test_connection_cancel.py`
  updated for the new loop gate.

---

## v0.2.15 - June 2026

### Fixes

- **`Connection.start()` is now cancellable.** The reconnect loop previously
  caught `asyncio.CancelledError` and kept looping (it only logged it), so
  callers using `asyncio.wait_for()` could not stop it. When the device was
  visible in a BLE scan but not actually connectable, the loop span forever —
  which hung Home Assistant's startup (via the `daikin_madoka` integration's
  `async_setup_entry`). The handler now resets the status and re-raises, so
  cancellation/timeout works as expected. Regression test in
  `tests/test_connection_cancel.py`.

---

## v0.2.14

- Drop dead `bleak.discover` import; prune unused setup deps.
- Fix two silent bugs: missing return in `ResetCleanFilterTimer` and a wrong
  logging level.
