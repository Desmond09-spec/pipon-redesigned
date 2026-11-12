# Motion-graphics study (reel / sting / dots loop)

**Category:** `python` · **Script:** `make_motion.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/mg/make_motion.py`

Pipon motion-graphics study 02 — three techniques built around one plate-free mark. Everything is drawn procedurally with NumPy distance fields and real brand fonts, then encoded with ffmpeg/libopenh264. Rev 02 removed the near-black squircle behind the logo: the mark is now just three flat #E8532F dots on #FBF9F4 paper, landing with contact shadows, impact ripples and a drawn hairline triangle.

## Requirements

Python 3.11, numpy, Pillow, ffmpeg with libopenh264; brand fonts in ../../assets/fonts. Writes intermediate frames under the mg/frames scratch directory.

## Run

```
python3 make_motion.py
```

## Outputs

motion/pipon-motion-reel.mp4 (1280x720, 6.0 s), pipon-logo-sting.mp4 (1080x1080, 2.6 s), pipon-dots-loop.mp4 (1280x720, 2.0 s seamless loop), pipon-logo-sting.gif preview, three posters, pipon-motion-sheet.jpg contact sheet, and the motion/index.html preview page.

## Artifacts in this folder

- `motion-preview.html` (5,763 B)
- `pipon-dots-loop-poster.jpg` (44,341 B)
- `pipon-dots-loop.mp4` (227,545 B)
- `pipon-logo-sting-poster.jpg` (63,829 B)
- `pipon-logo-sting.gif` (265,286 B)
- `pipon-logo-sting.mp4` (275,656 B)
- `pipon-motion-assets.zip` (1,905,011 B)
- `pipon-motion-reel-poster.jpg` (49,766 B)
- `pipon-motion-reel.mp4` (683,349 B)
- `pipon-motion-sheet.jpg` (65,045 B)

## Notes

pipon-motion-reel.mp4 is consumed by make_hero_story as the mid-film insert. The per-frame PNG dump is transient scratch and is not archived here.


