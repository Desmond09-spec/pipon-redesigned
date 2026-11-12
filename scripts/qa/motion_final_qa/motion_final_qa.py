"""Final QA for the plate-free motion preview.

Verifies the one-time `data-start` seek shows the mark immediately without
reintroducing the old load/seek loop, and that all three clips play cleanly.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/motion")
URL = "http://localhost:8090/"

INSTRUMENT = """
() => {
  window.__ev = {};
  document.querySelectorAll('video').forEach(function (v, i) {
    var key = v.getAttribute('src');
    var rec = window.__ev[key] = {loadstart:0, emptied:0, seeked:0, abort:0,
                                  stalled:0, error:0, samples:[]};
    ['loadstart','emptied','seeked','abort','stalled','error'].forEach(function (e) {
      v.addEventListener(e, function () { rec[e] += 1; });
    });
  });
  window.__t = setInterval(function () {
    document.querySelectorAll('video').forEach(function (v) {
      window.__ev[v.getAttribute('src')].samples.push(
        +v.currentTime.toFixed(2));
    });
  }, 250);
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", args=["--autoplay-policy=no-user-gesture-required"])
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    errors, failed = [], []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("requestfailed", lambda r: failed.append(r.url))

    page.goto(URL, wait_until="networkidle")
    page.evaluate(INSTRUMENT)
    page.wait_for_timeout(4200)  # >1 full 2.6s sting loop

    report = page.evaluate("""
    () => {
      clearInterval(window.__t);
      return {
        title: document.title,
        fonts: Array.from(document.fonts).filter(f => f.status === 'loaded')
                 .map(f => f.family).filter((v,i,a) => a.indexOf(v) === i).sort(),
        overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
        vids: Array.from(document.querySelectorAll('video')).map(function (v) {
          return {src: v.getAttribute('src'), ready: v.readyState,
                  paused: v.paused, t: +v.currentTime.toFixed(2),
                  dur: +v.duration.toFixed(2), w: v.videoWidth, h: v.videoHeight,
                  err: v.error ? v.error.code : null};
        }),
        ev: window.__ev
      };
    }
    """)

    # Screenshot just the square sting card so we can measure its pixels.
    card = page.query_selector(".card--square video")
    card.screenshot(path=str(ROOT / "sting-final-qa.png"))
    page.screenshot(path=str(ROOT / "preview-final-qa.png"), full_page=True)

    print(json.dumps(report, indent=2))
    print("console errors:", errors)
    print("failed requests:", failed)

    # Loop detection: any repeated loadstart / emptied means the seek restarted
    # the resource. More than a couple of samples per clip is fine; we look at
    # event counters and monotonic time within a single pass.
    print("\n--- loop verdict ---")
    for src, ev in report["ev"].items():
        s = ev["samples"]
        restarts = sum(1 for a, b in zip(s, s[1:]) if b < a - 0.35)
        print(f"{src}: loadstart={ev['loadstart']} emptied={ev['emptied']} "
              f"seeked={ev['seeked']} abort={ev['abort']} stalled={ev['stalled']} "
              f"error={ev['error']} | time restarts (loops)={restarts} | "
              f"t-range={min(s)}..{max(s)}")

    browser.close()
