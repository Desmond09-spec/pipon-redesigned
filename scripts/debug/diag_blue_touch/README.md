# Debug — held-touch tap-highlight probe

**Category:** `debug` · **Script:** `diag_blue_touch.py` · **Origin:** `/tmp/diag_blue_touch.py`

Holds a touch down on a How step and samples the rendered pixels, then reads the computed -webkit-tap-highlight-color to confirm the UA default.

## Requirements

playwright (Python), Chromium/Chrome, numpy, Pillow.

## Run

```
python3 diag_blue_touch.py   # requires a served build on :4188
```

## Outputs

Scores and computed styles printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (480 B)

## Notes

Headless Chromium does not paint the tap highlight into screenshots, so the computed style was the decisive evidence.


