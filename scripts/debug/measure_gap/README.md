# Debug — measure hero media/copy gap

**Category:** `debug` · **Script:** `measure_gap.py` · **Origin:** `/tmp/measure_gap.py`

Reads live bounding boxes and computed styles for .hero__video, .hero__media, .hero__copy and .hero__h1 to quantify the visible gap between the video and the copy at mid widths.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 measure_gap.py   # requires dev server on :5174
```

## Outputs

JSON measurements printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (5,016 B)

## Notes

One-off measurement used to derive the transform compensation.


