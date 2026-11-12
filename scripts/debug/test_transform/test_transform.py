import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont

URL = "http://localhost:5174/"
OUT = "/tmp/transform_test"
os.makedirs(OUT, exist_ok=True)

# candidate CSS applied to the story hero only
CANDS = {
    "A_baseline": "",
    "B_tx46_s80": """.hero--story .hero__video,
       .hero--story .hero__video.is-ready{
         transform-origin:0 50%; transform:translateX(46px) scale(.80);}""",
    "C_tx30_s87": """.hero--story .hero__video,
       .hero--story .hero__video.is-ready{
         transform-origin:0 50%; transform:translateX(30px) scale(.87);}""",
    "D_s85_o25": """.hero--story .hero__video,
       .hero--story .hero__video.is-ready{
         transform-origin:25% 50%; transform:scale(.85);}""",
}

WIDTHS = [1024, 1200, 1280]

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
        for cname, css in CANDS.items():
            for w in WIDTHS:
                ctx = await b.new_context(viewport={"width":w,"height":900}, device_scale_factor=1)
                pg = await ctx.new_page()
                await pg.goto(URL, wait_until="networkidle")
                await pg.wait_for_timeout(700)
                await pg.add_style_tag(content="[data-reveal],.in-blur,.in-fade,.in-down{opacity:1!important;transform:none!important;filter:none!important;animation:none!important}")
                if css:
                    await pg.add_style_tag(content=css)
                await pg.evaluate("()=>{const v=document.querySelector('.hero__video'); v.pause(); v.currentTime=4.2;}")
                await pg.wait_for_timeout(280)
                await pg.screenshot(path="%s/%s_%d.png" % (OUT, cname, w))
                await ctx.close()
        await b.close()

asyncio.run(run())

# contact sheet: rows = candidates, cols = widths
TW, TH = 512, 450
rows, cols = len(CANDS), len(WIDTHS)
pad, label_h = 8, 26
sheet = Image.new("RGB", (cols*(TW+pad)+pad, rows*(TH+label_h+pad)+pad), (238,235,228))
d = ImageDraw.Draw(sheet)
for r, cname in enumerate(CANDS):
    for c, w in enumerate(WIDTHS):
        im = Image.open("%s/%s_%d.png" % (OUT, cname, w)).convert("RGB").resize((TW,TH), Image.LANCZOS)
        x = pad + c*(TW+pad)
        y = pad + r*(TH+label_h+pad)
        d.text((x+4, y+4), "%s  @%dpx" % (cname, w), fill=(30,28,26))
        sheet.paste(im, (x, y+label_h))
sheet.save("%s/sheet.jpg" % OUT, quality=88)
print("saved", "%s/sheet.jpg" % OUT)
