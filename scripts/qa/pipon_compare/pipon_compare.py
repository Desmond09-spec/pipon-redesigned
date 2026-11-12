"""Build the three-way hero comparison sheets and full-page captures."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/pipon/shots")
OUT = Path("/workspace")
VARIANTS = ["original", "reaim", "brand"]
LABELS = {
    "original": "ORIGINAL  /  shelf spark, boxed at top",
    "reaim": "RE-AIM  /  same clip, no seam, copy overlaps",
    "brand": "BRAND  /  three-dot clip, true field",
}


def sheet(kind, w, h, cell_w):
    cw, ch = cell_w, int(cell_w * h / w) + 46
    canvas = Image.new("RGB", (cw * 3 + 40, ch + 10), (233, 231, 226))
    d = ImageDraw.Draw(canvas)
    for i, v in enumerate(VARIANTS):
        im = Image.open(ROOT / v / f"{kind}.png").convert("RGB")
        im = im.resize((cw, int(cw * h / w)))
        x = 10 + i * (cw + 10)
        canvas.paste(im, (x, 40))
        d.text((x + 4, 12), LABELS[v], fill=(26, 24, 22))
        d.rectangle((x, 40, x + cw, 40 + int(cw * h / w)), outline=(190, 186, 180), width=1)
    path = OUT / f"pipon-hero-{kind}-compare.jpg"
    canvas.save(path, quality=92)
    print("SHEET", path, canvas.size)


sheet("mobile", 390, 844, 390)
sheet("desktop", 1440, 900, 620)

FORCE = """() => {
  document.documentElement.style.scrollBehavior = 'auto';
  document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-in'));
  document.querySelectorAll('img[loading="lazy"]').forEach(el => el.loading = 'eager');
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    for v in VARIANTS:
        for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                      is_mobile=(name == "mobile"), has_touch=(name == "mobile"))
            page = ctx.new_page()
            page.goto(f"http://127.0.0.1:5174/?hero={v}", wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            page.wait_for_timeout(2600)
            page.evaluate(FORCE)
            page.wait_for_timeout(700)
            page.screenshot(path=str(ROOT / v / f"{name}-full.png"), full_page=True)
            ctx.close()
        print("FULL", v)
    browser.close()
