"""Full-page review capture: forces scroll reveals and lazy images, then shoots
desktop + mobile at full height. Complements the skill's shoot.py (first viewport)."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

url = sys.argv[1]
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("shots-full")
out.mkdir(parents=True, exist_ok=True)

VIEWS = [("desktop", 1440, 900), ("mobile", 390, 844)]

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="chrome")
        engine = "chrome"
    except Exception:
        browser = p.chromium.launch()
        engine = "chromium"
    report = {"browser": engine}
    for name, w, h in VIEWS:
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                  is_mobile=(name == "mobile"), has_touch=(name == "mobile"))
        page = ctx.new_page()
        errors, failed = [], []
        page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        page.on("requestfailed", lambda r: failed.append(f"{r.url[:100]} ({r.failure})"))
        page.on("response", lambda r: failed.append(f"{r.url[:100]} (HTTP {r.status})") if r.status >= 400 else None)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2200)
        # Reveal every block and disable smooth scroll so a full-page shot is accurate.
        page.evaluate("""() => {
          document.documentElement.style.scrollBehavior = 'auto';
          // Force the final rest state so a full-page still is deterministic.
          document.querySelectorAll('[data-reveal]').forEach(el => {
            el.classList.add('is-in');
            el.style.setProperty('--d', '0ms');
            el.style.transitionDuration = '0s';
          });
          document.querySelectorAll('img[loading=\"lazy\"]').forEach(el => el.loading = 'eager');
        }""")
        page.evaluate("""async () => {
          const step = window.innerHeight * 0.7;
          for (let y = 0; y < document.body.scrollHeight; y += step) {
            window.scrollTo(0, y);
            await new Promise(r => setTimeout(r, 90));
          }
          window.scrollTo(0, 0);
        }""")
        page.wait_for_timeout(1800)
        page.screenshot(path=str(out / f"{name}-full.png"), full_page=True)
        page.screenshot(path=str(out / f"{name}-viewport.png"))
        qa = page.evaluate("""() => {
          const vw = document.documentElement.clientWidth;
          return {
            scrollWidth: document.documentElement.scrollWidth, viewport: vw,
            horizontalOverflow: document.documentElement.scrollWidth > vw + 1,
            pageHeight: document.documentElement.scrollHeight,
            brokenImages: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.slice(0,110)),
            fontsLoaded: [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/"/g,'')))],
            videos: [...document.querySelectorAll('video')].map(v => ({ready: v.readyState, paused: v.paused, error: v.error ? v.error.code : null})),
            h1: document.querySelector('h1') ? {text: document.querySelector('h1').innerText.slice(0,80), font: getComputedStyle(document.querySelector('h1')).fontFamily.slice(0,40)} : null,
          };
        }""")
        qa["consoleErrors"] = errors[:10]
        qa["failedRequests"] = [f for f in failed if "ERR_ABORTED" not in f][:10]
        report[name] = qa
        ctx.close()
    browser.close()

print(json.dumps(report, indent=1))
print("Shots:", ", ".join(str(p) for p in sorted(out.glob('*.png'))))
