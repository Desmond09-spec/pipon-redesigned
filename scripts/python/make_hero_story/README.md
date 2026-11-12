# Hero story loop renderer

**Category:** `python` · **Script:** `make_hero_story.py` · **Origin:** `/workspace/motion/make_hero_story.py`

Procedurally renders the 19 s / 30 fps / 570-frame seamless hero film that explains what Pipon is. Three pips rotate clockwise, converge into one dot, the dot expands into a product viewport (compose -> post -> scroll -> like -> comment), the window dissolves into pipon-motion-reel.mp4, then the reel's final three dots merge, un-merge and rotate back to a frame identical to frame 0. Everything is drawn at 2x with Pillow/FreeType and encoded as H.264 with ffmpeg/libopenh264; no stock footage and no keystroke-typing (text wipe-reveals, cursor only glides and clicks).

## Requirements

Python 3.11, numpy, Pillow, ffmpeg with libopenh264; brand fonts in ../../assets/fonts; pipon-motion-reel.mp4 (produced by make_motion) as the mid-film insert.

## Run

```
python3 make_hero_story.py all        # also: desktop | portrait
```

## Outputs

pipon/public/pips-story.mp4 (1600x904), pips-story-portrait.mp4 (720x1280) and their two posters.

## Artifacts in this folder

- `pips-story-portrait-poster.jpg` (41,025 B)
- `pips-story-portrait.mp4` (1,372,783 B)
- `pips-story-poster.jpg` (56,634 B)
- `pips-story.mp4` (1,651,291 B)

## Notes

Frame 0 == frame N by construction: the loop seam sits inside the rotating-three-pips beat. Rev 2 removed a spurious fourth dot at the un-merge by making the merged dot the three coincident pips. Paths are absolute (/workspace/...), so adjust the ROOT/MOTION/PUBLIC constants if you relocate the tree.


