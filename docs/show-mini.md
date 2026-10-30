# Show-mini (S0.7.2): status

The same in both setups: a v1 Assist satellite to HA on the hub Mac, which uses the Studio's speech services once one joins.

Board: Waveshare ESP32-P4 3.4" round (800×800 MIPI-DSI, onboard mics with echo cancellation and a 2 W speaker).

Not written yet on purpose. ESP32-P4 display and audio support in ESPHome depends on the exact panel driver, touch controller and codec on this board, and a config written without the board in hand would not boot. Next steps once the board arrives:

1. Flash Waveshare's demo to confirm the display, touch and audio work.
2. Read the panel, touch and codec chips from Waveshare's schematic; write `esphome/show-mini.yaml` with the `mipi_dsi` display, LVGL, `i2s_audio` and the same `voice_assistant` and timer handling as `dot-clock.yaml`.
3. LVGL pages: clock, weather, timers, now playing, and the assistant's answer text (from the `voice_assistant` `on_tts_start` text).
