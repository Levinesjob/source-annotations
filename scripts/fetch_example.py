"""Download the pinned public example; verify its exact content hash."""
import hashlib
import json
from pathlib import Path
import urllib.request

root = Path(__file__).resolve().parents[1]
paper = json.loads((root/'examples/waypoint-opd/annotations.json').read_text(encoding='utf-8'))['paper']
target = root/'local/waypoint-opd-v1.pdf'
target.parent.mkdir(exist_ok=True)
if target.exists():
    data = target.read_bytes()
else:
    with urllib.request.urlopen(paper['pdf_url'], timeout=90) as response:
        data = response.read()
if hashlib.sha256(data).hexdigest() != paper['sha256']:
    raise SystemExit('Source hash mismatch; existing file was not overwritten. Verify v1 before continuing.')
target.write_bytes(data)
print('Verified example: local/waypoint-opd-v1.pdf')
