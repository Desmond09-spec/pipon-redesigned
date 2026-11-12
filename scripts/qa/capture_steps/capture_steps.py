import asyncio, os
from playwright.async_api import async_playwright

OUT = "/tmp/steps_shots"
os.makedirs(OUT, exist_ok=True)

async def shoot(page, name):
    await page.locator("#how").scroll_into_view_if_needed()
    await page.wait_for_timeout(500)
    await page.screenshot(path=f"{OUT}/{name}.png")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        # desktop: open each step in turn
        page = await b.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:4188/", wait_until="domcontentloaded")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(500)
        await page.locator("#how").scroll_into_view_if_needed()
        await page.wait_for_timeout(1200)
        for i in range(3):
            await page.locator(".step__toggle").nth(i).click()
            await page.wait_for_timeout(700)
            await shoot(page, f"desktop_step{i+1}")
        await page.close()

        # mobile: step 2 open
        m = await b.new_page(viewport={"width": 390, "height": 844})
        await m.goto("http://127.0.0.1:4188/", wait_until="domcontentloaded")
        await m.evaluate("document.fonts.ready")
        await m.wait_for_timeout(500)
        await m.locator("#how").scroll_into_view_if_needed()
        await m.wait_for_timeout(1200)
        await m.locator(".step__toggle").nth(1).click()
        await m.wait_for_timeout(700)
        await m.screenshot(path=f"{OUT}/mobile_step2.png")
        await m.close()
        await b.close()
        print("captured")

asyncio.run(main())
