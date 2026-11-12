#!/usr/bin/env python3
"""Pipon motion-graphics study 02 — three techniques, one plate-free mark.

Everything is drawn procedurally (NumPy distance fields + real brand fonts from
Pillow/FreeType) and encoded with ffmpeg/libopenh264. No stock footage, no AI
video model, no external assets. Exact brand hexes throughout.

Rev 02: the near-black squircle was removed from the logo. The mark is now just
three flat #E8532F dots on #FBF9F4 paper — so the ident no longer pops a black
tile. It lands with contact shadows, impact ripples and a drawing hairline
triangle instead. No BLACK token, no rounded-rect plate, anywhere.

Outputs to /workspace/motion:
  pipon-motion-reel.mp4   1280x720, 6.0s  — mark build / kinetic type / loop
  pipon-logo-sting.mp4    1080x1080, 2.6s — square social-safe ident
  pipon-dots-loop.mp4     1280x720, 2.0s  — mathematically seamless loop
  pipon-logo-sting.gif    480x480 preview
  pipon-motion-sheet.jpg  3x3 frame contact sheet
"""
import math
import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = "/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d69-4b32cb565000/mg"
OUT = "/workspace/motion"
TMP = os.path.join(BASE, "frames")
PJS = os.path.join(BASE, "fonts/PJS.ttf")
FRA = os.path.join(BASE, "fonts/Fraunces-Italic.ttf")

PAPER = (0xFB, 0xF9, 0xF4)      # --bg
INK = (0x1B, 0x19, 0x17)        # --fg (wordmark text only, never a plate)
ACCENT = (0xE8, 0x53, 0x2F)     # --accent
ACCENT_INK = (0xB8, 0x5C, 0x3C) # --accent-ink
FAINT = (0x9A, 0x92, 0x88)
RULE = (0xE4, 0xDE, 0xD5)
SHADOW = (0x5A, 0x2A, 0x1C)     # warm contact shadow under the dots

