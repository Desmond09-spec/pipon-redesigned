import json
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
result = {}

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="chrome")
    except Exception:
        browser = p.chromium.launch()

    # Desktop: nav theme flip on scroll
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    result["nav_before_scroll_ink"] = page.locator(".nav.nav--ink").count() > 0
    page.evaluate("window.scrollTo(0, 1000)")
    page.wait_for_timeout(600)
    result["nav_after_scroll_ink"] = page.locator(".nav.nav--ink").count() > 0
    result["nav_links"] = page.locator(".nav__links a").count()
    ctx.close()

    # Mobile: burger opens/closes, no overflow at 375 and 390
    for width in (375, 390):
        ctx = browser.new_context(viewport={"width": width, "height": 844}, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
        btn = page.locator(".nav__burger")
        btn.click()
        page.wait_for_timeout(500)
        opened = page.locator(".menu.menu--open").count() > 0
        expanded = btn.get_attribute("aria-expanded")
        locked = page.evaluate("document.body.style.overflow === 'hidden'")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        closed = page.locator(".menu.menu--open").count() == 0
        result[f"mobile_{width}"] = {
            "horizontalOverflow": overflow, "menuOpened": opened,
            "ariaExpandedOnOpen": expanded, "bodyScrollLocked": locked,
            "menuClosedOnEscape": closed,
        }
        ctx.close()

    # Reduced motion: everything visible, video paused
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    result["reduced_motion"] = page.evaluate("""() => {
      const reveals = [...document.querySelectorAll('[data-reveal]')];
      const hidden = reveals.filter(e => parseFloat(getComputedStyle(e).opacity) < 0.99).length;
      const h1 = document.querySelector('h1');
      return {
        revealCount: reveals.length,
        hiddenReveals: hidden,
        h1Opacity: h1 ? getComputedStyle(h1).opacity : null,
        heroPaused: document.querySelector('.hero__video') ? document.querySelector('.hero__video').paused : null,
      };
    }""")
    ctx.close()
    browser.close()

print(json.dumps(result, indent=1))
