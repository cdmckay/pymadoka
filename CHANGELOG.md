# Changelog

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
