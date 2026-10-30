# Devices v2 (Phase 2, S2.4.2) and Phase 3 hardware (E3.1)

## v2: stream to the voice server on the Studio

**Mac mini + Mac Studio only.** With the Mac mini only, the devices stay on v1 (Assist satellites to HA on the hub Mac) and nothing in this section applies.

- Show-style (Pi): replace the Wyoming satellite with a LiveKit client that streams the mic and plays replies, and a WebSocket from the agent service that pushes screen cards (timer, doorbell, next meeting, now playing). The kiosk shows a card on its own when one arrives.
- Show-mini: same cards over WebSocket, rendered as LVGL pages.
- Dot-style stays an Assist satellite; Assist on the hub Mac can use the Studio's Whisper and Piper.
- Fallback: when the Studio doesn't answer within 2 s, devices fall back to Assist on the hub Mac.

## Phase 3

The hardware below works in both setups.

- Final enclosures and better speaker drivers to close the gap with Echo sound.
- More rooms, outdoor and bathroom devices.
- mmWave presence sensors (for example an LD2410 on an ESP32) so answers follow you room by room; they feed `sensor.owner_room`, which the reminders already use.
