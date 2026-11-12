# Blue tap-highlight fix verification

**Category:** `qa` · **Script:** `qa_blue.py` · **Origin:** `/tmp/qa_blue.py`

Desktop + mobile verification of the tap-highlight fix: asserts the computed -webkit-tap-highlight-color is transparent on html and on every interactive control, that no blue pixels flash on a held touch, and that keyboard :focus-visible and the accordion still work.

## Requirements

playwright (Python), Chromium/Chrome; a served build on :4188.

## Run

```
python3 qa_blue.py   # requires a served build on :4188
```

## Outputs

PASS/FAIL lines printed to stdout; no files are written.

## Artifacts in this folder

- `run-log.txt` (3,129 B)

## Notes

Final result: 18/18 checks pass on desktop and mobile. Root cause was Chromium's default rgba(51, 181, 229, 0.4) tap highlight, not a CSS animation.


