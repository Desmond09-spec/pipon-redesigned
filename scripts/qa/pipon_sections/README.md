# Section-by-section capture

**Category:** `qa` · **Script:** `pipon_sections.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/pipon_sections.py`

Captures the sections touched by the brand alignment (#pip, #community, #how, #join, footer) at desktop and mobile, forcing all scroll reveals to their visible state first.

## Requirements

playwright (Python), Chromium/Chrome; the Vite dev server on :5174.

## Run

```
Start the dev server on :5174, then: python3 pipon_sections.py
```

## Outputs

pipon/shots/sections/*.png

## Artifacts in this folder

- `sections/desktop-community.png` (1,192,707 B)
- `sections/desktop-footer.png` (97,047 B)
- `sections/desktop-how.png` (225,817 B)
- `sections/desktop-join.png` (216,407 B)
- `sections/desktop-navlogo.png` (3,155 B)
- `sections/desktop-pip.png` (425,035 B)
- `sections/mobile-community.png` (278,637 B)
- `sections/mobile-footer.png` (92,617 B)
- `sections/mobile-how.png` (202,828 B)
- `sections/mobile-join.png` (131,332 B)
- `sections/mobile-navlogo.png` (3,047 B)
- `sections/mobile-pip.png` (283,390 B)

## Notes

The FORCE snippet adds is-in to every [data-reveal] so the sheet is not half-faded.


