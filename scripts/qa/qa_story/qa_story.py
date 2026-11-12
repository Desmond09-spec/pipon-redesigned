import asyncio, json, os
from playwright.async_api import async_playwright

URL = "http://localhost:5174/"
OUT = "/tmp/story_qa"
os.makedirs(OUT, exist_ok=True)

async def probe(page, label):
    return await page.evaluate("""async () => {
      const v = document.querySelector('.hero__video');
      if (!v) return {error:'no video'};
      const cs = getComputedStyle(v);
      const de = document.documentElement;
      const fonts = document.fonts ? document.fonts.status : 'n/a';
      return {
        src: v.currentSrc.split('/').pop(),
        poster: (v.poster||'').split('/').pop(),
        readyState: v.readyState, networkState: v.networkState,
        paused: v.paused, muted: v.muted, loop: v.loop,
        t: +v.currentTime.toFixed(2), duration: +v.duration.toFixed(2),
        vw: v.videoWidth, vh: v.videoHeight,
        hasReady: v.classList.contains('is-ready'),
        opacity: cs.opacity, objectPosition: cs.objectPosition,
        overflowX: de.scrollWidth - de.clientWidth,
        fonts: fonts,
        heroClass: document.querySelector('.hero').className,
      };
    }""")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
        for name, vp in [("desktop", {"width":1440,"height":900}),
                         ("mobile",  {"width":390,"height":844})]:
            ctx = await browser.new_context(viewport=vp, device_scale_factor=1)
            page = await ctx.new_page()
            errs, fails, badimg = [], [], []
            page.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("requestfailed", lambda r: fails.append(r.url.split('/')[-1]+" :: "+str(r.failure)))
            page.on("response", lambda r: badimg.append(r.url.split('/')[-1]) if r.status>=400 else None)
            await page.goto(URL, wait_until="networkidle")
            await page.wait_for_timeout(1200)
            # force scroll reveals visible for clean screenshot
            await page.add_style_tag(content="[data-reveal],.in-blur,.in-fade,.in-down{opacity:1!important;transform:none!important;filter:none!important;animation:none!important}")
            state = await probe(page, name)
            await page.screenshot(path=f"{OUT}/{name}_top.png")
            # sample the video at several story beats by seeking
            beats = [("dots",0.5),("merge",1.9),("ui",4.2),("feed",7.2),
                     ("comment",8.6),("reel",12.5),("unmerge",17.4)]
            for tag,t in beats:
                await page.evaluate("(t)=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=t;}", t)
                await page.wait_for_timeout(220)
                await page.screenshot(path=f"{OUT}/{name}_{tag}.png")
            # resume and confirm playback advances
            await page.evaluate("()=>{const v=document.querySelector('.hero__video'); v.play().catch(()=>{});}")
            await page.wait_for_timeout(700)
            adv = await page.evaluate("()=>+document.querySelector('.hero__video').currentTime.toFixed(2)")
            print(json.dumps({"viewport":name,"state":state,"resumed_at":adv,
                              "console_errors":errs,"request_failed":fails,"http_errors":badimg}, indent=2))
            await ctx.close()
        await browser.close()

asyncio.run(run())
