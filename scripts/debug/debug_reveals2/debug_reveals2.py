import asyncio, sys
from playwright.async_api import async_playwright

async def case(b, w, h, label):
    page = await b.new_page(viewport={"width": w, "height": h})
    await page.goto("http://127.0.0.1:4188/", wait_until="domcontentloaded")
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(500)
    n = await page.locator("[data-reveal]").count()
    for i in range(n):
        await page.evaluate("i => document.querySelectorAll('[data-reveal]')[i].scrollIntoView({block:'center'})", i)
        await page.wait_for_timeout(130)
    await page.wait_for_timeout(1200)
    bad = await page.evaluate("""() => [...document.querySelectorAll('[data-reveal]')]
      .map((e,i) => ({i, cls:e.className, dataIn:e.hasAttribute('data-in'),
                      op:getComputedStyle(e).opacity,
                      h:Math.round(e.getBoundingClientRect().height),
                      vh:innerHeight,
                      parentDisp:getComputedStyle(e.parentElement).display}))
      .filter(x => x.op !== '1')""")
    print(f"=== {label} {w}x{h}, {n} reveals, {len(bad)} hidden ===")
    for x in bad:
        print(" ", x)
    await page.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        await case(b, 1440, 900, "desktop")
        await case(b, 390, 844, "mobile")
        await b.close()

asyncio.run(main())
