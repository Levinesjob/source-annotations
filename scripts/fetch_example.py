"""Download the pinned public example; verify its exact content hash."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

root = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--example',choices=('waypoint-opd','attention-is-all-you-need'),default='waypoint-opd')
args=parser.parse_args()
paper = json.loads((root/'examples'/args.example/'annotations.json').read_text(encoding='utf-8'))['paper']
target = root/'local'/f'{args.example}-v1.pdf'
target.parent.mkdir(exist_ok=True)
if target.exists():
    data = target.read_bytes()
else:
    with urllib.request.urlopen(paper['pdf_url'], timeout=90) as response:
        data = response.read()
if hashlib.sha256(data).hexdigest() != paper['sha256']:
    raise SystemExit('Source hash mismatch; existing file was not overwritten. Verify v1 before continuing.')
target.write_bytes(data)
print('Verified example: '+target.relative_to(root).as_posix())
