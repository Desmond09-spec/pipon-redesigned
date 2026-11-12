"""One-page visual summary of the brand alignment pass."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("/workspace/pipon-brand-sheet.jpg")
S = Path("/workspace/pipon/shots/sections")
W, H = 1200, 760
sheet = Image.new("RGB", (W, H), (246, 243, 237))
d = ImageDraw.Draw(sheet)


def label(x, y, text, size=13):
    d.text((x, y), text, fill=(90, 82, 74))


def title(x, y, text):
    d.text((x, y), text, fill=(27, 25, 23))


title(28, 18, "PIPON  /  BRAND ALIGNMENT  ·  REV 02")
label(28, 40, "One mark. One accent hue. No plate, no second colour anywhere in the shipped design.")

# --- canonical mark, drawn from the measured 128px logo geometry --------------
# Rev 02: the near-black squircle is gone. The mark is three flat dots on paper,
# cropped to the dot cluster (viewBox 29 28 76 76) so it keeps its visual weight.
LOGO = 190
logo = Image.new("RGB", (LOGO, LOGO), (246, 243, 237))
ld = ImageDraw.Draw(logo)
sc = LOGO / 76
for cx, cy in [(46, 47), (88, 47), (67, 85)]:
    x, y, r = (cx - 29) * sc, (cy - 28) * sc, 11.5 * sc
    ld.ellipse([x - r, y - r, x + r, y + r], fill=(232, 83, 47))
sheet.paste(logo, (28, 78))
title(28, 278, "THE MARK")
label(28, 300, "plate-free / no dark tile", 11)
label(28, 316, "3 flat dots #E8532F", 11)
label(28, 332, "centres 46/88/67, r 11.5", 11)

# --- nav mark close-up, scaled up --------------------------------------------
nav = Image.open(S / "desktop-navlogo.png").convert("RGB")
nav = nav.resize((nav.width * 3, nav.height * 3), Image.LANCZOS)
sheet.paste(nav, (250, 108))
title(250, 278, "IN THE NAV")
label(250, 300, "same mark at 22px", 11)
label(250, 316, "beside the wordmark", 11)

# --- hero clip frame ---------------------------------------------------------
hero = Image.open("/workspace/pipon/shots/brand/desktop.png").convert("RGB")
hero.thumbnail((430, 250))
sheet.paste(hero, (560, 78))
title(560, 338, "IN THE HERO")
label(560, 358, "the same three dots, as a field", 11)

# --- warm palette ------------------------------------------------------------
PAL = [
    ("#F2A65A -> #E8532F", (242, 166, 90), (232, 83, 47)),
    ("#E8532F -> #B03B1B", (232, 83, 47), (176, 59, 27)),
    ("#EFC3A4 -> #C65B26", (239, 195, 164), (198, 91, 38)),
    ("#B85C3C -> #E8532F", (184, 92, 60), (232, 83, 47)),
    ("#F2C79B -> #B85C3C", (242, 199, 155), (184, 92, 60)),
]
title(28, 392, "ONE HUE, FIVE TONES  /  avatar + trust gradients")
for i, (name, c1, c2) in enumerate(PAL):
    x = 28 + i * 232
    sw = Image.new("RGB", (210, 46))
    sd = ImageDraw.Draw(sw)
    for px in range(210):
        t = px / 209
        sd.line([(px, 0), (px, 46)], fill=tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)))
    sheet.paste(sw, (x, 424))
    label(x, 476, name, 10)

# --- below-the-fold contexts -------------------------------------------------
for i, (f, cap) in enumerate([
    ("desktop-pip.png", "FEATURED PIP  /  three-dot watermark now a whisper"),
    ("desktop-join.png", "JOIN  /  accent-toned watermark behind the headline"),
    ("desktop-footer.png", "FOOTER  /  canonical mark"),
]):
    im = Image.open(S / f).convert("RGB")
    im.thumbnail((360, 170))
    x = 28 + i * 392
    sheet.paste(im, (x, 518))
    label(x, 696, cap, 10)

d.line([(28, 372), (W - 28, 372)], fill=(214, 208, 199), width=1)
d.line([(28, 502), (W - 28, 502)], fill=(214, 208, 199), width=1)
label(28, H - 26, "Rev 01: purple / teal / pink gradients + iridescent spark.  Rev 02: black logo plate removed, mark is three dots.", 11)
sheet.save(OUT, quality=92)
print("SHEET", OUT, sheet.size)
