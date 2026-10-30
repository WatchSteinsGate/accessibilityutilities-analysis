from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/source-attachments/2026-10-30-intake.json').read_text())
items=data['attachments']
assert len(items)==data['attachment_occurrences']==9
assert len({v['sha256'] for v in items})==data['unique_sha256']==7
assert len([v for v in items if v['sha256']=='e5091be0d1bd5ae339f93e99ef32e62fee2f9d8dacd67fd12fcd07724ad4a79c'])==data['original_workpack_copies']==3
source=next(v for v in items if v['name']=='Resize-layout-continuation.md')
p=ROOT/'docs/source-reports/Resize-layout-continuation.md'
assert p.stat().st_size==source['size']
assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']
archive=next(v for v in items if v['name']=='Resize-layout-continuation-evidence.zip')
assert archive['archived_report_sha256']==source['sha256']
for v in items:
 assert len(v['sha256'])==64 and v['size']>0 and v['disposition']
 for name in v.get('repository_files',[]): assert (ROOT/name).exists() or name in {line.split('  ',1)[1] for line in (ROOT/'SHA256SUMS').read_text().splitlines()} or any(line.split('  ',1)[1].startswith(name) for line in (ROOT/'SHA256SUMS').read_text().splitlines()),name
print('9 attachment occurrences, 7 unique identities, 3 identical original workpacks; exact source report verified. Omitted archives/binaries are not claimed present.')
