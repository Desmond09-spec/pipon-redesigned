# Debug — reveal state after jumping straight to #how (pass 3)

**Category:** `debug` · **Script:** `debug_reveals3.py` · **Origin:** `/tmp/debug_reveals3.py`

Reproduces the QA order (jump straight to #how first) and reports data-in counts before and after clicks.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 debug_reveals3.py   # requires a served build on :4188
```

## Outputs

Counts printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (526 B)

## Notes

Isolated the failure to the click re-render, not the scroll observer.


