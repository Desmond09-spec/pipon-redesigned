# Un-merge beat — exactly-three-pips verification

**Category:** `qa` · **Script:** `verify_unmerge.py` · **Origin:** `/tmp/verify_unmerge.py`

Extracts frames from pips-story.mp4 around the 16.9-18.5 s un-merge beat and counts connected orange components (scipy.ndimage) to prove exactly three pips are present and no fourth centre dot appears.

## Requirements

Python 3.11, numpy, Pillow, scipy, ffmpeg; the rendered story clip.

## Run

```
python3 verify_unmerge.py [video.mp4]
```

## Outputs

/tmp/unmerge_final_pips-story/t*.png (archived here).

## Artifacts in this folder

- `pipon-fourth-dot-fix.jpg` (53,957 B)
- `pipon-merge-before.jpg` (25,847 B)
- `pipon-unmerge-after-centre.jpg` (61,529 B)
- `pipon-unmerge-after-preview.jpg` (42,106 B)
- `pipon-unmerge-before.jpg` (44,643 B)
- `pipon-unmerge-model2.jpg` (42,681 B)
- `run-log.txt` (1,833 B)
- `unmerge_frames/t16.90.png` (36,121 B)
- `unmerge_frames/t17.00.png` (53,574 B)
- `unmerge_frames/t17.10.png` (72,164 B)
- `unmerge_frames/t17.20.png` (80,087 B)
- `unmerge_frames/t17.30.png` (81,626 B)
- `unmerge_frames/t17.50.png` (79,312 B)
- `unmerge_frames/t17.70.png` (80,285 B)
- `unmerge_frames/t17.90.png` (81,878 B)
- `unmerge_frames/t18.50.png` (95,372 B)

## Notes

Written for the fourth-dot bug the user reported after the motion reel. The renderer now makes the merged dot the three coincident pips, so no separate centre dot is ever drawn.


