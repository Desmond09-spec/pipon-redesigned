#!/usr/bin/env python3
"""Procedural, seamless, made-to-brand hero loop for Pipon.

Three flat orange dots in the logo's 2-up / 1-down triangle, drifting on warm
paper. EVERY moving term is an integer number of cycles over the loop, so
frame N == frame 0 exactly (verified below). The background is exactly the
page background #FBF9F4, so there is no seam and no scrim is required.

Outputs a 16:9 desktop clip and a 9:16 portrait clip from one generator.
"""
import math
import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = "/workspace/pipon/public"
TMP = "/tmp/pipon_frames"

# The one-value switch promised in the delivery note:
#   True  = flat discs, exactly like the three dots in the real logo
#   False = lambert-shaded 3D spheres (the first, less faithful render)
FLAT = True

# One accent hue, tonal variation only.
ACCENT = np.array((0xE8, 0x53, 0x2F), np.float32)   # --accent #E8532F
HIGH   = np.array((0xFB, 0xBE, 0x96), np.float32)   # specular
DEEP   = np.array((0xB0, 0x3B, 0x1B), np.float32)   # shaded edge (logo-ish depth)
SHADOW = (90, 42, 28, 44)                            # warm contact shadow
BLOOM  = (232, 83, 47, 22)                           # faint rim light
LINE   = (184, 92, 60)                               # --accent-ink #B85C3C
PAPER  = (0xFB, 0xF9, 0xF4)                         # exact --bg
SPEC   = np.array((255, 246, 238), np.float32)

FPS, DUR = 24, 8.0
N = int(FPS * DUR)                                   # 192 frames
TAU = 2 * math.pi

# Logo geometry, in units of dot radius R. Measured from the 128px logo:
# centres (46,47), (88,47), (67,85), radius 11 -> upper half-separation 1.91R,
# lower dot 3.45R below the upper pair. Cluster centroid (67, 59.7).
OFFSETS = [(-1.91, -1.16), (1.91, -1.16), (0.0, 2.29)]
PHASE   = [0.0, 1.7, 3.4]


def sphere_patch(R):
    """RGBA patch: flat logo disc when FLAT, lambert sphere otherwise. ~1.5px feather."""
    pad = int(R * 0.55)
    S = R + pad
    yy, xx = np.mgrid[-S:S + 1, -S:S + 1].astype(np.float32)
    d = np.sqrt(xx * xx + yy * yy) / R
    if FLAT:
        # Single flat fill. No gradient, no specular, no rim light — the mark
        # in the hero is now literally the mark in the logo.
        col = np.broadcast_to(ACCENT, d.shape + (3,)).copy()
    else:
        z = np.sqrt(np.clip(1.0 - d * d, 0.0, 1.0))
        lam = np.clip(-0.42 * (xx / R) - 0.52 * (yy / R) + 0.74 * z, 0.0, 1.0)
        t = lam[..., None]
        col = np.where(t < 0.55,
                       DEEP + (ACCENT - DEEP) * (t / 0.55),
                       ACCENT + (HIGH - ACCENT) * ((t - 0.55) / 0.45))
        sx, sy = -0.38 * R, -0.46 * R
        sd = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / (R * 0.42)
        spec = (np.clip(1.0 - sd, 0.0, 1.0) ** 2.4 * 0.55)[..., None]
        col = col * (1.0 - spec) + SPEC * spec
    alpha = np.clip((1.0 - d) * R / 1.5 + 0.5, 0.0, 1.0)
    rgba = np.concatenate([np.clip(col, 0, 255), alpha[..., None] * 255], axis=2)
    return Image.fromarray(rgba.astype(np.uint8), "RGBA"), S


