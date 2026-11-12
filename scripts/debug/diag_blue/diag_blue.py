import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import numpy as np

URL = "http://127.0.0.1:4188/"

def blue_score(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # blue-ish pixels: blue clearly dominant
    mask = (b > r + 25) & (b > g + 10) & (b > 100)
    return int(mask.sum()), float(b[mask].mean()) if mask.any() else 0

async def probe(browser, label, mobile):
    ctx = await browser.new_context(
        viewport={"width": 390 if mobile else 1440, "height": 844 if mobile else 900},
        is_mobile=mobile, has_touch=mobile, device_scale_factor=1,
    )
    page = await ctx.new_page()
    await page.goto(URL, wait_until="domcontentloaded")
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(500)
    await page.locator("#how").scroll_into_view_if_needed()
    await page.wait_for_timeout(1200)

    info = await page.locator(".step__toggle").nth(1).evaluate("""e => {
        const cs = getComputedStyle(e);
        return {
          tapHighlight: cs.webkitTapHighlightColor,
          userSelect: cs.userSelect || cs.webkitUserSelect,
          outline: cs.outline,
          selectionBg: getComputedStyle(e, '::selection').backgroundColor,
        };
    }""")
    print(f"\n=== {label} computed ===", info)

    box = await page.locator(".step__toggle").nth(1).bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    # capture during press (mouse down but not up)
    await page.mouse.move(cx, cy)
    await page.mouse.down()
    await page.screenshot(path=f"/tmp/blue_{label}_down.png")
    await page.mouse.up()

    # capture immediately after click, then a few frames later
    for ms in (0, 40, 100, 250):
        if ms:
            await page.wait_for_timeout(ms if ms == 40 else ms - 0)
        else:
            await page.locator(".step__toggle").nth(1).click()
        await page.screenshot(path=f"/tmp/blue_{label}_t{ms}.png")

    for f in [f"down", "t0", "t40", "t100", "t250"]:
        print(f"  {label} {f}: blue_px={blue_score(f'/tmp/blue_{label}_{f}.png')}")

    # document-level selection state right after a click
    sel = await page.evaluate("""() => {
        const s = getSelection();
        return { text: s ? s.toString().slice(0,80) : '', count: s ? s.rangeCount : 0,
                 active: document.activeElement ? document.activeElement.className : '' };
    }""")
    print(f"  {label} selection:", sel)
    await ctx.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        await probe(browser, "desktop", False)
        await probe(browser, "mobile", True)
        await browser.close()

asyncio.run(main())
