# Mid-width transform QA for the story hero

**Category:** `qa` · **Script:** `qa_transform.py` · **Origin:** `/tmp/qa_transform.py`

Measures the baked-in product window (source x 139..799 at 1600x904) against the live hero copy box at 1024/1200/1440 px and on the production build, testing the translateX/scale compensation.

## Requirements

playwright (Python), Chromium/Chrome, Pillow.

## Run

```
Start dev (:5174) and preview (:4173), then: python3 qa_transform.py
```

## Outputs

/tmp/transform_qa/*.png plus desktop_band_sheet.jpg (archived here).

## Artifacts in this folder

- `pipon-desktop-centering-before-after.jpg` (70,213 B)
- `pipon-story-midwidth-fix.jpg` (190,172 B)
- `run-log.txt` (1,650 B)
- `transform_qa/desktop_band_sheet.jpg` (153,720 B)
- `transform_qa/dist_1024.png` (330,325 B)
- `transform_qa/dist_1200.png` (342,426 B)
- `transform_qa/dist_1200_reduce.png` (375,351 B)
- `transform_qa/dist_1440.png` (367,657 B)
- `transform_qa/dist_390.png` (245,531 B)
- `transform_qa/mobile_390.png` (258,054 B)
- `transform_qa/reduce_1024.png` (336,839 B)
- `transform_qa/reduce_1200.png` (375,351 B)
- `transform_qa/reduce_mobile_sheet.jpg` (76,111 B)
- `transform_qa/report.json` (6,203 B)
- `transform_qa/story_1024.png` (344,551 B)
- `transform_qa/story_1100.png` (365,707 B)
- `transform_qa/story_1200.png` (395,076 B)
- `transform_qa/story_1280.png` (416,167 B)
- `transform_qa/story_1439.png` (428,703 B)
- `transform_qa/story_1440.png` (434,237 B)
- `transform_qa/story_1600.png` (431,862 B)
- `transform_qa/story_1920.png` (494,549 B)

## Notes

Produced the responsive --story-tx / --story-s breakpoints now in styles.css.


