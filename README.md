# home-voice-devices

Firmware and setup for the custom voice devices that replace the Echos (roadmap **E0.7**), plus the ESP32 Bluetooth proxies (**S0.2.4**). Every device is a thin Assist satellite on the IoT network: it detects the wake word, streams audio to Home Assistant on the hub Mac, plays the reply and shows status. It makes no decisions.

## Two setups

The devices are the same hardware and firmware in both setups. Only what they talk to changes:

| | **Mac mini only** | **Mac mini + Mac Studio** |
|---|---|---|
| Dot-style, Show-mini | Assist satellites to HA on the hub Mac | Same. HA uses the Studio's Whisper and Piper, so answers come back faster |
| Show-style (Pi) | Wyoming satellite to HA on the hub Mac (`pi-show/`) | Devices v2: a LiveKit client to the Studio's voice server, with cards pushed by the agent service (`docs/devices-v2.md`) |
| If the Studio is off | Not applicable | Every device falls back to Assist on the hub Mac within 2 s |
| Install | Flash or run `pi-show/install.sh` with `HA_HOST_IP` = the HA VM | Same first, then the v2 steps in `docs/devices-v2.md` |

| Device | Replaces | Path | State |
|---|---|---|---|
| Dot-style: ESP32-S3 + XVF3800 + I2S amp + 32×8 LED matrix | Echo Dot with Clock | `esphome/dot-clock.yaml` | Config validates on ESPHome 2026.9; needs a first flash on real hardware |
| Show-mini: Waveshare ESP32-P4 3.4" round | Echo Spot | `docs/show-mini.md` | Waiting for the board |
| Show-style: Raspberry Pi 5 + Touch Display 2 + XVF3800 | Echo Show | `pi-show/` | Install script ready |
| Bluetooth proxy: any ESP32 | (new) | `esphome/bluetooth-proxy.yaml` | Config validates |

## Dot-style features

Clock with blinking colon, listening/thinking/replying animations, native Assist timers with a countdown and chime, wake word on the device (`okay_nabu` until the custom one is trained, see `docs/wake-word.md`), "stop" wake word for timers, action button (tap to talk, hold to mute), brightness control from HA, announcements with music ducking.

## Flashing

```bash
pip install esphome
cp esphome/secrets.example.yaml esphome/secrets.yaml   # fill from the vault; git-ignored
esphome run esphome/dot-clock.yaml                     # first time over USB, later over the IoT network
```

For each room, copy `dot-clock.yaml` to `dot-<room>.yaml` and change `name`, `friendly_name` and `api_key` in the substitutions; add a matching `api_key_dot_<room>` to `secrets.yaml`. Each device gets its own API key.

## Security

No fallback hotspot, no web server, encrypted API per device, OTA password. The Pi drops all inbound traffic except Home Assistant's address on the satellite port, and SSH is off.

## Checks

CI validates every ESPHome config, shellchecks the Pi scripts and runs the unit tests. Run `pre-commit install` after cloning.

The unit tests in `tests/` check rules every device must follow: its own API key, an encrypted API, an OTA password, no hotspot and no web server. They also render the Pi's firewall and services into a temp dir and check that only Home Assistant's address can reach the satellite port. Run them with `pip install -r requirements-test.txt && pytest`.
