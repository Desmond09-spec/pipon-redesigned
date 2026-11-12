# Pipon — Python scripts & artifacts

Every Python script written during this project, the results it produced, and a README for each one.
Created at the request: *"All the Python scripts and all the artifacts created from the Python scripts,
add them into a folder in the root directory, with proper subfolders for each Python, QA, and debug script
and the results running those scripts produced (artifacts)."*

## Layout

```
scripts/
├── README.md                  ← this file (index, how-to-run, exclusions)
├── assets/fonts/              ← shared brand fonts used by the generators
├── python/                    ← 3 generator scripts
├── qa/                        ← 16 QA scripts + 1 shared capture set
└── debug/                     ← 11 diagnostic scripts + 1 shared evidence set
```

Each script gets **its own folder**:

```
<category>/<script-name>/
├── README.md        ← what it does, requirements, exact command, outputs, findings
├── <script-name>.py ← the script itself
└── artifacts/       ← the files that run produced (videos, posters, screenshots, sheets)
```

Two folders are **artifact collections rather than scripts** and are labelled as such in their READMEs:
`qa/site_captures/` (the shared browser-screenshot tree) and `debug/visual_evidence/` (loose
before/after comparison sheets).

**`python/` — generators.** Python scripts that produce shipped media (video, posters, contact sheets).

**`qa/` — quality assurance.** Scripts that verify behaviour, capture screenshots or build review sheets.

**`debug/` — diagnosis.** Short-lived scripts that reproduce a bug, measure the DOM or A/B-test a fix.

## Index

