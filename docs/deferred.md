# Deferred work

Each entry names the trigger that starts it. Delete the entry when it is done.

## Update the LED library pin and the install script
- **What:** Move the `submodules/matrix` pin from `dfc27c1` to `b4dc553`. Rewrite `scripts/install` to run the
  README's setup steps, and make it stop at the first error (today it prints "Installation complete!" even
  after its Python build fails).
- **Why it waits:** Changing the pin changes what every fresh clone installs. Tom has not decided yet
  (raised 2026-11-14).
- **Trigger:** Tom approves the change.
