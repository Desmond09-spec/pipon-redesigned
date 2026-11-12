# Debug — diagnose the blue click overlay

**Category:** `debug` · **Script:** `diag_blue.py` · **Origin:** `/tmp/diag_blue.py`

Scores screenshots for blue-dominant pixels while a How step is tapped, to prove the cyan-blue rectangle is a browser tap highlight rather than a CSS animation or selection colour.

## Requirements

playwright (Python), Chromium/Chrome, numpy, Pillow.

## Run

```
python3 diag_blue.py   # requires a served build on :4188
```

## Outputs

Blue-pixel scores printed to stdout; the before-state evidence image is archived here.

## Artifacts in this folder

- `pipon-blue-flash-before.jpg` (44,026 B)
- `run-log.txt` (3,772 B)

## Notes

Chromium's default -webkit-tap-highlight-color is rgba(51, 181, 229, 0.4) on touch devices.