| Category | Folder | What it does |
| --- | --- | --- |
| `python` | [`make_hero_story/`](python/make_hero_story/README.md) | Procedurally renders the 19 s / 30 fps / 570-frame seamless hero film that explains what Pipon is. |
| `python` | [`make_pips/`](python/make_pips/README.md) | Procedural, mathematically seamless made-to-brand hero loop: three flat orange dots in the logo's 2-up / 1-down triangle drift on warm #FBF9F4 paper. |
| `python` | [`make_motion/`](python/make_motion/README.md) | Pipon motion-graphics study 02 — three techniques built around one plate-free mark. |
| `qa` | [`motion_final_qa/`](qa/motion_final_qa/README.md) | Verifies the one-time data-start seek on the plate-free motion preview shows the mark immediately without reintroducing the old load/seek loop, and that all three clips play without abort/stall/error events. |
| `qa` | [`pipon_brand_sheet/`](qa/pipon_brand_sheet/README.md) | Composites section crops and the hero shot into a 1200x760 visual summary of the brand alignment pass — "one mark, one accent hue, no plate, no second colour anywhere in the shipped design". |
| `qa` | [`pipon_compare/`](qa/pipon_compare/README.md) | Builds desktop and mobile comparison sheets for the three switchable hero variants (original shelf spark, re-aimed crop, made-to-brand clip) and captures full-page shots via Playwright at ?hero=<variant>. |
| `qa` | [`pipon_interaction/`](qa/pipon_interaction/README.md) | Pipon interaction + a11y checks (How accordion, join form, keyboard focus, console/page errors) plus a clean element shot of the voices section. |
| `qa` | [`pipon_sections/`](qa/pipon_sections/README.md) | Captures the sections touched by the brand alignment (#pip, #community, #how, #join, footer) at desktop and mobile, forcing all scroll reveals to their visible state first. |
| `qa` | [`pipon_variants_qa/`](qa/pipon_variants_qa/README.md) | Freeze-frame, interaction, reduced-motion and narrow-viewport QA for the three hero variants. |
| `qa` | [`pipon_worstframe/`](qa/pipon_worstframe/README.md) | Freezes threads.mp4 at its busiest frames (t = 0.1 / 3 / 9 s) and shoots the voices section at desktop and mobile to prove the copy stays readable wherever the loop happens to be. |
| `qa` | [`capture_full/`](qa/capture_full/README.md) | Generic full-page screenshot helper: forces scroll reveals and lazy images, then shoots desktop (1440x900) and mobile (390x844) at full height. |
| `qa` | [`qa_story/`](qa/qa_story/README.md) | Probes the story hero video on the dev server: computed object-fit/object-position, readyState, currentTime, font status and transform across several mid-width viewports, then writes per-candidate crops. |
| `qa` | [`qa_transform/`](qa/qa_transform/README.md) | Measures the baked-in product window (source x 139..799 at 1600x904) against the live hero copy box at 1024/1200/1440 px and on the production build, testing the translateX/scale compensation. |
| `qa` | [`qa_final/`](qa/qa_final/README.md) | Runs the same reveal/animation probe against both the Vite dev server and the production preview, then captures clean full-page screenshots at desktop, 1024 px mid-width and mobile. |
| `qa` | [`qa_steps/`](qa/qa_steps/README.md) | Opens each of the three How steps on desktop, mobile and with reduced motion, recording className, data-in / data-open, computed opacity/transform, panel hidden state and chevron transform. |
| `qa` | [`qa_blue/`](qa/qa_blue/README.md) | Desktop + mobile verification of the tap-highlight fix: asserts the computed -webkit-tap-highlight-color is transparent on html and on every interactive control, that no blue pixels flash on a held touch, and that keyboard :focus-visible and the accordion still work. |
| `qa` | [`verify_unmerge/`](qa/verify_unmerge/README.md) | Extracts frames from pips-story.mp4 around the 16.9-18.5 s un-merge beat and counts connected orange components (scipy.ndimage) to prove exactly three pips are present and no fourth centre dot appears. |
| `qa` | [`capture_steps/`](qa/capture_steps/README.md) | Scrolls #how into view and captures each opened step at desktop and mobile for the visual before/after sheet. |
| `qa` | [`site_captures/`](qa/site_captures/README.md) | The remaining pipon/shots/ browser screenshots produced by the interaction, section and per-round final-state QA passes, kept together rather than arbitrarily split across scripts. |
| `debug` | [`measure_gap/`](debug/measure_gap/README.md) | Reads live bounding boxes and computed styles for .hero__video, .hero__media, .hero__copy and .hero__h1 to quantify the visible gap between the video and the copy at mid widths. |
| `debug` | [`live_crops/`](debug/live_crops/README.md) | Shoots the live hero at 1024 / 1100 / 1200 / 1280 / 1440 / 1600 px so the baked-in product window can be compared against the responsive layout. |
| `debug` | [`test_transform/`](debug/test_transform/README.md) | Applies a dict of candidate transform rules to the story hero live in the browser and shoots each at 1024 / 1200 / 1280 px, labelling the results with Pillow. |
| `debug` | [`repro_steps/`](debug/repro_steps/README.md) | Minimal reproduction for step 02 disappearing after a click: jumps straight to #how, opens each step and logs className/data-in plus console errors. |
| `debug` | [`debug_reveals/`](debug/debug_reveals/README.md) | Scrolls the whole page in 300 px steps then reports which [data-reveal] elements still lack data-in. |
| `debug` | [`debug_reveals2/`](debug/debug_reveals2/README.md) | Same probe as pass 1 but across multiple viewport sizes, scrolling each reveal into view individually. |
| `debug` | [`debug_reveals3/`](debug/debug_reveals3/README.md) | Reproduces the QA order (jump straight to #how first) and reports data-in counts before and after clicks. |
| `debug` | [`diag_blue/`](debug/diag_blue/README.md) | Scores screenshots for blue-dominant pixels while a How step is tapped, to prove the cyan-blue rectangle is a browser tap highlight rather than a CSS animation or selection colour. |
| `debug` | [`diag_blue_touch/`](debug/diag_blue_touch/README.md) | Holds a touch down on a How step and samples the rendered pixels, then reads the computed -webkit-tap-highlight-color to confirm the UA default. |
| `debug` | [`interaction_check/`](debug/interaction_check/README.md) | Early interaction check for the nav theme flip on scroll (nav.nav--ink before/after scrolling), written during the Luxuria by Tiannah phase of this conversation. |
| `debug` | [`visual_evidence/`](debug/visual_evidence/README.md) | Loose before/after and contact-sheet JPGs from the workspace root that were composed by short one-off scripts rather than by one of the filed scripts. |

## Running these scripts

These are archived working scripts, not an installed package. Two things to know:

1. **Absolute paths.** Generators hardcode `/workspace/...` (`ROOT`, `MOTION`, `PUBLIC`, `OUT`).
   Change those constants if you check the repo out elsewhere.
2. **Local servers.** Most QA/debug scripts expect a running site: Vite dev on `:5174`,
   production preview on `:4173`, or a served build on `:4188`. Start the app first.

Common requirements: Python 3.11, `playwright` (Python bindings) with Chromium/Chrome, `numpy`,
`Pillow`, `scipy` (only `verify_unmerge.py`), and `ffmpeg` with `libopenh264` for the renderers.
Brand fonts live in `assets/fonts/`.

## Deliberately NOT in this folder

### Luxuria by Tiannah artifacts — excluded

The earlier Luxuria by Tiannah project is a **different brand**. None of its outputs are here:

| Excluded | Why |
| --- | --- |
| `/workspace/luxuria-by-tiannah.zip` | Luxuria deliverable bundle |
| `/workspace/dist/`, `/workspace/public/`, `/workspace/shots/` | Luxuria build, media and QA screenshots ("Time, made precious") |
| `/workspace/index.html`, `src/`, `package.json`, `pnpm-lock.yaml` | Luxuria Vite project itself |
| scratchpad `luxuria-spec.md`, `craft-hevc.mp4`, `shots-full/`, `cf/`, `imgcheck/`, `media-check/`, `gitignore-test/` | Luxuria spec, source media, captures and git-ignore experiments |

Two scripts (`qa/capture_full/`, `debug/interaction_check/`) were *written* during that phase and are
included because the brief asked for **all** Python scripts — but their Luxuria outputs are not.
Both READMEs carry an explicit exclusion note. `debug/interaction_check/` targets the Luxuria nav and
does not apply to Pipon; `qa/capture_full/` is a generic tool that was reused for Pipon.

### Other intentional omissions

- The installed skill's `shoot.py` — third-party tooling supplied by the MotionSites Web Builder skill,
  not a script written for this project.
- **Transient scratch**: per-frame PNG dumps (`mg/frames/`, `/tmp/pipon_*_frames/`), downloaded stock
  source videos and candidate clips (`pipon-cands/`, `pipon-media/`), and `__pycache__`. These are
  intermediate inputs/caches, not reviewable results.
- **Delivery bundles** (`pipon.zip`, `pipon-redesigned.zip`, `pipon-redesigned.bundle`,
  `motionsites-web-builder-skill.zip`) — packaging of the site, not script output. The one exception
  is `pipon-motion-assets.zip`, filed under `python/make_motion/artifacts/` because it is exactly
  that script's output.
- The site source and `dist/` builds — those are the product, not artifacts of these scripts.

### A git note

The repo `.gitignore` ignores `dist` and any directory named `shots`. Nothing inside `scripts/` uses
either name (captures are filed under `artifacts/captures/`), so this whole tree is trackable. The
production `dist/` assets are tracked with `git add -f` separately.
