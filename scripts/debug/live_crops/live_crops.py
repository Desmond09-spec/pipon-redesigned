import asyncio, os
from playwright.async_api import async_playwright

URL = "http://localhost:5174/"
OUT = "/tmp/live_crops"
os.makedirs(OUT, exist_ok=True)

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
        for w in [1024, 1100, 1200, 1280, 1440, 1600]:
            ctx = await b.new_context(viewport={"width":w,"height":900}, device_scale_factor=1)
            pg = await ctx.new_page()
            await pg.goto(URL, wait_until="networkidle")
            await pg.wait_for_timeout(900)
            await pg.add_style_tag(content="[data-reveal],.in-blur,.in-fade,.in-down{opacity:1!important;transform:none!important;filter:none!important;animation:none!important}")
            await pg.evaluate("()=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=4.2;}")
            await pg.wait_for_timeout(300)
            await pg.screenshot(path="%s/live_%d.png" % (OUT, w))
            d = await pg.evaluate("""()=>{
              const v=document.querySelector('.hero__video');
              const c=document.querySelector('.hero__copy').getBoundingClientRect();
              return {vw:v.videoWidth,vh:v.videoHeight,copyLeft:+c.left.toFixed(1),
                      op:getComputedStyle(v).objectPosition, t:+v.currentTime.toFixed(2)};
            }""")
            print(w, d)
            await ctx.close()
        await b.close()

asyncio.run(run())
