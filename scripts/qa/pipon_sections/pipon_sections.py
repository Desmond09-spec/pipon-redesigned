"""Capture the sections touched by the brand alignment, at desktop and mobile."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/pipon/shots/sections")
ROOT.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:5174/"

FORCE = """() => {
  document.documentElement.style.scrollBehavior = 'auto';
  document.querySelectorAll('[data-reveal]').forEach(el => el.classList.add('is-in'));
}"""

SECTIONS = ["#pip", "#community", "#how", "#join", "footer"]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    for name, w, h in [("desktop", 1440, 900), ("mobile", 390, 844)]:
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1,
                                  is_mobile=(name == "mobile"), has_touch=(name == "mobile"))
        page = ctx.new_page()
        page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2200)
        page.evaluate(FORCE)
        page.wait_for_timeout(500)
        # Nav is fixed, so capture it first while the paper hero is behind it —
        # otherwise el.screenshot() below leaves the page scrolled over the dark
        # join/footer and the transparent nav picks up that dark background.
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        page.query_selector(".nav__logo").screenshot(path=str(ROOT / f"{name}-navlogo.png"))
        for sel in SECTIONS:
            el = page.query_selector(sel)
            if el:
                el.screenshot(path=str(ROOT / f"{name}-{sel.replace('#','').replace('footer','footer')}.png"))
        print("OK", name)
        ctx.close()
    browser.close()
print("SECTIONS", ROOT)