FPS = 30
_GRIDS = {}


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def seg(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eoc(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def eob(t, s=1.70158):
    t = clamp(t)
    u = t - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def font(path, size, name=None, axes=None):
    f = ImageFont.truetype(path, size)
    if name:
        f.set_variation_by_name(name)
    if axes:
        f.set_variation_by_axes(axes)
    return f


class Canvas:
    """Antialiased vector compositor on the exact paper field."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        key = (W, H)
        if key not in _GRIDS:
            _GRIDS[key] = np.mgrid[0:H, 0:W].astype(np.float32)
        self.gy, self.gx = _GRIDS[key]
        self.buf = np.empty((H, W, 3), np.float32)
        self.buf[:] = np.asarray(PAPER, np.float32)

    def blend(self, mask, color, alpha=1.0):
        a = mask * float(alpha)
        c = np.asarray(color, np.float32)
        self.buf[:] = self.buf * (1 - a[..., None]) + c * a[..., None]

    def disc(self, cx, cy, r, color, alpha=1.0):
        if r <= 0:
            return
        x0, x1 = max(0, int(cx - r - 2)), min(self.W, int(cx + r + 3))
        y0, y1 = max(0, int(cy - r - 2)), min(self.H, int(cy + r + 3))
        if x0 >= x1 or y0 >= y1:
            return
        xs = self.gx[y0:y1, x0:x1]
        ys = self.gy[y0:y1, x0:x1]
        d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        a = np.clip(r - d + 0.5, 0, 1) * float(alpha)
        region = self.buf[y0:y1, x0:x1]
        region[:] = region * (1 - a[..., None]) + np.asarray(color, np.float32) * a[..., None]

    def ring(self, cx, cy, r, width, color, alpha=1.0):
        """Antialiased annulus — used for the landing ripples (local region)."""
        pad = r + width + 2
        x0, x1 = max(0, int(cx - pad)), min(self.W, int(cx + pad + 1))
        y0, y1 = max(0, int(cy - pad)), min(self.H, int(cy + pad + 1))
        if x0 >= x1 or y0 >= y1:
            return
        xs, ys = self.gx[y0:y1, x0:x1], self.gy[y0:y1, x0:x1]
        d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        a = np.clip(width / 2 - np.abs(d - r) + 0.5, 0, 1) * float(alpha)
        region = self.buf[y0:y1, x0:x1]
        region[:] = region * (1 - a[..., None]) + np.asarray(color, np.float32) * a[..., None]

    def image(self):
        return Image.fromarray(np.clip(self.buf, 0, 255).astype(np.uint8), "RGB")


def text_mask(c, text, f, x, y, dy=0, box=None):
    layer = Image.new("L", (c.W, c.H), 0)
    ImageDraw.Draw(layer).text((x, y + dy), text, font=f, fill=255, anchor="lt")
    m = np.asarray(layer, np.float32) / 255.0
    if box:
        bx0, by0, bx1, by1 = box
        rect = np.zeros((c.H, c.W), np.float32)
        rect[max(0, int(by0)):min(c.H, int(by1)), max(0, int(bx0)):min(c.W, int(bx1))] = 1
        m *= rect
    return m


def tracked_mask(c, text, f, x, y, spacing):
    layer = Image.new("L", (c.W, c.H), 0)
    d = ImageDraw.Draw(layer)
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=f, fill=255, anchor="lt")
        cx += f.getlength(ch) + spacing
    return np.asarray(layer, np.float32) / 255.0, cx - x - spacing


def footer(c, t):
    W, H = c.W, c.H
    y = H - 56
    c.buf[int(y):int(y) + 1, 48:W - 48] = np.asarray(RULE, np.float32)
    f = font(PJS, 12, name="Medium")
    m, _ = tracked_mask(c, "PIPON  /  MOTION SYSTEM", f, 48, H - 43, 2.0)
    c.blend(m, FAINT, .95)
    right = "STUDY 02  ·  PLATE-FREE"
    mr, w = tracked_mask(c, right, f, 0, 0, 2.0)
    mr2, _ = tracked_mask(c, right, f, W - 48 - w, H - 43, 2.0)
    c.blend(mr2, FAINT, .95)


# ---------------------------------------------------------------- scene A ---
def scene_a(c, t, cfg):
    """Mark build, plate-free: three flat dots land with staggered overshoot,
    warm contact shadows bloom, accent ripples expand, a hairline triangle draws
    between them, then the wordmark wipes in. No squircle, no dark plate."""
    W, H = c.W, c.H
    R = cfg["R"]
    mcx, mcy = W / 2, cfg["cy"]
    offs = [(-1.91, -1.16), (1.91, -1.16), (0.0, 2.29)]
    pts = [(mcx + ox * R, mcy + oy * R) for ox, oy in offs]
    starts = [.26 + i * .12 for i in range(3)]

    # 1. Warm contact shadows bloom under each dot as it settles onto the paper.
    sh = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sh)
    for (x, y), d in zip(pts, starts):
        k = smooth(seg(t, d + .10, d + .62))
        if k > 0:
            ox, oy = R * .10, R * .20
            sd.ellipse([x - R + ox, y - R + oy, x + R + ox, y + R + oy], fill=int(34 * k))
    sm = np.asarray(sh.filter(ImageFilter.GaussianBlur(R * .40)), np.float32) / 255.0
    c.blend(sm, SHADOW, .9)

    # 2. Impact ripples — thin accent rings expanding out of each landing point.
    for (x, y), d in zip(pts, starts):
        q = seg(t, d + .34, d + 1.02)
        if 0 < q < 1:
            rr = R * (1.0 + 1.45 * eoc(q))
            c.ring(x, y, rr, max(1.5, R * .055), ACCENT_INK, (1 - q) * .38)

    # 3. Hairline triangle draws between the dot centres once they have landed.
    tk = eoc(seg(t, .92, 1.62))
    if tk > 0:
        ln = Image.new("L", (W, H), 0)
        ld = ImageDraw.Draw(ln)
        for i in range(3):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 3]
            ld.line([x1, y1, x1 + (x2 - x1) * tk, y1 + (y2 - y1) * tk],
                    fill=int(255 * .12), width=max(1, int(R * .03)))
        c.blend(np.asarray(ln, np.float32) / 255.0, ACCENT_INK, 1.0)

    # 4. The dots: staggered drop with ease-out-back overshoot and a slight grow.
    for (x, y), d in zip(pts, starts):
        kk = eob(seg(t, d, d + .46))
        alpha = smooth(seg(t, d, d + .16))
        if alpha > 0:
            c.disc(x, y - 1.9 * R * (1 - kk), R * (.42 + .58 * kk), ACCENT, alpha)

    # 5. Wordmark wipes in beneath the mark.
    wf = font(PJS, cfg["word"], name="SemiBold")
    label = "pipon"
    tw = wf.getlength(label)
    tx, ty = mcx - tw / 2, mcy + 3.29 * R + cfg["gap"]
    wk = eoc(seg(t, .82, 1.48))
    wm = text_mask(c, label, wf, tx, ty, dy=20 * (1 - wk))
    wipe = np.zeros((H, W), np.float32)
    wx1 = tx - 12 + (tw + 24) * wk
    wipe[:, max(0, int(tx - 12)):min(W, int(wx1))] = 1
    c.blend(wm * wipe, INK, .15 + .85 * wk)

    dk = clamp(eob(seg(t, 1.30, 1.70)))
    c.disc(tx + tw + 18, ty + cfg["word"] * .15, cfg["word"] * .075 * dk, ACCENT, dk)


# ---------------------------------------------------------------- scene B ---
def scene_b(c, t):
    """Kinetic type: word-by-word mask-up, rule wipe, three-dot pulse."""
    W, H = c.W, c.H
    x = 110
    fe = font(PJS, 13, name="Medium")
    me, _ = tracked_mask(c, "02  /  KINETIC TYPE", fe, x, 150, 2.4)
    c.blend(me, FAINT, smooth(seg(t, 0, .4)) * .9)

    f1 = font(FRA, 82, axes=[72, 400, 0, 1])
    f2 = font(PJS, 92, name="SemiBold")
    lines = [(x, 232, "small thoughts,", f1, ACCENT_INK, .12),
             (x, 344, "big people.", f2, INK, .30)]
    idx = 0
    for lx, ly, text, f, color, start in lines:
        cx = lx
        for word in text.split(" "):
            w = f.getlength(word)
            d = start + idx * .11
            k = eoc(seg(t, d, d + .52))
            box = (cx - 4, ly - 8, cx + w + 4, ly + f.size * 1.16)
            m = text_mask(c, word, f, cx, ly, dy=46 * (1 - k), box=box)
            c.blend(m, color, k)
            cx += w + f.getlength(" ")
            idx += 1

    # Accent rule wipes in beneath the type.
    rk = eoc(seg(t, .72, 1.30))
    if rk > 0:
        c.buf[int(478):int(481), x:int(x + 430 * rk)] = np.asarray(ACCENT, np.float32)

    # Three-dot pulse, the brand motif as a timing indicator.
    for i in range(3):
        d = .85 + i * .13
        k = seg(t, d, d + .30)
        pulse = .30 + .70 * (.5 + .5 * math.sin(2 * math.pi * (t - d) / .9 - i * .55))
        c.disc(x + 10 + i * 32, 542, 8, ACCENT, k * pulse)


# ---------------------------------------------------------------- scene C ---
def scene_c(c, t, period=2.0):
    """Seamless loop: every moving term is an integer number of cycles."""
    W, H = c.W, c.H
    u = t / period
    a = 2 * math.pi * u
    R = 64
    cx0, cy0 = W / 2, H / 2 - 22
    offs = [(-1.91, -1.16), (1.91, -1.16), (0.0, 2.29)]
    phase = [0.0, 1.7, 3.4]
    theta = math.radians(2.6) * math.sin(a)
    ct, st = math.cos(theta), math.sin(theta)
    dx, dy = 9 * math.sin(a), 6 * math.cos(a)

    pts = []
    for i, (ox, oy) in enumerate(offs):
        breathe = 1.0 + .018 * math.sin(a + phase[i])
        px, py = ox * R * breathe, oy * R * breathe
        rx, ry = px * ct - py * st, px * st + py * ct
        px2 = 4.5 * math.sin(a + phase[i])
        py2 = 3.2 * math.cos(2 * a + phase[i])
        pts.append((cx0 + dx + rx + px2, cy0 + dy + ry + py2, R * breathe))

    # Soft warm contact shadows on the paper.
    sh = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sh)
    for x, y, r in pts:
        ox, oy = r * .10, r * .20
        sd.ellipse([x - r + ox, y - r + oy, x + r + ox, y + r + oy], fill=34)
    sm = np.asarray(sh.filter(ImageFilter.GaussianBlur(R * .40)), np.float32) / 255.0
    c.blend(sm, SHADOW, .9)

    # Hairline triangle.
    ln = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(ln)
    for i in range(3):
        x1, y1, _ = pts[i]
        x2, y2, _ = pts[(i + 1) % 3]
        ld.line([x1, y1, x2, y2], fill=int(255 * (.065 + .025 * math.sin(a))), width=2)
    c.blend(np.asarray(ln, np.float32) / 255.0, ACCENT_INK, 1.0)

    for x, y, r in pts:
        c.disc(x, y, r, ACCENT)

    fe = font(PJS, 12, name="Medium")
    ml, _ = tracked_mask(c, "LOOP 01  ·  2.0s  ·  SEAMLESS", fe, 110, H - 108, 2.0)
    c.blend(ml, FAINT, .9)


# Plate-free geometry: R is dot radius, cy is the cluster centre. The mark now
# stands on its own without the squircle, so it sits a little larger and higher.
REEL_A = dict(R=64, cy=250, word=96, gap=34)
SQUARE_A = dict(R=90, cy=370, word=132, gap=48)
REEL_W, REEL_H = 1280, 720


def reel_frame(t):
    c = Canvas(REEL_W, REEL_H)
    if t < 2.0:
        scene_a(c, t, REEL_A)
    elif t < 2.2:
        ca, cb = Canvas(REEL_W, REEL_H), Canvas(REEL_W, REEL_H)
        scene_a(ca, t, REEL_A)
        scene_b(cb, t - 2.0)
        k = smooth((t - 2.0) / .2)
        c.buf[:] = ca.buf * (1 - k) + cb.buf * k
    elif t < 4.0:
        scene_b(c, t - 2.0)
    elif t < 4.2:
        cb, cc = Canvas(REEL_W, REEL_H), Canvas(REEL_W, REEL_H)
        scene_b(cb, t - 2.0)
        scene_c(cc, t - 4.0)
        k = smooth((t - 4.0) / .2)
        c.buf[:] = cb.buf * (1 - k) + cc.buf * k
    else:
        scene_c(c, t - 4.0)
    footer(c, t)
    return c.image()


def encode(name, W, H, n, frame_fn, bitrate="2600k"):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    for i in range(n):
        frame_fn(i / FPS).save(os.path.join(d, "f%04d.png" % i))
    mp4 = os.path.join(OUT, name + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(d, "f%04d.png"), "-frames:v", str(n),
                    "-c:v", "libopenh264", "-b:v", bitrate, "-pix_fmt", "yuv420p",
                    "-an", "-movflags", "+faststart", mp4], check=True)
    print("%-22s %dx%d  %d frames  %.1fs  %s" % (name, W, H, n, n / FPS, mp4))
    return d


def main():
    os.makedirs(OUT, exist_ok=True)

    reel_dir = encode("pipon-motion-reel", REEL_W, REEL_H, 180, reel_frame)

    def sting(t):
        c = Canvas(1080, 1080)
        scene_a(c, t, SQUARE_A)
        footer(c, t)
        return c.image()

    encode("pipon-logo-sting", 1080, 1080, 78, sting, "2400k")

    def loop(t):
        c = Canvas(REEL_W, REEL_H)
        scene_c(c, t, period=2.0)
        footer(c, t)
        return c.image()

    loop_dir = encode("pipon-dots-loop", REEL_W, REEL_H, 60, loop, "2200k")

    # Seam proof against the ACTUAL encoded frames: frame 0 vs the t=2.0 repeat.
    c60 = Canvas(REEL_W, REEL_H)
    scene_c(c60, 2.0, period=2.0)
    footer(c60, 2.0)
    f0 = np.asarray(Image.open(os.path.join(loop_dir, "f0000.png")), np.int16)
    f60 = np.asarray(c60.image(), np.int16)
    seam = float(np.abs(f0 - f60).mean())
    # Continuity: the last encoded frame should be one small step from frame 0.
    f59 = np.asarray(Image.open(os.path.join(loop_dir, "f0059.png")), np.int16)
    step = float(np.abs(f0 - f59).mean())
    print("loop seam delta (frame0 vs t=2.0):", round(seam, 5))
    print("loop wrap step (frame59 vs frame0):", round(step, 5))

    # Animated GIF preview of the square ident.
    gif = os.path.join(OUT, "pipon-logo-sting.gif")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", os.path.join(OUT, "pipon-logo-sting.mp4"),
                    "-vf", "fps=15,scale=480:480:flags=lanczos,split[s0][s1];"
                           "[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
                    "-loop", "0", gif], check=True)

    # 3x3 contact sheet of the reel.
    picks = [9, 24, 45, 72, 93, 114, 135, 153, 174]
    tw, th = 400, 225
    sheet = Image.new("RGB", (tw * 3 + 40, th * 3 + 96), (246, 243, 237))
    d = ImageDraw.Draw(sheet)
    d.text((20, 14), "PIPON  /  MOTION GRAPHICS STUDY 02  ·  PLATE-FREE MARK", fill=INK)
    d.text((20, 36), "three flat dots on paper · no squircle · Plus Jakarta Sans + Fraunces · H.264", fill=FAINT)
    f = font(PJS, 12, name="Medium")
    for i, idx in enumerate(picks):
        im = Image.open(os.path.join(reel_dir, "f%04d.png" % idx)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = 20 + (i % 3) * (tw + 10)
        y = 62 + (i // 3) * (th + 12)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + th - 20), "t = %.2fs" % (idx / FPS), font=f, fill=(255, 255, 255))
    sheet.save(os.path.join(OUT, "pipon-motion-sheet.jpg"), quality=90)
    print("SHEET + GIF written to", OUT)


if __name__ == "__main__":
    main()
