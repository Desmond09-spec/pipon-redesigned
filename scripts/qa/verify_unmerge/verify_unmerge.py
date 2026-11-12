"""Verify the story hero shows exactly THREE pips through the un-merge beat."""
import subprocess
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

VIDEO = sys.argv[1] if len(sys.argv) > 1 else "/workspace/pipon/public/pips-story.mp4"
OUT = "/tmp/unmerge_final_" + os.path.basename(VIDEO).replace(".mp4", "")
TIMES = [16.9, 17.0, 17.1, 17.2, 17.3, 17.5, 17.7, 17.9, 18.5]
os.makedirs(OUT, exist_ok=True)


def orange_components(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    # solid accent pips: strong red, clearly above g/b
    mask = (r > 190) & (r - g > 90) & (r - b > 90)
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    big = int((sizes > 300).sum())
    return big, sorted([int(s) for s in sizes if s > 300], reverse=True)


rows = []
for t in TIMES:
    p = os.path.join(OUT, "t%.2f.png" % t)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", VIDEO,
                    "-frames:v", "1", p, "-y"], check=True)
    big, sizes = orange_components(p)
    rows.append((t, big, sizes[:5]))
    print("t=%5.2fs  components=%d  sizes=%s" % (t, big, sizes[:5]))

bad = [r for r in rows if r[0] >= 17.2 and r[0] < 17.9 and r[1] != 3]
print("\nRESULT:", "PASS - exactly three pips after split" if not bad else "FAIL %s" % bad)
sys.exit(1 if bad else 0)
