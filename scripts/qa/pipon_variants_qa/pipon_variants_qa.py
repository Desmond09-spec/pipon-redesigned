"""Freeze-frame + interaction + reduced-motion + narrow-viewport QA for the
three switchable Pipon hero variants. Uses real Chrome so H.264 decodes."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

OUT = Path("/workspace/pipon/shots/frames")
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:5174/"
VARIANTS = ["original", "reaim", "brand"]
TIMES = [0.0, 3.0, 6.0]

FREEZE = """(t) => {
  const v = document.querySelector('.hero__video');
  if (!v) return;
  v.play = () => Promise.resolve();   // defeat the IntersectionObserver auto-play
  v.pause();
  v.autoplay = false;
  v.currentTime = t;
  document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-in'));
}"""

report = {}
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")

    # 1. freeze frames for every variant / viewport / time
    for variant in VARIANTS:
        for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            ctx = browser.new_context(
                viewport={"width": w, "height": h}, device_scale_factor=1,
                is_mobile=(name == "mobile"), has_touch=(name == "mobile"),
            )
            page = ctx.new_page()
            page.goto(f"{BASE}?hero={variant}", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2300)
            for t in TIMES:
                page.evaluate(FREEZE, t)
                page.wait_for_timeout(420)
                page.screenshot(path=str(OUT / f"{variant}-{name}-t{int(t)}.png"))
            ctx.close()

    # 2. live switcher (only rendered with ?compare=1)
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.goto(f"{BASE}?compare=1", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1200)
    switcher = []
    for v in VARIANTS:
        page.click(f".hero-switcher__btn:has-text('{v}')")
        page.wait_for_timeout(700)
        switcher.append({
            "clicked": v,
            "url": page.url.split("5174")[-1],
            "heroClass": page.eval_on_selector(".hero", "e => e.className"),
            "src": page.eval_on_selector(".hero__video", "e => (e.currentSrc||e.src).split('/').pop()"),
            "pressed": page.eval_on_selector(f".hero-switcher__btn:has-text('{v}')", "e => e.getAttribute('aria-pressed')"),
        })
    report["switcher"] = switcher
    ctx.close()

    # 3. reduced motion: hero video must be paused but visible
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True,
                              reduced_motion="reduce")
    page = ctx.new_page()
    rm = []
    for v in VARIANTS:
        page.goto(f"{BASE}?hero={v}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1100)
        rm.append(page.eval_on_selector(".hero__video", """e => ({
            paused: e.paused, ready: e.readyState,
            opacity: getComputedStyle(e).opacity,
            src: (e.currentSrc||e.src).split('/').pop()
        })"""))
        page.screenshot(path=str(OUT / f"reduced-{v}.png"))
    report["reducedMotion"] = rm
    ctx.close()

    # 4. narrow viewport overflow + readable headline
    ctx = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    narrow = []
    for v in VARIANTS:
        page.goto(f"{BASE}?hero={v}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1400)
        narrow.append(page.evaluate("""() => ({
            viewport: document.documentElement.clientWidth,
            scrollWidth: document.documentElement.scrollWidth,
            overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
            h1: document.querySelector('h1').getBoundingClientRect().toJSON(),
            ctaVisible: document.querySelector('.btn-fill').getBoundingClientRect().bottom <= innerHeight + 2,
        })"""))
    report["narrow375"] = narrow
    ctx.close()
    browser.close()

print(json.dumps(report, indent=1))

# contact sheet of the mobile frozen frames
cells = []
for v in VARIANTS:
    for t in TIMES:
        im = Image.open(OUT / f"{v}-mobile-t{int(t)}.png").convert("RGB")
        im.thumbnail((250, 540))
        cells.append((f"{v} / t={int(t)}s", im))
CW, CH = 260, 580
sheet = Image.new("RGB", (CW * 3, CH * 3), (236, 234, 229))
d = ImageDraw.Draw(sheet)
for i, (lab, im) in enumerate(cells):
    x, y = (i % 3) * CW, (i // 3) * CH
    sheet.paste(im, (x + 5, y + 26))
    d.text((x + 6, y + 7), lab, fill=(20, 20, 20))
sheet.save(OUT / "mobile-frames.jpg", quality=90)
print("SHEET", OUT / "mobile-frames.jpg")
