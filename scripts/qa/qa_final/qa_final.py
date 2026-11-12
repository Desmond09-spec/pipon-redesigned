import asyncio, os, json
from playwright.async_api import async_playwright

DEV = "http://localhost:5174/"
DIST = "http://localhost:4173/"
OUT = "/tmp/final_qa"
os.makedirs(OUT, exist_ok=True)

REVEAL = "[data-reveal],.in-blur,.in-fade,.in-down{opacity:1!important;transform:none!important;filter:none!important;animation:none!important}"

PROBE = r"""() => {
  const v = document.querySelector('.hero__video');
  const cs = getComputedStyle(v);
  const de = document.documentElement;
  const imgs = [...document.images];
  return {
    heroClass: document.querySelector('.hero').className,
    src: v.currentSrc.split('/').pop(),
    poster: (v.poster||'').split('/').pop(),
    readyState: v.readyState, paused: v.paused, muted: v.muted, loop: v.loop,
    t: +v.currentTime.toFixed(2), dur: +v.duration.toFixed(2),
    hasReady: v.classList.contains('is-ready'),
    objectPosition: cs.objectPosition, transform: cs.transform,
    docHeight: de.scrollHeight, overflowX: de.scrollWidth - de.clientWidth,
    brokenImgs: imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src.split('/').pop()),
    imgCount: imgs.length,
    fonts: document.fonts ? document.fonts.status : 'n/a',
    sections: [...document.querySelectorAll('section, footer')].map(s=>s.className||s.tagName).slice(0,14),
  };
}"""

async def one(b, base, label, vp, variant="", rm=None, full=True, seek=None):
    ctx = await b.new_context(viewport=vp, device_scale_factor=1,
                              **({"reduced_motion": rm} if rm else {}))
    pg = await ctx.new_page()
    errs, fails, http = [], [], []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR "+str(e)))
    pg.on("requestfailed", lambda r: fails.append(r.url.split('/')[-1]+" :: "+str(r.failure)))
    pg.on("response", lambda r: http.append(str(r.status)+" "+r.url.split('/')[-1]) if r.status >= 400 else None)
    url = base + (("?"+variant) if variant else "")
    await pg.goto(url, wait_until="networkidle")
    await pg.wait_for_timeout(900)
    await pg.add_style_tag(content=REVEAL)
    if seek is not None:
        await pg.evaluate("t=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=t;}", seek)
        await pg.wait_for_timeout(250)
    d = await pg.evaluate(PROBE)
    d["console_errors"] = errs
    d["failed_requests"] = fails
    d["http_errors"] = http
    shot = "%s/%s.png" % (OUT, label)
    await pg.screenshot(path=shot, full_page=full)
    d["shot"] = shot.split('/')[-1]
    await ctx.close()
    return d

async def run():
    rep = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True,
              args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])

        # 1) FULL PAGE top-to-bottom on the production build, desktop + mobile
        rep["dist_desktop_full"] = await one(b, DIST, "dist_desktop_full", {"width":1440,"height":900})
        rep["dist_1024_full"]    = await one(b, DIST, "dist_1024_full",   {"width":1024,"height":900})
        rep["dist_mobile_full"]  = await one(b, DIST, "dist_mobile_full",  {"width":390,"height":844})

        # 2) all hero variants + compare switcher against rebuilt CSS (viewport shots)
        for v in ["hero=original","hero=reaim","hero=brand","hero=story","compare=1"]:
            key = "var_"+v.replace("=","_")
            rep[key] = await one(b, DIST, key, {"width":1440,"height":900}, variant=v, full=False)

        # 2b) compare switcher buttons actually enumerate all 4
        ctx = await b.new_context(viewport={"width":1440,"height":900})
        pg = await ctx.new_page()
        await pg.goto(DIST+"?compare=1", wait_until="networkidle")
        await pg.wait_for_timeout(500)
        rep["switcher_buttons"] = await pg.evaluate(
            "()=>[...document.querySelectorAll('.hero-switcher__btn')].map(b=>b.textContent.trim())")
        await ctx.close()

        # 3) FULL 19s loop: play through from 0, sample t at intervals, confirm it wraps & seams
        ctx = await b.new_context(viewport={"width":1440,"height":900})
        pg = await ctx.new_page()
        await pg.goto(DIST, wait_until="networkidle")
        await pg.wait_for_timeout(600)
        loop = await pg.evaluate("""async () => {
          const v = document.querySelector('.hero__video');
          v.muted = true; v.currentTime = 0;
          try { await v.play(); } catch(e) {}
          const samples = [];
          const t0 = performance.now();
          for (let i=0;i<8;i++){
            await new Promise(r=>setTimeout(r,600));
            samples.push(+v.currentTime.toFixed(2));
          }
          // jump near end and confirm wrap
          v.currentTime = v.duration - 0.30;
          await new Promise(r=>setTimeout(r,900));
          return {dur:+v.duration.toFixed(2), samples, afterWrap:+v.currentTime.toFixed(2),
                  paused:v.paused, loop:v.loop, ended:v.ended, readyState:v.readyState};
        }""")
        rep["loop_playthrough"] = loop
        await ctx.close()

        await b.close()

    with open(OUT+"/report.json","w") as f: json.dump(rep, f, indent=2)

    print("=== full-page (production dist) ===")
    for k in ["dist_desktop_full","dist_1024_full","dist_mobile_full"]:
        d=rep[k]
        print(" %-18s src=%-26s ovfX=%s docH=%s imgs=%s broken=%s errs=%s fails=%s http=%s" %
              (k, d["src"], d["overflowX"], d["docHeight"], d["imgCount"], d["brokenImgs"],
               len(d["console_errors"]), len(d["failed_requests"]), d["http_errors"]))
    print("\n=== variants (rebuilt CSS) ===")
    for k in ["var_hero_original","var_hero_reaim","var_hero_brand","var_hero_story","var_compare_1"]:
        d=rep[k]
        print(" %-18s -> %-16s hero=%-18s op=%-12s tr=%s" %
              (k, d["src"], d["heroClass"], d["objectPosition"], d["transform"][:22]))
    print("\n=== switcher buttons ===", rep["switcher_buttons"])
    print("\n=== full 19s loop ===")
    print(" ", rep["loop_playthrough"])

asyncio.run(run())
