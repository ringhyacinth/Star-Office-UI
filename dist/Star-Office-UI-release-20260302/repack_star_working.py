#!/usr/bin/env python3
"""Repack star-working spritesheet into a grid to fit GPU max texture sizes.

Problem:
- Current spritesheet is 44160x144 (192 frames * 230w), too wide for WebGL max texture size on most GPUs.
- Result: texture upload fails => renders as black rectangle.

This script repacks frames into rows.
Default:
- frame: 230x144
- frames: 192
- cols: 35  -> width 8050
- rows: ceil(192/35)=6 -> height 864

Output:
- frontend/star-working-spritesheet-grid.png

Safe:
- does NOT delete original file.
"""

import math
import os
from PIL import Image

ROOT = "/root/.openclaw/workspace/star-office-ui"
IN_PATH = os.path.join(ROOT, "frontend", "star-working-spritesheet.png")
OUT_PATH = os.path.join(ROOT, "frontend", "star-working-spritesheet-grid.png")

FRAME_W = 230
FRAME_H = 144
FRAMES = 192
COLS = 35


def main():
    img = Image.open(IN_PATH).convert("RGBA")
    w, h = img.size

    expected_w = FRAME_W * FRAMES
    if h != FRAME_H or w < expected_w:
        raise SystemExit(f"Unexpected input size {img.size}, expected height={FRAME_H}, width>={expected_w}")

    rows = math.ceil(FRAMES / COLS)
    out_w = FRAME_W * COLS
    out_h = FRAME_H * rows

    out = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))

    for i in range(FRAMES):
        src_x0 = i * FRAME_W
        src_y0 = 0
        frame = img.crop((src_x0, src_y0, src_x0 + FRAME_W, src_y0 + FRAME_H))

        r = i // COLS
        c = i % COLS
        dst_x0 = c * FRAME_W
        dst_y0 = r * FRAME_H
        out.paste(frame, (dst_x0, dst_y0))

    out.save(OUT_PATH)

    orig_size = os.path.getsize(IN_PATH)
    new_size = os.path.getsize(OUT_PATH)
    print(f"Wrote: {OUT_PATH}")
    print(f"Input size: {w}x{h}  ({orig_size/1024/1024:.2f} MB)")
    print(f"Output size: {out_w}x{out_h} ({new_size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
