# Debug — reveal state after full scroll (pass 2, multi-viewport)

**Category:** `debug` · **Script:** `debug_reveals2.py` · **Origin:** `/tmp/debug_reveals2.py`

Same probe as pass 1 but across multiple viewport sizes, scrolling each reveal into view individually.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 debug_reveals2.py   # requires a served build on :4188
```

## Outputs

Counts printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (601 B)

## Notes

Ruled out a viewport-specific cause.


