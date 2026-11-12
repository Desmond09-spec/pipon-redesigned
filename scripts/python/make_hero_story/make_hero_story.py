#!/usr/bin/env python3
"""
Pipon hero story loop — procedural, frame-accurate, seamless.

Renders two H.264 hero clips (desktop 1600x904, portrait 720x1280) that tell
what Pipon is: three pips rotate clockwise, converge into one dot, that dot
expands into a product viewport (compose / post / scroll / like / comment),
the viewport animates into the existing pipon-motion-reel.mp4, and the reel's
final three dots merge back into a single dot which un-merges and rotates —
closing the loop on an identical frame.

Everything is drawn with Pillow/FreeType at 2x and downsampled. No stock
footage, no keystroke typing: text reveal is a soft horizontal wipe, the way
product films do it. The cursor only glides and clicks.
"""

import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# ----------------------------------------------------------------------------
# paths / constants
# ----------------------------------------------------------------------------
ROOT = "/workspace"
MOTION = os.path.join(ROOT, "motion")
PUBLIC = os.path.join(ROOT, "pipon", "public")
FONTDIR = os.path.join(MOTION, "fonts")
REEL = os.path.join(MOTION, "pipon-motion-reel.mp4")
REEL_FRAMES = "/tmp/pipon_reel_frames"
FRAME_DIR = "/tmp/pipon_story_frames"

S = 2                      # supersample
FPS = 30
DUR = 19.0
N = int(FPS * DUR)         # 570 frames

PAPER = (251, 249, 244)
ACCENT = (232, 83, 47)
ACCENT_DEEP = (200, 64, 31)
INK = (27, 25, 23)
MUTED = (139, 132, 120)
FAINT = (181, 174, 162)
LINE = (232, 226, 215)
CARD = (255, 254, 251)
WHITE = (255, 255, 255)
AVATARS = [(242, 166, 90), (232, 83, 47), (239, 195, 164), (184, 92, 60)]

# timeline boundaries (seconds)
# The loop seam sits *inside* the rotating-three-pips beat: t=0 and t=DUR show
# the identical mark (theta=0), so the last frame leads into the first with no
# visible jump. The single merged dot is the recurring waypoint of the cycle.
T_ROT_A = 1.0          # rotation, first half
T_MERGE = 1.9          # three pips converge into one dot
T_EXPAND = 2.7         # the dot unfolds into the product viewport
T_POST = 4.6           # cursor reaches Post
T_FEED = 6.2           # viewport scrolls, feed appears
T_LIKE = 7.5           # cursor likes a Pip
T_COMMENT = 9.0        # cursor comments; text wipe-reveals
T_MORPH = 9.8          # product window dissolves; reel begins its own intro
T_MORPH_END = 10.45    # cross-dissolve complete
T_REEL = 15.8          # reel has played its full 6.0s (180 frames)
T_REEL_MERGE = 16.9    # reel's last three dots merge into one
T_UNMERGE = 17.9       # dot un-merges into three pips
# 17.9 -> 19.0 : rotation, second half
OMEGA = (2.0 * math.pi / 3.0) / 2.1      # 120 deg over 2.1s of continuous rotation

# unit triangle (derived from the shipped pips.mp4 first frame)
TRI_U = [(-1.96, -1.13), (1.99, -1.14), (-0.04, 2.30)]

PIPS = [
    ("Maya A.", "@maya", "2m", "small thoughts are still thoughts.", 24, 6),
    ("Jules", "@julespips", "8m", "found my people in a 90-character post.", 41, 12),
    ("Kofi", "@kofi.wav", "14m", "coffee, rain, and a very good sentence.", 18, 3),
]

POST_TEXT = "the light at 6pm today was unreal."
COMMENT_TEXT = "this is exactly it."


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def sc(v):
    return int(round(v * S))


def bx(b):
    return tuple(sc(v) for v in b)


_font_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        path = os.path.join(FONTDIR, "PJS.ttf" if kind == "pjs" else "Fraunces-Italic.ttf")
        _font_cache[key] = ImageFont.truetype(path, sc(size))
    return _font_cache[key]


def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def phase(t, a, b):
    return clamp01((t - a) / (b - a))


def smooth(t):
    t = clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def out_cubic(t):
    t = clamp01(t)
    return 1.0 - (1.0 - t) ** 3


def in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t * t * t


def out_back(t, s=1.25):
    t = clamp01(t)
    return 1.0 + (s + 1.0) * (t - 1.0) ** 3 + s * (t - 1.0) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix_rect(a, b, t):
    return tuple(lerp(a[i], b[i], t) for i in range(4))


def rgba(c, a=255):
    return c + (int(a),)


