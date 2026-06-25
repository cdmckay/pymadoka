# pymadoka (cdmckay fork)

Fork of [`mduran80/pymadoka`](https://github.com/mduran80/pymadoka) — a Python
library to control Daikin BRC1H ("Madoka") BLE thermostats. This fork carries
patches needed to run under current Home Assistant / bleak.

**Consumer:** the [`cdmckay/daikin_madoka`](https://github.com/cdmckay/daikin_madoka)
Home Assistant integration, deployed on the `banana` host (Raspberry Pi, NixOS).
Nix pins this fork by `rev` + `hash` in
`nix:hosts/banana/pkgs/pymadoka/default.nix` — it does **not** pip-install from
PyPI. So a change here only reaches HA once it's pushed **and** that pin is
bumped and `banana` is rebuilt.

## Conventions

On every functional change:

1. **Bump the version** in `setup.py`.
2. **Add a `CHANGELOG.md` entry** at the top (newest first) describing the
   change and *why* — match the existing `## vX.Y.Z - Month Year` + `### Fixes`
   format. Don't skip this; the changelog is the record of why this fork
   diverges from upstream.
3. Keep `pythonImportsCheck` in the Nix package green — the build smoke-imports
   `pymadoka`, `pymadoka.connection`, `pymadoka.controller`.
4. **Add a `pytest` regression test** under `tests/` for any behavioral fix, and
   run the suite before pushing. Mock the BLE layer (monkeypatch
   `establish_connection`, stub `_connect`, etc.) — tests must not touch real
   hardware. The Nix build only smoke-imports modules, so it will **not** run
   these for you. No deps locally? Run them in a Nix shell (one combined
   `withPackages` env — listing the packages separately to `nix shell` does
   *not* put them on one interpreter's path):

   ```bash
   nix shell --impure --expr \
     '(builtins.getFlake "nixpkgs").legacyPackages.${builtins.currentSystem}.python3.withPackages (ps: with ps; [ bleak bleak-retry-connector click pytest ])' \
     -c python -m pytest -q
   ```

## Deploying a change to banana

```bash
# in this repo
git push origin main                       # nix fetches by rev, so push first
# in the nix repo (or /etc/nixos on banana)
#   bump rev + hash + version in hosts/banana/pkgs/pymadoka/default.nix
#   nixos-rebuild test --flake /etc/nixos#banana   # headless Pi: test before switch
#   verify against the live BRC1H, then switch
```

## Gotchas

- `connection.py` must **not** reimport `bleak.discover` — bleak removed it in
  0.18 and banana ships bleak 2.x.
- `force_device_disconnect()` shells out to `bluetoothctl`; `bluez` is on HA's
  PATH via banana's systemd unit. Keep that working or remove the shell-out.
