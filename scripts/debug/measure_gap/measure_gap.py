import asyncio, json
from playwright.async_api import async_playwright

URL = "http://localhost:5174/"

JS = """async () => {
  const v = document.querySelector('.hero__video');
  const media = document.querySelector('.hero__media');
  const copy = document.querySelector('.hero__copy');
  const h1 = document.querySelector('.hero__h1');
  const mr = media.getBoundingClientRect();
  const cr = copy.getBoundingClientRect();
  const hr = h1 ? h1.getBoundingClientRect() : null;
  const cs = getComputedStyle(v);
  const op = cs.objectPosition.split(' ');
  const px = parseFloat(op[0]) / 100;
  const vw = v.videoWidth, vh = v.videoHeight;
  // object-fit: cover transform
  const scale = Math.max(mr.width / vw, mr.height / vh);
  const rw = vw * scale, rh = vh * scale;
  const offX = (mr.width - rw) * px;
  const offY = (mr.height - rh) * 0.5;
  const sx = (x) => mr.left + offX + x * scale;
  const sy = (y) => mr.top + offY + y * scale;
  return {
    W: mr.width, H: mr.height, vw, vh, scale,
    offX, offY, objPos: cs.objectPosition,
    copyLeft: cr.left, copyRight: cr.right,
    h1Left: hr ? hr.left : null,
    // source-space window right edges and their screen positions
    edges: [799, 769, 739, 709, 699, 689, 679, 660].map(e => ({src:e, screen:+sx(e).toFixed(1)})),
    winLeftScreen: +sx(139).toFixed(1),
    winTopScreen: +sy(207).toFixed(1),
    winBotScreen: +sy(707).toFixed(1),
    overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
}"""

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
        for w in [1024, 1100, 1200, 1280, 1440, 1600, 1920]:
            ctx = await browser.new_context(viewport={"width":w,"height":900}, device_scale_factor=1)
            page = await ctx.new_page()
            await page.goto(URL, wait_until="networkidle")
            await page.wait_for_timeout(500)
            d = await page.evaluate(JS)
            # gap = copy left - window right (positive = clear)
            print("\n=== viewport %d ===" % w)
            print("  media %.0fx%.0f  scale %.4f  objPos %s  offX %.1f" % (d["W"], d["H"], d["scale"], d["objPos"], d["offX"]))
            print("  copyLeft %.1f  h1Left %s  winLeft %.1f  overflowX %s" % (d["copyLeft"], d["h1Left"], d["winLeftScreen"], d["overflowX"]))
            for e in d["edges"]:
                gap = d["copyLeft"] - e["screen"]
                print("    WIN right src %3d -> screen %6.1f   gap to copy %+7.1f %s" %
                      (e["src"], e["screen"], gap, "OK" if gap >= 24 else ("TIGHT" if gap >= 0 else "COLLIDE")))
            await ctx.close()
        await browser.close()

asyncio.run(run())
