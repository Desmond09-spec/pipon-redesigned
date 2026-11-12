import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
import numpy as np

URL = "http://127.0.0.1:4188/"

def blue_score(path):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mask = (b > r + 25) & (b > g + 10) & (b > 100)
    return int(mask.sum())

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(
            viewport={"width": 390, "height": 844}, is_mobile=True,
            has_touch=True, device_scale_factor=1)
        page = await ctx.new_page()
        cdp = await ctx.new_cdp_session(page)
        await page.goto(URL, wait_until="domcontentloaded")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(500)
        await page.locator("#how").scroll_into_view_if_needed()
        await page.wait_for_timeout(1200)

        box = await page.locator(".step__toggle").nth(1).bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

        await page.screenshot(path="/tmp/bluetouch_before.png")
        await cdp.send("Input.dispatchTouchEvent", {
            "type": "touchStart",
            "touchPoints": [{"x": cx, "y": cy, "id": 1}],
        })
        await page.wait_for_timeout(60)
        await page.screenshot(path="/tmp/bluetouch_held.png")
        await cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        await page.wait_for_timeout(400)
        await page.screenshot(path="/tmp/bluetouch_after.png")

        for f in ("before", "held", "after"):
            print(f, "blue_px =", blue_score(f"/tmp/bluetouch_{f}.png"))

        # side-by-side crop around the option
        ims = []
        for f in ("before", "held", "after"):
            im = Image.open(f"/tmp/bluetouch_{f}.png").convert("RGB")
            ims.append(im.crop((0, int(box["y"]) - 30, 390, int(box["y"] + box["height"]) + 30)))
        w = 390
        h = max(i.height for i in ims)
        sheet = Image.new("RGB", (w * 3, h + 28), (250, 249, 244))
        d = ImageDraw.Draw(sheet)
        for i, (lab, im) in enumerate(zip(("BEFORE", "HELD (tap down)", "AFTER"), ims)):
            sheet.paste(im, (i * w, 28))
            d.text((i * w + 8, 8), lab, fill=(20, 20, 20))
        sheet.save("/workspace/pipon-blue-flash-before.jpg", quality=92)
        print("saved before sheet")
        await browser.close()

asyncio.run(main())
