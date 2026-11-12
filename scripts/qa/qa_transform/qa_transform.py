import asyncio, os, json
from playwright.async_api import async_playwright

URL = "http://localhost:5174/"
OUT = "/tmp/transform_qa"
os.makedirs(OUT, exist_ok=True)

# The narrative clip bakes a fixed product window at source x 139..799 (1600x904).
WIN_L, WIN_R = 139, 799

MEASURE = r"""() => {
  const v = document.querySelector('.hero__video');
  const hero = document.querySelector('.hero');
  const copy = document.querySelector('.hero__copy').getBoundingClientRect();
  const hr = hero.getBoundingClientRect();
  const cs = getComputedStyle(v);
  const W = hr.width, H = hr.height;
  const vw = v.videoWidth, vh = v.videoHeight;
  // object-fit: cover mapping (source -> element-local)
  const cover = Math.max(W / vw, H / vh);
  const rw = vw * cover, rh = vh * cover;
  const pos = cs.objectPosition.split(' ');
  const px = parseFloat(pos[0]) / 100, py = parseFloat(pos[1]) / 100;
  const offX = (W - rw) * px, offY = (H - rh) * py;
  const localx = (sx) => offX + sx * cover;
  // CSS transform as a matrix (origin 0 50% => x' = a*x + e)
  const m = new DOMMatrixReadOnly(cs.transform === 'none' ? '' : cs.transform);
  const screenx = (sx) => m.a * localx(sx) + m.e;
  return {
    heroClass: hero.className,
    src: v.currentSrc.split('/').pop(),
    transform: cs.transform,
    objectPosition: cs.objectPosition,
    transition: cs.transitionProperty + ' / ' + cs.transitionDuration,
    opacity: cs.opacity,
    hasReady: v.classList.contains('is-ready'),
    paused: v.paused, muted: v.muted, loop: v.loop,
    readyState: v.readyState, t: +v.currentTime.toFixed(2),
    a: +m.a.toFixed(3), e: +m.e.toFixed(1),
    copyLeft: +copy.left.toFixed(1),
    winLeft_screen: +screenx(139).toFixed(1),
    winRight_screen: +screenx(799).toFixed(1),
    gap: +(copy.left - screenx(799)).toFixed(1),
    overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    fonts: document.fonts ? document.fonts.status : 'n/a',
  };
}"""

async def run():
    report = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True,
              args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])

        # --- 1. desktop band + control widths, story beat t=4.2s (product window) ---
        for w in [1024, 1100, 1200, 1280, 1439, 1440, 1600, 1920]:
            ctx = await b.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1)
            pg = await ctx.new_page()
            errs, fails = [], []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("requestfailed", lambda r: fails.append(r.url.split('/')[-1]))
            await pg.goto(URL, wait_until="networkidle")
            await pg.wait_for_timeout(700)
            await pg.add_style_tag(content="[data-reveal],.in-blur,.in-fade,.in-down{opacity:1!important;transform:none!important;filter:none!important;animation:none!important}")
            await pg.evaluate("()=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=4.2;}")
            await pg.wait_for_timeout(250)
            d = await pg.evaluate(MEASURE)
            d["console_errors"] = errs
            d["failed_requests"] = fails
            report["w%d" % w] = d
            await pg.screenshot(path="%s/story_%d.png" % (OUT, w))
            await ctx.close()

        # --- 2. reduced motion at two widths in the band ---
        for w in [1024, 1200]:
            ctx = await b.new_context(viewport={"width": w, "height": 900},
                                      reduced_motion="reduce", device_scale_factor=1)
            pg = await ctx.new_page()
            await pg.goto(URL, wait_until="networkidle")
            await pg.wait_for_timeout(700)
            d = await pg.evaluate(MEASURE)
            report["reduce_%d" % w] = d
            await pg.screenshot(path="%s/reduce_%d.png" % (OUT, w))
            await ctx.close()

        # --- 3. mobile control (must be full-bleed, no scoped transform) ---
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        pg = await ctx.new_page()
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_timeout(700)
        await pg.evaluate("()=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=4.2;}")
        await pg.wait_for_timeout(250)
        d = await pg.evaluate(MEASURE)
        report["mobile_390"] = d
        await pg.screenshot(path="%s/mobile_390.png" % (OUT))
        await ctx.close()

        await b.close()

    with open("%s/report.json" % OUT, "w") as f:
        json.dump(report, f, indent=2)

    # concise console table
    print("%-12s %-9s %-7s %-7s %-8s %-8s %-9s %-7s" %
          ("case", "scale", "tx", "winL", "winR", "copyL", "gap", "ovfX"))
    for k, d in report.items():
        print("%-12s %-9s %-7s %-7s %-8s %-8s %-9s %-7s" %
              (k, d["a"], d["e"], d["winLeft_screen"], d["winRight_screen"],
               d["copyLeft"], d["gap"], d["overflowX"]))
    print("\nreduce transform / transition:")
    for k in ["reduce_1024", "reduce_1200"]:
        print(" ", k, "->", report[k]["transform"], "|", report[k]["transition"],
              "| paused", report[k]["paused"], "| opacity", report[k]["opacity"])
    print("\nconsole errors / failed reqs across desktop cases:")
    for k in ["w1024", "w1200", "w1440", "w1600"]:
        print(" ", k, "errs", report[k]["console_errors"], "fails", report[k]["failed_requests"])

asyncio.run(run())
