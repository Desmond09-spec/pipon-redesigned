# Final dev-vs-dist regression QA

**Category:** `qa` · **Script:** `qa_final.py` · **Origin:** `/tmp/qa_final.py`

Runs the same reveal/animation probe against both the Vite dev server and the production preview, then captures clean full-page screenshots at desktop, 1024 px mid-width and mobile.

## Requirements

playwright (Python), Chromium/Chrome.

## Run

```
Start dev (:5174) and preview (:4173), then: python3 qa_final.py
```

## Outputs

/tmp/final_qa/*.png (archived here).

## Artifacts in this folder

- `final_qa/clean_desktop.png` (1,270,909 B)
- `final_qa/clean_mid1024.png` (1,065,437 B)
- `final_qa/clean_mobile.png` (549,288 B)
- `final_qa/dist_1024_full.png` (889,640 B)
- `final_qa/dist_desktop_full.png` (1,090,687 B)
- `final_qa/dist_mobile_full.png` (409,729 B)
- `final_qa/faint_section_crop.png` (44,499 B)
- `final_qa/fullpage_clean_strip.jpg` (167,461 B)
- `final_qa/fullpage_strip.jpg` (79,153 B)
- `final_qa/report.json` (6,098 B)
- `final_qa/scrolled_pipsection.png` (360,038 B)
- `final_qa/var_compare_1.png` (379,428 B)
- `final_qa/var_hero_brand.png` (417,009 B)
- `final_qa/var_hero_original.png` (1,136,900 B)
- `final_qa/var_hero_reaim.png` (1,206,817 B)
- `final_qa/var_hero_story.png` (370,471 B)
- `pipon-story-fullpage.jpg` (167,461 B)
- `pipon-story-responsive-grid.jpg` (153,720 B)
- `run-log.txt` (1,504 B)

## Notes

Confirms the production build behaves like dev — the check run before each push.


