"""Pipon interaction + a11y checks, plus a clean element shot of the voices section."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5174"
OUT = Path("/workspace/pipon/shots")
OUT.mkdir(parents=True, exist_ok=True)
report = {}

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="chrome")
    except Exception:
        browser = p.chromium.launch()

    # ---- desktop: accordion + form ----
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:180]))
    page.on("console", lambda m: errs.append(m.text[:180]) if m.type == "error" else None)
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1800)

    toggles = page.locator(".step__toggle")
    report["steps_count"] = toggles.count()
    report["steps_aria_initial"] = [toggles.nth(i).get_attribute("aria-expanded") for i in range(toggles.count())]
    toggles.nth(0).click()
    page.wait_for_timeout(500)
    report["steps_aria_after_click"] = [toggles.nth(i).get_attribute("aria-expanded") for i in range(toggles.count())]
    report["panel_1_visible"] = page.locator("#step-panel-0").is_visible()
    report["panel_1_text"] = page.locator("#step-panel-0").inner_text().strip()
    report["panel_2_hidden"] = not page.locator("#step-panel-1").is_visible()
    toggles.nth(1).click()
    page.wait_for_timeout(300)
    report["aria_exclusive"] = [toggles.nth(i).get_attribute("aria-expanded") for i in range(toggles.count())]

    # email form
    page.locator('.email-pill input').fill("hello@example.com")
    page.locator('.email-pill button').click()
    page.wait_for_timeout(300)
    report["join_success_text"] = page.locator(".join__done").inner_text().strip() if page.locator(".join__done").count() else None
    report["form_gone"] = page.locator(".email-pill").count() == 0

    # footer link targets (no dead #top links)
    report["footer_hrefs"] = page.locator(".footer__col a").evaluate_all("els => els.map(e => e.getAttribute('href'))")

    # voices scrim computed style
    report["voices_scrim_desktop"] = page.evaluate(
        "() => getComputedStyle(document.querySelector('.voices__media'), '::after').backgroundImage.slice(0,160)"
    )
    page.locator(".voices").screenshot(path=str(OUT / "voices-desktop.png"))

    # anchor nav
    page.locator('.nav__pill a[href="#how"]').click()
    page.wait_for_timeout(700)
    report["anchor_scrollY"] = page.evaluate("() => Math.round(window.scrollY)")

    report["desktop_errors"] = errs[:10]
    ctx.close()

    # ---- mobile: menu, voices shot, tap targets ----
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    merrs = []
    page.on("pageerror", lambda e: merrs.append(str(e)[:180]))
    page.on("console", lambda m: merrs.append(m.text[:180]) if m.type == "error" else None)
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1800)
    burger = page.locator(".nav__burger")
    report["burger_box"] = burger.bounding_box()
    report["menu_visible_initial"] = page.locator(".menu").is_visible()
    burger.click()
    page.wait_for_timeout(400)
    report["burger_expanded"] = burger.get_attribute("aria-expanded")
    report["menu_visible_open"] = page.locator(".menu").is_visible()
    report["menu_link_count"] = page.locator(".menu__links a").count()
    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
    report["burger_after_escape"] = burger.get_attribute("aria-expanded")
    report["menu_visible_after_escape"] = page.locator(".menu").is_visible()

    # clean voices element shot at mobile
    page.locator(".voices").scroll_into_view_if_needed()
    page.wait_for_timeout(1200)
    report["voices_scrim_mobile"] = page.evaluate(
        "() => getComputedStyle(document.querySelector('.voices__media'), '::after').backgroundImage.slice(0,200)"
    )
    page.locator(".voices").screenshot(path=str(OUT / "voices-mobile.png"))
    report["mobile_errors"] = merrs[:10]
    ctx.close()

    # ---- reduced motion ----
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    report["reduced_motion"] = {
        "marquee_anim": page.evaluate("() => getComputedStyle(document.querySelector('.marquee__track')).animationName"),
        "reveal_opacity": page.evaluate("() => getComputedStyle(document.querySelector('[data-reveal]')).opacity"),
        "hero_video_paused": page.evaluate("() => document.querySelector('.hero__video').paused"),
    }
    ctx.close()

    # ---- 375px narrow ----
    ctx = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1200)
    report["375"] = page.evaluate("""() => ({
      scrollWidth: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      h1: getComputedStyle(document.querySelector('h1')).fontSize,
    })""")
    page.screenshot(path=str(OUT / "narrow-375.png"))
    ctx.close()

    browser.close()

print(json.dumps(report, indent=1))