def make_frame(W, H, cx, cy, R, frame):
    u = frame / N
    a = TAU * u
    img = Image.new("RGBA", (W, H), PAPER + (255,))

    # Shared cluster motion: tiny rotate + drift. All integer cycles.
    theta = math.radians(2.2) * math.sin(a)
    dx = 10 * math.sin(a + 0.4)
    dy = 7 * math.cos(a)
    ct, st = math.cos(theta), math.sin(theta)

    pts = []
    for i, (ox, oy) in enumerate(OFFSETS):
        breathe = 1.0 + 0.012 * math.sin(a + PHASE[i])
        px, py = ox * R * breathe, oy * R * breathe
        rx, ry = px * ct - py * st, px * st + py * ct
        # Independent parallax: 1-cycle and 2-cycle terms -> still seamless.
        px2 = 4.5 * math.sin(a + PHASE[i])
        py2 = 3.2 * math.cos(2 * a + PHASE[i])
        pts.append((cx + dx + rx + px2, cy + dy + ry + py2, R * breathe))

    # 1. Contact shadows (soft, warm, offset down-right). Kept in flat mode —
    #    it is a shadow ON the paper, not shading ON the dot, so the disc stays flat.
    shadow = SHADOW[:3] + ((30 if FLAT else SHADOW[3]),)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    for x, y, r in pts:
        ox, oy = r * 0.10, r * 0.20
        ds.ellipse([x - r + ox, y - r + oy, x + r + ox, y + r + oy], fill=shadow)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(R * 0.42)))

    # 2. Faint rim light — only for the shaded 3D render.
    if not FLAT:
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        db = ImageDraw.Draw(bl)
        for x, y, r in pts:
            e = r * 1.20
            db.ellipse([x - e, y - e, x + e, y + e], fill=BLOOM)
        img = Image.alpha_composite(img, bl.filter(ImageFilter.GaussianBlur(R * 0.30)))

    # 3. Hairline triangle: "people, ideas and creativity together". Breathing.
    ln = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(ln)
    la = int(255 * (0.070 + 0.028 * math.sin(a)))
    for i in range(3):
        x1, y1, _ = pts[i]
        x2, y2, _ = pts[(i + 1) % 3]
        dl.line([x1, y1, x2, y2], fill=LINE + (la,), width=max(1, int(R * 0.022)))
    img = Image.alpha_composite(img, ln)

    # 4. Dots on top.
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x, y, r in pts:
        patch, S = sphere_patch(int(round(r)))
        sp.paste(patch, (int(round(x)) - S, int(round(y)) - S), patch)
    img = Image.alpha_composite(img, sp)
    return img.convert("RGB")


def render(name, W, H, cx, cy, R, portrait=False):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    for f in range(N):
        make_frame(W, H, cx, cy, R, f).save(os.path.join(d, "f%04d.png" % f))
    # Seam check: generate frame N and compare to frame 0.
    f0 = np.asarray(Image.open(os.path.join(d, "f0000.png")), np.int16)
    fN = np.asarray(make_frame(W, H, cx, cy, R, N), np.int16)
    seam = float(np.abs(f0 - fN).mean())
    mp4 = os.path.join(OUT, name + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
           "-i", os.path.join(d, "f%04d.png"), "-frames:v", str(N),
           "-c:v", "libopenh264", "-b:v", "1400k", "-pix_fmt", "yuv420p",
           "-an", "-movflags", "+faststart", mp4]
    subprocess.run(cmd, check=True)
    poster = os.path.join(OUT, name + "-poster.jpg")
    Image.open(os.path.join(d, "f0000.png")).save(poster, quality=88, subsampling=0)
    print("%-16s %dx%d  R=%d  centre=(%d,%d)  seam_delta=%.5f  %s" %
          (name, W, H, R, cx, cy, seam, mp4))
    return seam


os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
# Desktop: cluster centred in the left field, level with the vertically centred
# copy. cy is the clip's exact vertical centre, so object-position: center keeps
# the dots centred at every desktop aspect ratio (no anchor drift on resize).
s1 = render("pips", 1600, 904, int(0.29 * 1600), int(0.50 * 904), 82)
# Portrait: cluster centred high, empty lower ~58% for a calm copy field.
s2 = render("pips-portrait", 720, 1280, 360, int(0.215 * 1280), 76, portrait=True)
print("SEAM_OK", s1 < 0.01 and s2 < 0.01)
