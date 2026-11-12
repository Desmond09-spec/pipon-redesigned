# Debug — candidate CSS transform A/B tests

**Category:** `debug` · **Script:** `test_transform.py` · **Origin:** `/tmp/test_transform.py`

Applies a dict of candidate transform rules to the story hero live in the browser and shoots each at 1024 / 1200 / 1280 px, labelling the results with Pillow.

## Requirements

playwright (Python), Chromium/Chrome, Pillow.

## Run

```
python3 test_transform.py   # requires dev server on :5174
```

## Outputs

/tmp/transform_test/*.png (archived here).

## Artifacts in this folder

- `run-log.txt` (458 B)
- `transform_test/A_baseline_1024.png` (375,912 B)
- `transform_test/A_baseline_1200.png` (405,906 B)
- `transform_test/A_baseline_1280.png` (418,867 B)
- `transform_test/B_tx46_s80_1024.png` (353,023 B)
- `transform_test/B_tx46_s80_1200.png` (381,011 B)
- `transform_test/B_tx46_s80_1280.png` (391,027 B)
- `transform_test/C_tx30_s87_1024.png` (360,811 B)
- `transform_test/C_tx30_s87_1200.png` (392,807 B)
- `transform_test/C_tx30_s87_1280.png` (402,877 B)
- `transform_test/D_s85_o25_1024.png` (358,460 B)
- `transform_test/D_s85_o25_1200.png` (388,397 B)
- `transform_test/D_s85_o25_1280.png` (401,234 B)
- `transform_test/sheet.jpg` (357,458 B)

## Notes

Winner (translateX + scale with transform-origin 0 50%) became the shipped breakpoint rules.


