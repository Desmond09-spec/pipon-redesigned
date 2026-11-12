# Debug — live crop sweep at six widths

**Category:** `debug` · **Script:** `live_crops.py` · **Origin:** `/tmp/live_crops.py`

Shoots the live hero at 1024 / 1100 / 1200 / 1280 / 1440 / 1600 px so the baked-in product window can be compared against the responsive layout.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 live_crops.py   # requires dev server on :5174
```

## Outputs

/tmp/live_crops/*.png (archived here).

## Artifacts in this folder

- `live_crops/live_1024.png` (375,625 B)
- `live_crops/live_1100.png` (386,594 B)
- `live_crops/live_1200.png` (405,925 B)
- `live_crops/live_1280.png` (418,899 B)
- `live_crops/live_1440.png` (432,230 B)
- `live_crops/live_1600.png` (431,850 B)
- `run-log.txt` (852 B)

## Notes

Input to the mid-width crop fix.


