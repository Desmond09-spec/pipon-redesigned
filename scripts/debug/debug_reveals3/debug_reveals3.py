import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await b.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:4188/", wait_until="domcontentloaded")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(500)
        # replicate QA: jump straight to How first
        await page.locator("#how").scroll_into_view_if_needed()
        await page.wait_for_timeout(1500)
        print("after #how jump, data-in count:",
              await page.evaluate("document.querySelectorAll('[data-reveal][data-in]').length"))
        n = await page.locator("[data-reveal]").count()
        for i in range(n):
            await page.evaluate("i => document.querySelectorAll('[data-reveal]')[i].scrollIntoView({block:'center'})", i)
            await page.wait_for_timeout(130)
        await page.wait_for_timeout(1200)
        bad = await page.evaluate("""() => [...document.querySelectorAll('[data-reveal]')]
          .map((e,i) => ({i, cls:e.className, dataIn:e.hasAttribute('data-in'),
                          op:getComputedStyle(e).opacity,
                          top:Math.round(e.getBoundingClientRect().top),
                          h:Math.round(e.getBoundingClientRect().height)}))
          .filter(x => x.op !== '1')""")
        print("hidden:", bad)
        await b.close()

asyncio.run(main())
