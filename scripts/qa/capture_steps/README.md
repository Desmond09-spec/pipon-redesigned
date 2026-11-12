# How accordion screenshot capture

**Category:** `qa` · **Script:** `capture_steps.py` · **Origin:** `/tmp/capture_steps.py`

Scrolls #how into view and captures each opened step at desktop and mobile for the visual before/after sheet.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 capture_steps.py   # requires a served build on :4188
```

## Outputs

/tmp/steps_shots/*.png (archived here).

## Artifacts in this folder

- `run-log.txt` (809 B)
- `steps_shots/desktop_step1.png` (369,668 B)
- `steps_shots/desktop_step2.png` (368,836 B)
- `steps_shots/desktop_step3.png` (368,313 B)
- `steps_shots/mobile_step2.png` (221,686 B)

## Notes

Before-fix captures show step 02 completely vanished; the fixed set is in qa_steps/artifacts/.


