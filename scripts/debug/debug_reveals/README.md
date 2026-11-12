# Debug — reveal state after full scroll (pass 1)

**Category:** `debug` · **Script:** `debug_reveals.py` · **Origin:** `/tmp/debug_reveals.py`

Scrolls the whole page in 300 px steps then reports which [data-reveal] elements still lack data-in.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 debug_reveals.py   # requires a served build on :4188
```

## Outputs

Counts printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (2,090 B)

## Notes

First of three narrowing passes on the How-section reveal bug.


