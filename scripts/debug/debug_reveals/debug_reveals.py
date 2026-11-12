import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await b.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:4188/", wait_until="domcontentloaded")
        await page.wait_for_timeout(800)
        await page.evaluate("""async () => {
          for (let y = 0; y < document.body.scrollHeight; y += 300) {
            window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90));
          }
          window.scrollTo(0, 0);
        }""")
        await page.wait_for_timeout(1500)
        bad = await page.evaluate("""() => [...document.querySelectorAll('[data-reveal]')]
          .map((e,i) => ({i, tag:e.tagName, cls:e.className, dataIn:e.hasAttribute('data-in'),
                          op:getComputedStyle(e).opacity, tf:getComputedStyle(e).transform,
                          rectTop: Math.round(e.getBoundingClientRect().top),
                          h: Math.round(e.getBoundingClientRect().height),
                          vis:getComputedStyle(e).visibility, disp:getComputedStyle(e).display}))
          .filter(x => x.op !== '1')""")
        for x in bad:
            print(x)
        print("total reveals:", await page.locator("[data-reveal]").count())
        await b.close()

asyncio.run(main())
