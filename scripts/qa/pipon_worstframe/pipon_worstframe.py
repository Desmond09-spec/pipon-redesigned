"""Freeze threads.mp4 at its busiest frames and shoot the voices section to
prove the copy stays readable regardless of where the loop is."""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5174"
OUT = Path("/workspace/pipon/shots")
TIMES = [("t0", 0.1), ("t3", 3.0), ("t9", 9.0)]

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="chrome")
    except Exception:
        browser = p.chromium.launch()

    for label, w, h, mobile in [("desktop", 1440, 900, False), ("mobile", 390, 844, True)]:
        ctx = browser.new_context(viewport={"width": w, "height": h}, is_mobile=mobile, has_touch=mobile)
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1600)
        page.locator(".voices").scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        # force every reveal to its final state
        page.evaluate("""() => document.querySelectorAll('[data-reveal]').forEach(el => {
            el.classList.add('is-in'); el.style.transitionDuration='0s';
        })""")
        for name, t in TIMES:
            page.evaluate("""async (t) => {
                const v = document.querySelector('.voices__video');
                v.pause();
                v.currentTime = t;
                await new Promise(r => setTimeout(r, 350));
            }""", t)
            page.wait_for_timeout(250)
            page.locator(".voices").screenshot(path=str(OUT / f"voices-{label}-{name}.png"))
        ctx.close()
    browser.close()

print("wrote worst-frame shots:", [p.name for p in sorted(OUT.glob("voices-*-t*.png"))])
