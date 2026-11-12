import asyncio, sys
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4188/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/qa_steps"

STATE = """e => ({
  cls: e.className,
  dataIn: e.hasAttribute('data-in'),
  dataOpen: e.getAttribute('data-open'),
  opacity: getComputedStyle(e).opacity,
  transform: getComputedStyle(e).transform,
  panelHidden: e.querySelector('.step__panel').hidden,
  chevTransform: getComputedStyle(e.querySelector('.step__chev')).transform
})"""

failures = []

def check(label, cond, detail=""):
    ok = "PASS" if cond else "FAIL"
    print(f"  [{ok}] {label} {detail}")
    if not cond:
        failures.append(label + " " + detail)

async def run_case(browser, width, height, reduce=False, tag="desktop"):
    ctx = await browser.new_context(
        viewport={"width": width, "height": height},
        reduced_motion="reduce" if reduce else "no-preference",
    )
    page = await ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.goto(URL, wait_until="domcontentloaded")
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(500)
    await page.locator("#how").scroll_into_view_if_needed()
    await page.wait_for_timeout(1500)

    steps = page.locator(".step")
    toggles = page.locator(".step__toggle")
    print(f"\n=== {tag} {width}x{height} reduce={reduce} ===")

    # baseline reveal state
    for i in range(3):
        s = await steps.nth(i).evaluate(STATE)
        check(f"{tag} step{i} revealed", s["dataIn"] and s["opacity"] == "1", str(s["opacity"]))

    # open each step one at a time, sample over the full transition window
    for target in (0, 1, 2):
        await toggles.nth(target).click()
        for ms in (0, 150, 400, 900):
            await page.wait_for_timeout(ms if ms else 40)
            s = await steps.nth(target).evaluate(STATE)
            check(f"{tag} open{target} t+{ms} opacity=1", s["opacity"] == "1",
                  f"op={s['opacity']} tf={s['transform']} cls={s['cls']} in={s['dataIn']}")
        s = await steps.nth(target).evaluate(STATE)
        check(f"{tag} open{target} data-in kept", s["dataIn"] is True)
        check(f"{tag} open{target} panel visible", s["panelHidden"] is False)
        check(f"{tag} open{target} chevron rotated", s["chevTransform"] != "none", s["chevTransform"])
        # siblings must stay visible
        for j in range(3):
            if j == target:
                continue
            o = await steps.nth(j).evaluate("e => getComputedStyle(e).opacity")
            check(f"{tag} open{target} sibling{j} opacity=1", o == "1", o)

    # close the open step by clicking it again
    await toggles.nth(2).click()
    await page.wait_for_timeout(900)
    s = await steps.nth(2).evaluate(STATE)
    check(f"{tag} close2 opacity=1", s["opacity"] == "1", s["opacity"])
    check(f"{tag} close2 panel hidden", s["panelHidden"] is True)
    check(f"{tag} close2 data-open=false", s["dataOpen"] == "false")

    # rapid switching
    for i in (0, 1, 2, 0, 2, 1):
        await toggles.nth(i).click(delay=30)
    await page.wait_for_timeout(900)
    for i in range(3):
        s = await steps.nth(i).evaluate(STATE)
        check(f"{tag} rapid-step{i} opacity=1", s["opacity"] == "1", s["opacity"])

    # all page reveals visible after each one is actually scrolled into view.
    # Temporarily disable CSS smooth scrolling, otherwise scrollIntoView
    # animates and the sweep outruns the IntersectionObserver sampling.
    await page.evaluate("document.documentElement.style.scrollBehavior = 'auto'")
    n = await page.locator("[data-reveal]").count()
    for i in range(n):
        await page.evaluate(
            "i => document.querySelectorAll('[data-reveal]')[i]"
            ".scrollIntoView({block:'center', behavior:'instant'})", i)
        await page.wait_for_timeout(130)
    await page.wait_for_timeout(1200)
    hidden = await page.evaluate("""() => [...document.querySelectorAll('[data-reveal]')]
        .filter(e => getComputedStyle(e).opacity !== '1'
                  && e.getBoundingClientRect().height > 0)
        .map(e => e.className || e.tagName)""")
    check(f"{tag} all reveals visible", len(hidden) == 0, f"hidden={hidden}")
    ox = await page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check(f"{tag} no horizontal overflow", ox <= 0, f"overflowX={ox}")
    check(f"{tag} no console errors", len(errors) == 0, str(errors[:2]))

    await page.locator("#how").scroll_into_view_if_needed()
    await page.wait_for_timeout(400)
    await page.screenshot(path=f"{OUT}/{tag}.png")
    await ctx.close()

async def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        await run_case(browser, 1440, 900, False, "desktop")
        await run_case(browser, 390, 844, False, "mobile")
        await run_case(browser, 1440, 900, True, "reduced")
        await browser.close()
    print("\n=== RESULT ===", "ALL PASS" if not failures else f"{len(failures)} FAILURES")
    for f in failures:
        print("  -", f)
    sys.exit(1 if failures else 0)

asyncio.run(main())