def ease_path(pts, t):
    """piecewise eased cursor path; pts = [(x,y), ...]"""
    if t <= 0:
        return pts[0]
    if t >= 1:
        return pts[-1]
    seg = 1.0 / (len(pts) - 1)
    i = min(int(t / seg), len(pts) - 2)
    u = in_out((t - i * seg) / seg)
    return (lerp(pts[i][0], pts[i + 1][0], u),
            lerp(pts[i][1], pts[i + 1][1], u))


# ----------------------------------------------------------------------------
# scene
# ----------------------------------------------------------------------------
class Scene:
    def __init__(self, name, W, H, CX, CY, R, TRI, WIN, REELBOX, bitrate):
        self.name = name
        self.W, self.H = W, H
        self.SZ = (W * S, H * S)
        self.CX, self.CY, self.R = CX, CY, R
        self.TRI = TRI
        self.WIN = WIN
        self.RB = REELBOX
        self.bitrate = bitrate
        self.mask_cache = {}

        # pre-blurred contact shadow sprite for the pips
        side = sc(R * 4)
        m = Image.new("L", (side, side), 0)
        ImageDraw.Draw(m).ellipse((sc(R), sc(R) + sc(9), sc(3 * R), sc(3 * R) + sc(9)), fill=58)
        m = m.filter(ImageFilter.GaussianBlur(sc(13)))
        spr = Image.new("RGBA", (side, side), (122, 68, 44, 0))
        spr.putalpha(m)
        self.dot_shadow = spr
        self.shadow_side = side

        # static window shadow
        self.win_shadow = self._shadow(WIN, 26, blur=26, dy=14, alpha=40)

    # -- low level ----------------------------------------------------------
    def layer(self):
        return Image.new("RGBA", self.SZ, (0, 0, 0, 0))

    def _shadow(self, b, radius, blur=22, dy=12, alpha=46):
        l = self.layer()
        bb = (b[0], b[1] + dy, b[2], b[3] + dy)
        ImageDraw.Draw(l).rounded_rectangle(bx(bb), radius=sc(radius), fill=(74, 48, 34, alpha))
        l.putalpha(l.getchannel("A").filter(ImageFilter.GaussianBlur(sc(blur))))
        return l

    def rrect(self, l, b, r, fill=None, outline=None, w=1):
        ImageDraw.Draw(l).rounded_rectangle(bx(b), radius=sc(r), fill=fill,
                                           outline=outline, width=max(1, sc(w)))

    def txt(self, l, xy, s, size, color=INK, kind="pjs", bold=False, alpha=255, anchor="la"):
        d = ImageDraw.Draw(l)
        kw = dict(font=font(kind, size), fill=rgba(color, alpha), anchor=anchor)
        if bold:
            kw.update(stroke_width=max(1, sc(0.65)), stroke_fill=rgba(color, alpha))
        d.text((sc(xy[0]), sc(xy[1])), s, **kw)

    def wipe(self, l, x0, x1, p, soft=17):
        """soft left-to-right reveal — no per-character typing"""
        edge = lerp(x0, x1, smooth(p))
        xs = np.arange(self.W * S, dtype=np.float32)[None, :]
        grad = np.clip((sc(edge) - xs) / max(1, sc(soft)) * 255.0, 0, 255).astype(np.uint8)
        m = Image.fromarray(np.repeat(grad, self.H * S, axis=0), "L")
        l.putalpha(ImageChops.multiply(l.getchannel("A"), m))

    def clip_round(self, l, b, r):
        m = Image.new("L", self.SZ, 0)
        ImageDraw.Draw(m).rounded_rectangle(bx(b), radius=sc(r), fill=255)
        l.putalpha(ImageChops.multiply(l.getchannel("A"), m))

    def feather_mask(self, b, radius=22, blur=11, ramp=0.10):
        key = (tuple(round(v, 1) for v in b), radius, blur, ramp)
        if key in self.mask_cache:
            return self.mask_cache[key]
        m = Image.new("L", self.SZ, 0)
        ImageDraw.Draw(m).rounded_rectangle(bx(b), radius=sc(radius), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(sc(blur)))
        a = np.asarray(m).astype(np.float32) / 255.0
        yy = np.arange(self.H * S, dtype=np.float32)[:, None]
        top, bot = sc(b[1]), sc(b[3])
        fh = max(1.0, sc((b[3] - b[1]) * ramp))
        vramp = np.clip((yy - top) / fh, 0, 1) * np.clip((bot - yy) / fh, 0, 1)
        out = Image.fromarray((a * vramp * 255).astype(np.uint8), "L")
        self.mask_cache[key] = out
        return out

    # -- brand primitives ---------------------------------------------------
    def mark(self, l, cx, cy, r, color=ACCENT, alpha=255):
        d = ImageDraw.Draw(l)
        for ux, uy in TRI_U:
            x, y = cx + ux * r, cy + uy * r
            d.ellipse(bx((x - r, y - r, x + r, y + r)), fill=rgba(color, alpha))

    def dots(self, base, items, shadow=True):
        """items = [(cx, cy, r, alpha, ghost_bool)]"""
        if shadow:
            # Union (max) the contact shadows instead of alpha-stacking them.
            # When the three pips coincide into one mark there must be ONE
            # shadow, not three stacked ones that darken and then pop apart
            # as the pips separate.
            a_union = Image.new("L", self.SZ, 0)
            W, H = self.SZ
            for cx, cy, r, alpha, ghost in items:
                if ghost or r < 8:
                    continue
                spr = self.dot_shadow
                k = r / self.R
                if abs(k - 1.0) > 0.02:
                    spr = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))),
                                     Image.LANCZOS)
                x = sc(cx) - spr.width // 2
                y = sc(cy + 9 * k) - spr.height // 2
                x0, y0 = max(0, x), max(0, y)
                x1, y1 = min(W, x + spr.width), min(H, y + spr.height)
                if x1 <= x0 or y1 <= y0:
                    continue
                spr_a = spr.getchannel("A").crop((x0 - x, y0 - y, x1 - x, y1 - y))
                region = a_union.crop((x0, y0, x1, y1))
                a_union.paste(ImageChops.lighter(region, spr_a), (x0, y0))
            sh = Image.new("RGBA", self.SZ, (122, 68, 44, 0))
            sh.putalpha(a_union)
            base.alpha_composite(sh)
        l = self.layer()
        d = ImageDraw.Draw(l)
        for cx, cy, r, alpha, ghost in items:
            d.ellipse(bx((cx - r, cy - r, cx + r, cy + r)),
                      fill=rgba(ACCENT, alpha * (0.55 if ghost else 1.0)))
        base.alpha_composite(l)

    def ripple(self, base, cx, cy, p, rmax=150, color=ACCENT, width=3):
        if p <= 0 or p >= 1:
            return
        r = lerp(self.R * 0.7, rmax, out_cubic(p))
        a = int(120 * (1 - p) ** 1.5)
        l = self.layer()
        ImageDraw.Draw(l).ellipse(bx((cx - r, cy - r, cx + r, cy + r)),
                                  outline=rgba(color, a), width=max(1, sc(width)))
        base.alpha_composite(l)

    def cursor(self, base, x, y, press=0.0, alpha=255):
        """mac-style pointer, tip at (x,y)"""
        k = 1.0 - 0.10 * press
        pts = [(0, 0), (0, 18), (4.5, 14.1), (7.4, 21.0),
               (10.6, 19.5), (7.8, 12.7), (13.2, 12.7)]
        pts = [(x + px * 1.25 * k, y + py * 1.25 * k) for px, py in pts]
        l = self.layer()
        d = ImageDraw.Draw(l)
        # soft shadow
        sh = [(px + 2.2, py + 2.8) for px, py in pts]
        d.polygon([(sc(a), sc(b)) for a, b in sh], fill=(40, 30, 22, 60))
        d.polygon([(sc(a), sc(b)) for a, b in pts], fill=rgba(WHITE, alpha),
                  outline=rgba(INK, alpha), width=max(1, sc(1.1)))
        base.alpha_composite(l)

    def click_ripple(self, base, x, y, p):
        if p <= 0 or p >= 1:
            return
        r = lerp(4, 34, out_cubic(p))
        a = int(150 * (1 - p))
        l = self.layer()
        ImageDraw.Draw(l).ellipse(bx((x - r, y - r, x + r, y + r)),
                                  outline=rgba(ACCENT, a), width=max(1, sc(2)))
        base.alpha_composite(l)

    # -- product UI ---------------------------------------------------------
    def ui(self, base, t, win, opacity=255, scroll=0.0, post_p=0.0, post_clicked=False,
           like_p=0.0, liked=False, comment_p=0.0, push=0.0, comment_sent=False,
           cursor=None, click_p=0.0):
        x0, y0, x3, y3 = win
        w = x3 - x0
        h = y3 - y0
        if opacity <= 0:
            return
        l = self.layer()

        # window
        self.rrect(l, win, 24, fill=rgba(CARD, opacity), outline=rgba(LINE, opacity), w=1)

        # header
        self.mark(l, x0 + 34, y0 + 27, 4.0, alpha=opacity)
        self.txt(l, (x0 + 54, y0 + 18), "pipon", 19, INK, bold=True, alpha=opacity)
        self.rrect(l, (x3 - 58, y0 + 16, x3 - 26, y0 + 48), 16,
                   fill=rgba(AVATARS[0], opacity))
        self.txt(l, (x3 - 42, y0 + 23), "M", 13, WHITE, bold=True, alpha=opacity)
        ImageDraw.Draw(l).line(bx((x0, y0 + 60, x3, y0 + 60)), fill=rgba(LINE, opacity),
                               width=max(1, sc(1)))

        # tabs
        self.txt(l, (x0 + 26, y0 + 70), "For you", 13, INK, bold=True, alpha=opacity)
        ImageDraw.Draw(l).rounded_rectangle(bx((x0 + 26, y0 + 92, x0 + 76, y0 + 95)),
                                            radius=sc(2), fill=rgba(ACCENT, opacity))
        self.txt(l, (x0 + 100, y0 + 70), "Your people", 13, MUTED, alpha=opacity)

        # scrollable content
        content = self.layer()
        cy = -scroll

        # composer
        comp_y = y0 + 104 + cy
        self.rrect(content, (x0 + 18, comp_y, x3 - 18, comp_y + 62), 15,
                   fill=rgba((247, 244, 237), opacity), outline=rgba(LINE, opacity), w=1)
        ImageDraw.Draw(content).ellipse(bx((x0 + 30, comp_y + 17, x0 + 58, comp_y + 45)),
                                        fill=rgba(AVATARS[3], opacity))
        if post_p > 0:
            tl = self.layer()
            self.txt(tl, (x0 + 70, comp_y + 21), POST_TEXT, 13.5, INK, alpha=opacity)
            self.wipe(tl, x0 + 66, x0 + 66 + 260, post_p)
            content.alpha_composite(tl)
        else:
            self.txt(content, (x0 + 70, comp_y + 21), "Share a small thought...", 13.5,
                     FAINT, alpha=opacity)
        btn = (x3 - 100, comp_y + 13, x3 - 26, comp_y + 49)
        self.rrect(content, btn, 18,
                   fill=rgba(ACCENT_DEEP if post_clicked else ACCENT, opacity))
        self.txt(content, ((btn[0] + btn[2]) / 2, comp_y + 23), "Post", 13, WHITE,
                 bold=True, alpha=opacity, anchor="ma")

        # feed
        c_tops = [y0 + 182 + cy, y0 + 284 + cy + push, y0 + 386 + cy + push]
        for i, (nm, hd, tm, body, likes, comments) in enumerate(PIPS):
            top = c_tops[i]
            cb = (x0 + 18, top, x3 - 18, top + 92)
            self.rrect(content, cb, 15, fill=rgba(WHITE, opacity),
                       outline=rgba(LINE, opacity), w=1)
            ImageDraw.Draw(content).ellipse(bx((x0 + 30, top + 14, x0 + 58, top + 42)),
                                            fill=rgba(AVATARS[i % 4], opacity))
            self.txt(content, (x0 + 68, top + 12), nm, 12.5, INK, bold=True, alpha=opacity)
            self.txt(content, (x0 + 68 + len(nm) * 7.4, top + 13), hd + "  .  " + tm,
                     11.5, MUTED, alpha=opacity)
            self.txt(content, (x0 + 30, top + 48), body, 12.5, INK, alpha=opacity)
            # actions
            hy = top + 72
            hx = x0 + 34
            heart = self.heart(hx, hy, 6.2,
                               filled=(liked and i == 0),
                               color=ACCENT if (liked and i == 0) else MUTED,
                               alpha=opacity)
            content.alpha_composite(heart)
            self.txt(content, (hx + 14, hy - 7), str(likes + (1 if liked and i == 0 else 0)),
                     11.5, MUTED, alpha=opacity)
            bx2 = x0 + 92
            self.bubble(content, bx2, hy, 6.2, opacity)
            self.txt(content, (bx2 + 14, hy - 7),
                     str(comments + (1 if (comment_sent and i == 0) else 0)),
                     11.5, MUTED, alpha=opacity)

        # revealed comment under the first pip
        if comment_p > 0:
            cp = smooth(comment_p)
            cb = (x0 + 30, y0 + 186 + cy, x3 - 26, y0 + 186 + cy + 36)
            self.rrect(content, cb, 12,
                       fill=rgba((247, 244, 237), int(opacity * cp)),
                       outline=rgba(LINE, int(opacity * cp)), w=1)
            tl = self.layer()
            self.txt(tl, (x0 + 42, y0 + 186 + cy + 10), "Tess   " + COMMENT_TEXT,
                     11.5, INK, alpha=int(opacity * cp))
            self.wipe(tl, x0 + 40, x0 + 250, comment_p)
            content.alpha_composite(tl)

        # comment composer pinned at the bottom of the window
        if 7.5 <= t < T_COMMENT:
            q = phase(t, 7.62, 7.95)
            if q > 0:
                q = smooth(q)
                cby = y3 - 52
                self.rrect(content, (x0 + 18, cby, x3 - 18, cby + 38), 12,
                           fill=rgba((247, 244, 237), int(opacity * q)),
                           outline=rgba(LINE, int(opacity * q)), w=1)
                self.txt(content, (x0 + 30, cby + 11), "Add a comment...", 11.5,
                         FAINT, alpha=int(opacity * q))
                tl = self.layer()
                self.txt(tl, (x0 + 30, cby + 11), COMMENT_TEXT, 11.5, INK,
                         alpha=int(opacity * q))
                self.wipe(tl, x0 + 28, x0 + 190, phase(t, 7.95, 8.55))
                content.alpha_composite(tl)
                arrow_a = int(opacity * smooth(phase(t, 8.35, 8.6)) * q)
                if arrow_a > 0:
                    self.rrect(content, (x3 - 56, cby + 5, x3 - 24, cby + 33), 14,
                               fill=rgba(ACCENT, arrow_a))
                    self.txt(content, (x3 - 40, cby + 11), ">", 12, WHITE,
                             bold=True, alpha=arrow_a, anchor="ma")

        self.clip_round(content, (x0 + 12, y0 + 98, x3 - 12, y3 - 12), 10)
        l.alpha_composite(content)
        l.putalpha(ImageChops.multiply(l.getchannel("A"),
                                       Image.new("L", self.SZ, 255)))
        base.alpha_composite(l)

        if cursor:
            cxp, cyp, press = cursor
            self.click_ripple(base, cxp, cyp, click_p)
            self.cursor(base, cxp, cyp, press)

    def heart(self, x, y, r, filled=False, color=MUTED, alpha=255):
        l = self.layer()
        d = ImageDraw.Draw(l)
        # two lobes + a triangle, scaled around (x,y)
        pts = [(-1, -0.25), (-1, 0.15), (-0.72, 0.45), (-0.35, 0.75), (0, 1.0),
               (0.35, 0.75), (0.72, 0.45), (1, 0.15), (1, -0.25), (0.72, -0.62),
               (0.35, -0.85), (0, -0.55), (-0.35, -0.85), (-0.72, -0.62)]
        p = [(x + px * r, y + py * r) for px, py in pts]
        if filled:
            d.polygon([(sc(a), sc(b)) for a, b in p], fill=rgba(color, alpha))
        else:
            d.line([(sc(a), sc(b)) for a, b in p] + [(sc(p[0][0]), sc(p[0][1]))],
                   fill=rgba(color, alpha), width=max(1, sc(1.3)), joint="curve")
        return l

    def bubble(self, l, x, y, r, alpha=255):
        d = ImageDraw.Draw(l)
        d.rounded_rectangle(bx((x - r, y - r * 0.8, x + r, y + r * 0.55)),
                            radius=sc(r * 0.45), outline=rgba(MUTED, alpha),
                            width=max(1, sc(1.3)))
        d.polygon([(sc(x - r * 0.15), sc(y + r * 0.45)),
                   (sc(x - r * 0.15), sc(y + r * 1.0)),
                   (sc(x + r * 0.38), sc(y + r * 0.45))],
                  outline=rgba(MUTED, alpha))

    # -- reel ---------------------------------------------------------------
    def reel_frame(self, idx, b, opacity=255):
        path = os.path.join(REEL_FRAMES, "f%03d.png" % max(0, min(179, idx)))
        if not os.path.exists(path):
            return self.layer()
        im = Image.open(path).convert("RGB").resize(
            (max(1, sc(b[2] - b[0])), max(1, sc(b[3] - b[1]))), Image.LANCZOS).convert("RGBA")
        mask = self.feather_mask(b)
        crop = mask.crop(bx(b))
        if opacity < 255:
            crop = crop.point(lambda v: v * opacity // 255)
        im.putalpha(crop)
        out = self.layer()
        out.alpha_composite(im, (sc(b[0]), sc(b[1])))
        return out

    # -- main ---------------------------------------------------------------
    def render(self, t):
        base = Image.new("RGBA", self.SZ, rgba(PAPER))
        cx, cy, R = self.CX, self.CY, self.R

        def tri_at(theta):
            out = []
            for px, py in self.TRI:
                dx, dy = px - cx, py - cy
                out.append((cx + dx * math.cos(theta) - dy * math.sin(theta),
                            cy + dx * math.sin(theta) + dy * math.cos(theta)))
            return out

        def theta(t):
            if t <= T_ROT_A:
                return OMEGA * t
            if t >= T_UNMERGE:
                return -OMEGA * (DUR - t)
            return None

        # ---------------- rotation halves (the loop seam) ------------------
        if t < T_ROT_A or t >= T_UNMERGE:
            th = theta(t)
            items = []
            for k in range(4, 0, -1):
                for px, py in tri_at(th - k * 0.055):
                    items.append((px, py, R * (1 - 0.035 * k), 26 - 4 * k, True))
            for px, py in tri_at(th):
                items.append((px, py, R, 255, False))
            self.dots(base, items)
            return self.finish(base)

        # ---------------- converge / merge ---------------------------------
        if t < T_MERGE:
            p = phase(t, T_ROT_A, T_MERGE)
            th0 = OMEGA * T_ROT_A
            src = tri_at(th0)
            items = []
            for i, (sx, sy) in enumerate(src):
                q = out_cubic(clamp01((p - i * 0.055) / 0.80))
                x, y = lerp(sx, cx, q), lerp(sy, cy, q)
                r = R * (1 - 0.30 * q)
                items.append((x, y, r, 255, False))
            if p > 0.76:
                q = smooth((p - 0.76) / 0.24)
                for i, (x, y, r, a, g) in enumerate(items):
                    items[i] = (x, y, lerp(r, 0, q), int(255 * (1 - q)), g)
                self.dots(base, items)
                l = self.layer()
                ImageDraw.Draw(l).ellipse(bx((cx - R * q, cy - R * q,
                                              cx + R * q, cy + R * q)),
                                          fill=rgba(ACCENT, 255))
                base.alpha_composite(l)
                self.ripple(base, cx, cy, q, rmax=R * 2.6)
            else:
                self.dots(base, items)
            return self.finish(base)

        # ---------------- dot expands into the viewport --------------------
        # The merged dot stays small and fades out fast while a paper card
        # blooms out of the same centre. Previously the whole growing rounded
        # rect was filled with orange until p=0.7, which read as a big flat
        # orange square for ~0.5s before any UI appeared.
        if t < T_EXPAND:
            p = phase(t, T_MERGE, T_EXPAND)
            # Cross-fade the dot into the card with *complementary* alphas so
            # there is never a blank frame, and reach full window size before
            # the UI is drawn (the UI is laid out at self.WIN, not at `win`).
            k = smooth(clamp01(p / 0.30))          # dot -> card
            grow = smooth(clamp01(p / 0.55))       # card reaches self.WIN here
            win = mix_rect((cx - R, cy - R, cx + R, cy + R), self.WIN, grow)
            radius = lerp(R, 24, grow)

            dot_a = int(255 * (1 - k))
            if dot_a > 0:
                l = self.layer()
                ImageDraw.Draw(l).ellipse(bx((cx - R, cy - R, cx + R, cy + R)),
                                          fill=rgba(ACCENT, dot_a))
                base.alpha_composite(l)

            card_a = int(255 * k)
            if card_a > 0:
                l = self.layer()
                self.rrect(l, win, radius, fill=rgba(CARD, card_a),
                           outline=rgba(LINE, card_a), w=1)
                base.alpha_composite(l)

            # a single expanding accent ring carries the dot's energy into the
            # growing card, so the bloom beat is not a dead white rectangle
            self.ripple(base, cx, cy, clamp01(p / 0.62), rmax=R * 4.2)

            if p > 0.50:
                a = int(255 * smooth((p - 0.50) / 0.50))
                sh = self.win_shadow.copy()   # never mutate the cached sprite
                sh.putalpha(ImageChops.multiply(sh.getchannel("A"),
                                                Image.new("L", self.SZ, a)))
                base.alpha_composite(sh)
                self.ui(base, t, self.WIN, opacity=a)
            return self.finish(base)

        # ---------------- product story ------------------------------------
        if t < T_MORPH:
            base.alpha_composite(self.win_shadow)
            scroll = 88.0 * out_cubic(phase(t, T_FEED - 0.05, T_FEED + 0.55))
            post_p = phase(t, T_EXPAND + 0.35, T_EXPAND + 1.05)
            post_clicked = t >= T_EXPAND + 1.30
            liked = t >= T_LIKE - 0.72
            like_p = phase(t, T_FEED + 0.15, T_LIKE - 0.72)
            comment_sent = t >= 8.72
            comment_p = phase(t, 8.55, 8.95)
            push = 44.0 * smooth(phase(t, 7.62, 8.15))

            # cursor choreography
            x0, y0, x3, y3 = self.WIN
            post_btn = (x3 - 63, y0 + 130)
            heart_pos = (x0 + 34, y0 + 92 + 72 - 0)   # approx, scrolled card 1
            heart_pos = (x0 + 34, y0 + 182 - 88 + 72)
            bubble_pos = (x0 + 92, heart_pos[1])
            away = (x3 - 34, y0 + 300)
            send = (x3 - 40, y3 - 33)

            cursor = None
            cp = 0.0
            press = 0.0
            if t < T_POST:
                q = phase(t, T_EXPAND, T_POST)
                if q < 0.72:
                    x, y = ease_path([(x3 + 90, y3 + 70), (x3 - 10, y0 + 300),
                                      post_btn], q / 0.72)
                else:
                    x, y = post_btn
                press = 0.85 * (1 - abs((q - 0.76) / 0.10)) if 0.66 < q < 0.86 else 0.0
                cp = phase(t, T_EXPAND + 1.30, T_EXPAND + 1.60)
                cursor = (x, y, max(0.0, press))
            elif t < T_FEED + 0.15:
                q = phase(t, T_POST, T_FEED + 0.15)
                x, y = ease_path([post_btn, (x3 - 30, y0 + 260), away], q)
                cursor = (x, y, 0.0)
            elif t < T_LIKE:
                q = phase(t, T_FEED + 0.15, T_LIKE)
                if q < 0.62:
                    x, y = ease_path([away, (x0 + 150, y0 + 230), heart_pos], q / 0.62)
                else:
                    x, y = heart_pos
                press = 0.85 * (1 - abs((q - 0.66) / 0.10)) if 0.56 < q < 0.76 else 0.0
                cp = phase(t, T_LIKE - 0.72, T_LIKE - 0.42)
                cursor = (x, y, max(0.0, press))
            elif t < T_COMMENT:
                q = phase(t, T_LIKE, T_COMMENT)
                if q < 0.20:
                    x, y = ease_path([heart_pos, bubble_pos], q / 0.20)
                    cp = phase(t, T_LIKE + 0.10, T_LIKE + 0.34)
                elif q < 0.42:
                    x, y = ease_path([bubble_pos, away], (q - 0.20) / 0.22)
                elif q < 0.72:
                    x, y = away
                else:
                    x, y = ease_path([away, send], (q - 0.72) / 0.28)
                    cp = phase(t, 8.55, 8.82)
                press = 0.8 * (1 - abs((q - 0.16) / 0.08)) if 0.08 < q < 0.24 else 0.0
                cursor = (x, y, max(0.0, press))
            else:
                q = phase(t, T_COMMENT, T_MORPH)
                x, y = ease_path([send, (x3 + 70, y3 + 40)], q)
                cursor = (x, y, 0.0)

            self.ui(base, t, self.WIN, scroll=scroll, post_p=post_p,
                    post_clicked=post_clicked, like_p=like_p, liked=liked,
                    comment_p=comment_p, push=push, comment_sent=comment_sent,
                    cursor=cursor, click_p=cp if 0 < cp < 1 else 0.0)
            return self.finish(base)

        # ---------------- window animates into the reel --------------------
        # The product window shrinks to the reel's 16:9 box and fades while the
        # reel cross-fades in, already running from its own frame 0. Tying idx
        # to (t - T_MORPH) keeps the reel at native speed and lands exactly on
        # frame 179 at T_REEL, so the following merge beat continues seamlessly.
        # (The old guard `if t < 9.8` was dead code here: this branch only runs
        # for t >= T_MORPH == 9.8, so the morph never played — a hard cut.)
        if t < T_REEL:
            idx = int((t - T_MORPH) * FPS)
            if t < T_MORPH_END:
                m = phase(t, T_MORPH, T_MORPH_END)
                f = smooth(m)
                b = mix_rect(self.WIN, self.RB, out_cubic(m))
                ui_a = int(255 * (1 - f))
                if ui_a > 0:
                    sh = self.win_shadow.copy()
                    sh.putalpha(ImageChops.multiply(sh.getchannel("A"),
                                                    Image.new("L", self.SZ, ui_a)))
                    base.alpha_composite(sh)
                    self.ui(base, t, b, opacity=ui_a, scroll=88.0, post_p=1.0,
                            post_clicked=True, liked=True, comment_p=1.0,
                            push=44.0, comment_sent=True)
                if f > 0:
                    base.alpha_composite(self.reel_frame(idx, self.RB, int(255 * f)))
            else:
                base.alpha_composite(self.reel_frame(idx, self.RB))
            return self.finish(base)

        # ---------------- reel's last 3 pips merge -------------------------
        if t < T_REEL_MERGE:
            p = phase(t, T_REEL, T_REEL_MERGE)
            fade = 1.0 - smooth(clamp01(p / 0.30))
            if fade > 0:
                fr = self.reel_frame(179, self.RB, int(255 * fade))
                base.alpha_composite(fr)
            # reel dot centres measured from reel_last.png
            rw, rh = 1280.0, 720.0
            rbw, rbh = self.RB[2] - self.RB[0], self.RB[3] - self.RB[1]
            src = []
            for rx, ry in [(516.3, 273.6), (767.6, 268.1), (639.0, 486.9)]:
                src.append((self.RB[0] + rx / rw * rbw, self.RB[1] + ry / rh * rbh))
            r0 = 63.8 * rbw / rw
            q = out_cubic(clamp01((p - 0.08) / 0.82))
            items = []
            for i, (sx, sy) in enumerate(src):
                qq = out_cubic(clamp01((q - i * 0.05) / 0.82))
                items.append((lerp(sx, cx, qq), lerp(sy, cy, qq),
                              lerp(r0, R * 0.95, qq), 255, False))
            if q > 0.80:
                f = smooth((q - 0.80) / 0.20)
                for i, (x, y, r, a, g) in enumerate(items):
                    items[i] = (x, y, r, int(255 * (1 - f)), g)
                self.dots(base, items)
                l = self.layer()
                ImageDraw.Draw(l).ellipse(bx((cx - R * f, cy - R * f,
                                              cx + R * f, cy + R * f)),
                                          fill=rgba(ACCENT))
                base.alpha_composite(l)
                self.ripple(base, cx, cy, f, rmax=R * 2.6)
            else:
                self.dots(base, items)
            return self.finish(base)

        # ---------------- dot un-merges into 3 pips ------------------------
        # The merged dot IS the three pips stacked at the same centre. The old
        # version drew a separate full-opacity centre disc for the whole beat
        # ON TOP OF the three growing pips, so the mark read as FOUR dots
        # (17.3s-17.7s) until that disc abruptly vanished at T_UNMERGE. Now
        # all three pips start at the centre at full size/opacity; at p=0 the
        # coincident discs are exactly one dot, at p=1 they are the triangle.
        # Mass is conserved and a fourth dot can never exist.
        if t < T_UNMERGE:
            p = phase(t, T_REEL_MERGE, T_UNMERGE)
            target = tri_at(-OMEGA * (DUR - T_UNMERGE))
            items = []
            for i, (tx, ty) in enumerate(target):
                q = out_back(clamp01((p - i * 0.07) / 0.78))
                items.append((lerp(cx, tx, q), lerp(cy, ty, q), R, 255, False))
            self.dots(base, items)
            self.ripple(base, cx, cy, phase(t, T_REEL_MERGE, T_REEL_MERGE + 0.5),
                        rmax=R * 2.2)
            return self.finish(base)

        # ---------------- rotation (second half) ---------------------------
        th = theta(t)
        items = []
        for k in range(4, 0, -1):
            for px, py in tri_at(th - k * 0.055):
                items.append((px, py, R * (1 - 0.035 * k), 26 - 4 * k, True))
        for px, py in tri_at(th):
            items.append((px, py, R, 255, False))
        self.dots(base, items)
        return self.finish(base)

    def finish(self, base):
        return base.convert("RGB").resize((self.W, self.H), Image.LANCZOS)


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------
def prepare_reel_frames():
    # guard on f000 specifically — a stale f001..f180 extraction must be redone
    if (os.path.isfile(os.path.join(REEL_FRAMES, "f000.png"))
            and os.path.isfile(os.path.join(REEL_FRAMES, "f179.png"))
            and len(os.listdir(REEL_FRAMES)) >= 180):
        return
    shutil.rmtree(REEL_FRAMES, ignore_errors=True)
    os.makedirs(REEL_FRAMES, exist_ok=True)
    # -start_number 0 keeps the extracted names aligned with reel_frame(idx),
    # which reads idx 0..179. Without it ffmpeg emits f001..f180: f000 goes
    # missing (blank first reel frame) and the real last frame is never shown.
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", REEL,
                    "-start_number", "0", "-vsync", "0",
                    os.path.join(REEL_FRAMES, "f%03d.png")], check=True)


