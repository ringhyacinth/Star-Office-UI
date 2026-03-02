#!/usr/bin/env python3
"""Convert an animated WebP to a horizontal spritesheet PNG.

Notes:
- Phaser's built-in loader doesn't support animated WebP directly.
- We convert frames into a spritesheet.
- Output: <name>-spritesheet.png
"""

import os
from PIL import Image


def webp_to_spritesheet(in_path: str, out_path: str, frame_w: int, frame_h: int, max_frames: int | None = None):
    im = Image.open(in_path)
    n = getattr(im, 'n_frames', 1)
    if max_frames:
        n = min(n, max_frames)

    sheet = Image.new('RGBA', (frame_w * n, frame_h), (0, 0, 0, 0))

    for i in range(n):
        im.seek(i)
        fr = im.convert('RGBA')
        if fr.size != (frame_w, frame_h):
            fr = fr.resize((frame_w, frame_h), Image.NEAREST)
        sheet.paste(fr, (i * frame_w, 0))

    sheet.save(out_path)
    return n


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('in_path')
    ap.add_argument('out_path')
    ap.add_argument('--w', type=int, required=True)
    ap.add_argument('--h', type=int, required=True)
    ap.add_argument('--max', type=int, default=None)
    args = ap.parse_args()

    n = webp_to_spritesheet(args.in_path, args.out_path, args.w, args.h, args.max)
    print(f"Wrote {args.out_path} with {n} frames")


if __name__ == '__main__':
    main()
