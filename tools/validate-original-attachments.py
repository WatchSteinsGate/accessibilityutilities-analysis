"""Validate publication metadata and optionally downloaded original bytes."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--directory', type=Path, help='Directory containing all eleven downloaded original files')
args = parser.parse_args()
manifest = json.loads((ROOT / 'results/source-attachments/2026-10-31-original-files.json').read_text())
items = manifest['files']
assert manifest['format'] == 'original-attachment-release-publication-v1'
assert len(items) == manifest['attachment_occurrences'] == 11
assert sum(v['name'].endswith('.zip') for v in items) == manifest['zip_files'] == 9
assert len(items) - manifest['zip_files'] == manifest['text_files'] == 2
assert len({v['sha256'] for v in items}) == manifest['unique_sha256'] == 10
source = {v['name']: v for v in json.loads((ROOT / manifest['source_intake']).read_text())['attachments']}
assert set(source) == {v['name'] for v in items}
sums = {line.split('  ', 1)[1]: line.split('  ', 1)[0] for line in (ROOT / 'archives/2026-10-31/SHA256SUMS').read_text().splitlines()}
for item in items:
    assert item['name'] == Path(item['name']).name
    assert item['size'] == source[item['name']]['size']
    assert item['sha256'] == source[item['name']]['sha256'] == sums[item['name']]
    assert item['github_digest'] == 'sha256:' + item['sha256']
    assert item['state'] == 'uploaded' and item['asset_id'] > 0
    assert item['download_url'].startswith('https://github.com/WatchSteinsGate/accessibilityutilities-analysis/releases/download/')
    if args.directory:
        data = (args.directory / item['name']).read_bytes()
        assert len(data) == item['size'], item['name']
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['name']
assert set(sums) == {v['name'] for v in items}
print('Publication metadata verified: 11 unchanged originals, 9 ZIPs, 2 text files, 10 unique identities.')
if args.directory:
    print('All eleven local original byte streams also verified; no archive members executed.')
else:
    print('Add --directory to verify downloaded bytes; this check alone does not refetch live release assets.')
