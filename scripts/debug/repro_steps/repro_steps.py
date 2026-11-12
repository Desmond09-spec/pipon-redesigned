import asyncio, sys
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4188/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        await page.goto(URL, wait_until="networkidle")
        await page.locator("#how").scroll_into_view_if_needed()
        await page.wait_for_timeout(1600)  # let reveals settle

        steps = page.locator(".step")
        print("step count:", await steps.count())
        for i in range(3):
            print("before click", i, await steps.nth(i).get_attribute("class"),
                  "opacity", await steps.nth(i).evaluate("e => getComputedStyle(e).opacity"))

        # click step 2 (index 1)
        await page.locator(".step__toggle").nth(1).click()
        for ms in (0, 120, 300, 600, 1000):
            await page.wait_for_timeout(ms if ms else 30)
            info = await steps.nth(1).evaluate("""e => ({
                cls: e.className,
                opacity: getComputedStyle(e).opacity,
                transform: getComputedStyle(e).transform,
                panelHidden: e.querySelector('.step__panel').hidden,
                panelOpacity: getComputedStyle(e.querySelector('.step__panel p')).opacity
            })""")
            print(f"t+{ms}ms", info)
        await page.screenshot(path="/tmp/repro_steps_after.png")
        print("console errors:", errors)
        await browser.close()

asyncio.run(main())