def encode(scene, frames_dir, out, poster, bitrate):
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f%04d.png"),
        "-c:v", "libopenh264", "-b:v", bitrate, "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart", out
    ], check=True)
    Image.open(os.path.join(frames_dir, "f0000.png")).convert("RGB").save(
        poster, quality=92, subsampling=0)
    print("  encoded %s  %d frames  %.1fs  %.2f MB" %
          (out, N, DUR, os.path.getsize(out) / 1e6))


def main():
    prepare_reel_frames()
    scenes = [
        Scene("desktop", 1600, 904, 469, 457, 81,
              [(310.1, 367.0), (629.9, 362.0), (466.1, 642.9)],
              (139, 207, 799, 707), (139, 271, 799, 642), "2600k"),
        # Portrait: object-fit cover on a ~390px phone only shows source
        # x=77..643 (and 83..636 on a 360px phone), with the nav pill over the
        # top ~100 source px and the headline starting around source y=575.
        # Keep the window/reel inside x=105..615 and y=118..520 so no edge,
        # shadow or Post button is cropped and the header clears the nav pill.
        Scene("portrait", 720, 1280, 366, 280, 75,
              [(218.9, 196.9), (515.1, 191.9), (363.0, 452.1)],
              (105, 118, 615, 520), (105, 150, 615, 437), "2000k"),
    ]
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    for scene in scenes:
        if only not in ("all", scene.name):
            continue
        d = os.path.join(FRAME_DIR, scene.name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        print("rendering %s  %dx%d  %d frames ..." % (scene.name, scene.W, scene.H, N))
        for i in range(N):
            im = scene.render(i / FPS)
            im.save(os.path.join(d, "f%04d.png" % i), compress_level=2)
            if i % 60 == 0:
                print("   %3d/%d" % (i, N), flush=True)
        out = os.path.join(PUBLIC, "pips-story.mp4" if scene.name == "desktop"
                           else "pips-story-portrait.mp4")
        poster = os.path.join(PUBLIC, "pips-story-poster.jpg" if scene.name == "desktop"
                              else "pips-story-portrait-poster.jpg")
        encode(scene, d, out, poster, scene.bitrate)
    print("DONE")


if __name__ == "__main__":
    main()
