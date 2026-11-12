# Debug — reproduce the How accordion vanish

**Category:** `debug` · **Script:** `repro_steps.py` · **Origin:** `/tmp/repro_steps.py`

Minimal reproduction for step 02 disappearing after a click: jumps straight to #how, opens each step and logs className/data-in plus console errors.

## Requirements

playwright (Python), Chromium/Chrome; a served build on :4188.

## Run

```
python3 repro_steps.py [url]
```

## Outputs

State log printed to stdout; no files.

## Artifacts in this folder

- `run-log.txt` (1,270 B)

## Notes

Confirmed React re-renders were wiping the imperatively-added is-in class.


