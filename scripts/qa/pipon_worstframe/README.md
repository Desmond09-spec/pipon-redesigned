# Worst-frame readability check

**Category:** `qa` · **Script:** `pipon_worstframe.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/pipon_worstframe.py`

Freezes threads.mp4 at its busiest frames (t = 0.1 / 3 / 9 s) and shoots the voices section at desktop and mobile to prove the copy stays readable wherever the loop happens to be.

## Requirements

playwright (Python), Chromium/Chrome; the Vite dev server on :5174.

## Run

```
Start the dev server on :5174, then: python3 pipon_worstframe.py
```

## Outputs

pipon/shots/*t0* / *t3* / *t9* screenshots.

## Artifacts in this folder

_No persisted files — this script reports to stdout only._

## Notes

This is the check that justified the gradient scrim over the voices video.


