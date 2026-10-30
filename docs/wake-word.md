# Custom wake word (S0.6.2)

The wake word runs on each device, so this is the same in both setups. Neither Mac trains it.

1. Pick the name: two or three syllables, unusual sounds, not a common word in your conversations.
2. Train a microWakeWord model with the official training notebook (synthetic samples from Piper, about an hour on a GPU; a free Colab GPU works). The Windows PC is not used for compute.
3. Put the resulting `.json` and `.tflite` in `esphome/wake_words/` (they contain no secrets) and change the `micro_wake_word` model in `dot-clock.yaml` to `wake_words/<name>.json`.
4. Measure: at least 95% wakes at 3 m with music at normal volume, and under 1 false wake per day per device. Log wakes from HA (`assist_satellite` state changes) for a week.
