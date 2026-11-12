# How-it-works accordion state QA

**Category:** `qa` · **Script:** `qa_steps.py` · **Origin:** `/tmp/qa_steps.py`

Opens each of the three How steps on desktop, mobile and with reduced motion, recording className, data-in / data-open, computed opacity/transform, panel hidden state and chevron transform.

## Requirements

playwright (Python), Chromium/Chrome; a served build on :4188.

## Run

```
python3 qa_steps.py [url] [output-dir]   # defaults: :4188, /tmp/qa_steps
```

## Outputs

desktop.png, mobile.png, reduced.png and a state report.

## Artifacts in this folder

- `pipon-how-click-fix.jpg` (214,588 B)
- `qa_steps/desktop.png` (345,918 B)
- `qa_steps/mobile.png` (220,249 B)
- `qa_steps/reduced.png` (335,782 B)
- `run-log.txt` (4,566 B)

## Notes

This is the check that caught the real bug where step 02 vanished: the scroll-reveal hook adds is-in imperatively, but React rewrote className on click and wiped it. The fix moved reveal state to a data-in attribute.


