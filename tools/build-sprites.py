#!/usr/bin/env python3
"""
build-sprites.py — kemas frame sequence jadi sprite sheet untuk canvas scrub.

Pakai:
    1. Ekstrak frame dari video.

       WebM VP9 dengan alpha — WAJIB pakai -c:v libvpx-vp9. Decoder VP9 bawaan
       ffmpeg mengabaikan alpha dan menghasilkan frame opaque tanpa peringatan:
         ffmpeg -c:v libvpx-vp9 -i source.webm -vf "fps=30,scale=1440:-2" \
                -pix_fmt rgba -compression_level 1 png/f_%04d.png
         # lalu encode ke WebP (PIL/cwebp), pertahankan alpha

       MP4 tanpa alpha:
         ffmpeg -i source.mp4 -vf "fps=30,scale=1440:-2" \
                -c:v libwebp -quality 72 -compression_level 6 frames/frame_%04d.webp

    2. python3 build-sprites.py --src frames --out sprites

Output: sprites/starfall_sheet_N.webp + manifest.json
Nilai di manifest.json harus dicocokkan dengan CONFIG di starfall-embed.html.

Dependency: pip install pillow
"""

import argparse
import json
import math
import os
from PIL import Image


def build(src_dir, out_dir, cell_width, cols, rows, quality):
    frames = sorted(f for f in os.listdir(src_dir)
                    if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg')))
    if not frames:
        raise SystemExit(f'Tidak ada frame ditemukan di {src_dir}')

    os.makedirs(out_dir, exist_ok=True)

    first = Image.open(os.path.join(src_dir, frames[0]))
    cell_height = round(first.height * cell_width / first.width)
    per_sheet = cols * rows

    # Guard: batas ukuran canvas/tekstur browser
    if cell_width * cols > 8192 or cell_height * rows > 8192:
        raise SystemExit(
            f'Sheet akan berukuran {cell_width*cols}x{cell_height*rows} — '
            'melebihi batas aman 8192px. Kecilkan --cell-width atau --cols/--rows.'
        )

    sheet_count = math.ceil(len(frames) / per_sheet)
    total_bytes = 0

    for s in range(sheet_count):
        chunk = frames[s * per_sheet:(s + 1) * per_sheet]
        rows_needed = math.ceil(len(chunk) / cols)
        # RGBA + fully-transparent fill: source frames have an alpha channel and
        # flattening to RGB here would silently bake in a black background.
        sheet = Image.new('RGBA', (cell_width * cols, cell_height * rows_needed), (0, 0, 0, 0))

        for i, name in enumerate(chunk):
            img = Image.open(os.path.join(src_dir, name)).convert('RGBA')
            img = img.resize((cell_width, cell_height), Image.LANCZOS)
            sheet.paste(img, ((i % cols) * cell_width, (i // cols) * cell_height))

        path = os.path.join(out_dir, f'starfall_sheet_{s + 1}.webp')
        sheet.save(path, 'WEBP', quality=quality, alpha_quality=92, method=4)
        size = os.path.getsize(path)
        total_bytes += size
        print(f'  sheet {s + 1}/{sheet_count}  {sheet.size[0]}x{sheet.size[1]}  {size // 1024} KB')

    manifest = {
        'frameCount': len(frames),
        'cellWidth': cell_width,
        'cellHeight': cell_height,
        'cols': cols,
        'rows': rows,
        'perSheet': per_sheet,
        'sheets': sheet_count,
    }
    with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'\n{len(frames)} frame -> {sheet_count} sheet · total {total_bytes / 1048576:.1f} MB')
    print('\nSalin nilai ini ke CONFIG di starfall-embed.html:')
    print(f'  frameCount: {len(frames)},')
    print(f'  cellWidth:  {cell_width},')
    print(f'  cellHeight: {cell_height},')
    print(f'  cols:       {cols},')
    print(f'  perSheet:   {per_sheet},')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--src', default='frames', help='folder berisi frame')
    p.add_argument('--out', default='sprites', help='folder output')
    p.add_argument('--cell-width', type=int, default=960, help='lebar tiap frame di sheet')
    p.add_argument('--cols', type=int, default=5)
    p.add_argument('--rows', type=int, default=5)
    p.add_argument('--quality', type=int, default=76)
    a = p.parse_args()
    build(a.src, a.out, a.cell_width, a.cols, a.rows, a.quality)
