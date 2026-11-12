# Full-page review capture (generic tool)

**Category:** `qa` · **Script:** `capture_full.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/capture_full.py`

Generic full-page screenshot helper: forces scroll reveals and lazy images, then shoots desktop (1440x900) and mobile (390x844) at full height. Complements the installed skill's shoot.py, which only captures the first viewport.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
python3 capture_full.py <url> [output-dir]
```

## Outputs

<output-dir>/desktop-full.png, desktop-viewport.png, mobile-full.png, mobile-viewport.png and a report.

## Artifacts in this folder

_No persisted files — this script reports to stdout only._

## Notes

General-purpose tool, first written during the Luxuria phase and reused during Pipon. Its Luxuria-phase output is deliberately NOT archived (see the master README exclusion list).

> **Luxuria exclusion.** This script dates from the Luxuria by Tiannah phase. Per the brief, **no Luxuria by Tiannah artifacts are included anywhere in this tree** — only the script and its documentation. See the master README for the full exclusion list.
