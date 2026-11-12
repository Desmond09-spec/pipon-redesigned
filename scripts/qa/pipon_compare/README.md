# Three-way hero comparison sheets

**Category:** `qa` · **Script:** `pipon_compare.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/pipon_compare.py`

Builds desktop and mobile comparison sheets for the three switchable hero variants (original shelf spark, re-aimed crop, made-to-brand clip) and captures full-page shots via Playwright at ?hero=<variant>.

## Requirements

playwright (Python), Chromium/Chrome, Pillow; the Vite dev server on :5174.

## Run

```
Start the dev server on :5174, then: python3 pipon_compare.py
```

## Outputs

pipon-hero-desktop-compare.jpg, pipon-hero-mobile-compare.jpg and full-page captures in /workspace.

## Artifacts in this folder

- `pipon-before-desktop-hero.png` (415,712 B)
- `pipon-final-hero.jpg` (70,971 B)
- `pipon-hero-candidates.jpg` (237,764 B)
- `pipon-hero-desktop-compare.jpg` (131,043 B)
- `pipon-hero-mobile-compare.jpg` (203,823 B)

## Notes

The variant switcher was a temporary QA affordance; the shipped site uses a single default hero.


