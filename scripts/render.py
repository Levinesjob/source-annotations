"""Render an annotated PDF to PNGs for visible review (does not certify content)."""
import argparse
from pathlib import Path
import pymupdf as fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdf')
parser.add_argument('directory')
parser.add_argument('--scale', type=float, default=1.5)
args = parser.parse_args()
if not 0.25 <= args.scale <= 4:
    parser.error('scale must be between 0.25 and 4')
out = Path(args.directory)
out.mkdir(parents=True, exist_ok=True)
with fitz.open(args.pdf) as doc:
    count = len(doc)
    for i, page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(args.scale,args.scale)).save(out/f'page-{i+1:02}.png')
print(f'Rendered {count} pages')
