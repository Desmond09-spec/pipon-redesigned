# Seamless three-dot hero loop generator

**Category:** `python` · **Script:** `make_pips.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/make_pips.py`

Procedural, mathematically seamless made-to-brand hero loop: three flat orange dots in the logo's 2-up / 1-down triangle drift on warm #FBF9F4 paper. Every moving term completes an integer number of cycles over the loop, so frame N equals frame 0 exactly (asserted in the script). The background matches the page background so there is no seam and no scrim is needed. Emits a 16:9 desktop clip and a 9:16 portrait clip from one generator.

## Requirements

Python 3.11, numpy, Pillow, ffmpeg with libopenh264.

## Run

```
python3 make_pips.py
```

## Outputs

pipon/public/pips.mp4, pips-portrait.mp4, pips-poster.jpg, pips-portrait-poster.jpg.

## Artifacts in this folder

- `pips-portrait-poster.jpg` (38,008 B)
- `pips-portrait.mp4` (232,044 B)
- `pips-poster.jpg` (53,531 B)
- `pips.mp4` (259,255 B)

## Notes

The FLAT_DOTS switch in the header toggles flat discs (matching the shipped logo) versus shaded spheres. Output path is hardcoded to /workspace/pipon/public.


