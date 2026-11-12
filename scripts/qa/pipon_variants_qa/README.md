# Hero variant freeze-frame / reduced-motion QA

**Category:** `qa` · **Script:** `pipon_variants_qa.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/pipon_variants_qa.py`

Freeze-frame, interaction, reduced-motion and narrow-viewport QA for the three hero variants. Freezes each clip at t = 0 / 3 / 6 s and shoots desktop + mobile, using real Chrome so H.264 decodes.

## Requirements

playwright (Python), Chromium/Chrome, Pillow; the Vite dev server on :5174.

## Run

```
Start the dev server on :5174, then: python3 pipon_variants_qa.py
```

## Outputs

pipon/shots/frames/*.png plus reduced-motion captures.

## Artifacts in this folder

- `frames/brand-desktop-t0.png` (404,149 B)
- `frames/brand-desktop-t3.png` (427,104 B)
- `frames/brand-desktop-t6.png` (430,895 B)
- `frames/brand-mobile-t0.png` (238,523 B)
- `frames/brand-mobile-t3.png` (247,148 B)
- `frames/brand-mobile-t6.png` (248,800 B)
- `frames/mobile-frames.jpg` (265,489 B)
- `frames/original-desktop-t0.png` (1,165,221 B)
- `frames/original-desktop-t3.png` (1,202,215 B)
- `frames/original-desktop-t6.png` (1,160,486 B)
- `frames/original-mobile-t0.png` (268,486 B)
- `frames/original-mobile-t3.png` (279,198 B)
- `frames/original-mobile-t6.png` (273,266 B)
- `frames/reaim-desktop-t0.png` (1,165,221 B)
- `frames/reaim-desktop-t3.png` (1,202,215 B)
- `frames/reaim-desktop-t6.png` (1,160,486 B)
- `frames/reaim-mobile-t0.png` (292,780 B)
- `frames/reaim-mobile-t3.png` (298,754 B)
- `frames/reaim-mobile-t6.png` (293,202 B)
- `frames/reduced-brand.png` (246,100 B)
- `frames/reduced-original.png` (279,909 B)
- `frames/reduced-reaim.png` (301,577 B)

## Notes

Overwrites video.play with a resolved promise to defeat the IntersectionObserver auto-play before setting currentTime.


