# Motion preview page — final playback QA

**Category:** `qa` · **Script:** `motion_final_qa.py` · **Origin:** `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/motion_final_qa.py`

Verifies the one-time data-start seek on the plate-free motion preview shows the mark immediately without reintroducing the old load/seek loop, and that all three clips play without abort/stall/error events.

## Requirements

playwright (Python), Chromium/Chrome, a local HTTP server on :8090.

## Run

```
Serve the motion folder on port 8090, then: python3 motion_final_qa.py
```

## Outputs

A JSON-ish PASS/FAIL report printed to stdout; no files are written.

## Artifacts in this folder

- `run-log.txt` (2,870 B)

## Notes

Instrumentation counts loadstart / emptied / seeked / abort / stalled / error on each <video>.


