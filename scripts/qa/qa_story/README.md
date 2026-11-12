# Narrative hero video — load/seek QA

**Category:** `qa` · **Script:** `qa_story.py` · **Origin:** `/tmp/qa_story.py`

Probes the story hero video on the dev server: computed object-fit/object-position, readyState, currentTime, font status and transform across several mid-width viewports, then writes per-candidate crops.

## Requirements

playwright (Python), Chromium/Chrome, Pillow; the Vite dev server on :5174.

## Run

```
Start the dev server on :5174, then: python3 qa_story.py
```

## Outputs

/tmp/story_qa/*.png and .jpg crop sheets (archived here).

## Artifacts in this folder

- `run-log.txt` (2,418 B)
- `story_qa/combo_1024.jpg` (106,595 B)
- `story_qa/combo_1024_A_36_only.png` (337,841 B)
- `story_qa/combo_1024_B_36_s92.png` (334,960 B)
- `story_qa/combo_1024_C_34_s94.png` (340,201 B)
- `story_qa/combo_1024_D_38_s90.png` (332,473 B)
- `story_qa/combo_1200.jpg` (94,358 B)
- `story_qa/combo_1200_A_36_only.png` (386,447 B)
- `story_qa/combo_1200_B_36_s92.png` (377,543 B)
- `story_qa/combo_1200_C_34_s94.png` (379,927 B)
- `story_qa/combo_1200_D_38_s90.png` (374,685 B)
- `story_qa/crop_1024_29.png` (344,379 B)
- `story_qa/crop_1024_36.png` (337,827 B)
- `story_qa/crop_1024_40.png` (335,898 B)
- `story_qa/crop_1024_46.png` (326,346 B)
- `story_qa/crop_1200_29.png` (386,350 B)
- `story_qa/crop_1200_36.png` (387,491 B)
- `story_qa/crop_1200_40.png` (384,831 B)
- `story_qa/crop_1200_46.png` (382,315 B)
- `story_qa/crop_compare_1024.jpg` (111,795 B)
- `story_qa/crop_compare_1200.jpg` (100,003 B)
- `story_qa/desktop_comment.png` (416,864 B)
- `story_qa/desktop_dots.png` (427,266 B)
- `story_qa/desktop_feed.png` (417,419 B)
- `story_qa/desktop_merge.png` (349,584 B)
- `story_qa/desktop_reel.png` (357,505 B)
- `story_qa/desktop_sheet.jpg` (155,267 B)
- `story_qa/desktop_top.png` (373,141 B)
- `story_qa/desktop_ui.png` (432,173 B)
- `story_qa/desktop_unmerge.png` (357,505 B)
- `story_qa/mobile_comment.png` (250,698 B)
- `story_qa/mobile_dots.png` (258,430 B)
- `story_qa/mobile_feed.png` (259,876 B)
- `story_qa/mobile_merge.png` (229,552 B)
- `story_qa/mobile_reel.png` (227,295 B)
- `story_qa/mobile_sheet.jpg` (238,067 B)
- `story_qa/mobile_sheet_v2.jpg` (231,878 B)
- `story_qa/mobile_top.png` (240,532 B)
- `story_qa/mobile_ui.png` (257,748 B)
- `story_qa/mobile_unmerge.png` (256,727 B)
- `story_qa/tablet_ui.png` (340,320 B)

## Notes

Used to diagnose the desktop hero not sitting centred on the left at mid widths.


