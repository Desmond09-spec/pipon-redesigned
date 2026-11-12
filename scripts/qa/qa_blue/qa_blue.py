import asyncio, sys
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:4188/"
fails = []

def check(label, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label} {detail}")
    if not cond:
        fails.append(label)

async def case(browser, label, mobile):
    ctx = await browser.new_context(
        viewport={"width": 390 if mobile else 1440, "height": 844 if mobile else 900},
        is_mobile=mobile, has_touch=mobile)
    page = await ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    await page.goto(URL, wait_until="domcontentloaded")
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(500)
    await page.locator("#how").scroll_into_view_if_needed()
    await page.wait_for_timeout(1200)
    print(f"\n=== {label} ===")

    for i in range(3):
        v = await page.locator(".step__toggle").nth(i).evaluate("e => getComputedStyle(e).webkitTapHighlightColor")
        check(f"{label} toggle{i} tap-highlight transparent",
              v in ("rgba(0, 0, 0, 0)", "transparent", "rgba(0,0,0,0)"), v)

    # all interactive controls should be clean
    bad = await page.evaluate("""() => [...document.querySelectorAll('a, button, input')]
      .map(e => ({cls: e.className, v: getComputedStyle(e).webkitTapHighlightColor}))
      .filter(x => x.v !== 'rgba(0, 0, 0, 0)' && x.v !== 'transparent')""")
    check(f"{label} all controls clean", len(bad) == 0, str(bad[:3]))

    # accordion still works, no fade
    for i in range(3):
        await page.locator(".step__toggle").nth(i).click()
        await page.wait_for_timeout(700)
        s = await page.locator(".step").nth(i).evaluate("""e => ({
            op: getComputedStyle(e).opacity,
            open: e.getAttribute('data-open'),
            panel: e.querySelector('.step__panel').hidden
        })""")
        check(f"{label} step{i} opens & stays opaque",
              s["op"] == "1" and s["open"] == "true" and s["panel"] is False, str(s))

    # keyboard focus ring still present (accessibility not regressed)
    await page.locator(".step__toggle").nth(0).focus()
    await page.keyboard.press("Tab")
    await page.keyboard.press("Shift+Tab")
    ring = await page.locator(".step__toggle").nth(0).evaluate("e => getComputedStyle(e).outlineColor")
    check(f"{label} focus outline kept", ring not in ("", "transparent"), ring)

    check(f"{label} no console errors", len(errors) == 0, str(errors[:2]))
    await ctx.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        await case(b, "desktop", False)
        await case(b, "mobile", True)
        await b.close()
    print("\n=== RESULT ===", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
    sys.exit(1 if fails else 0)

asyncio.run(main())
