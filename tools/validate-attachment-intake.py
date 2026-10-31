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

# The later reattachment batch is separate: historical counts above stay unchanged.
current=json.loads((ROOT/'results/source-attachments/2026-10-31-intake.json').read_text())
newitems=current['attachments']
assert current['format']=='attachment-intake-v2'
assert len(newitems)==current['attachment_occurrences']==11
assert len({v['sha256'] for v in newitems})==current['unique_sha256']==10
oldhash={v['sha256'] for v in items}
seen=[v for v in newitems if v['sha256'] in oldhash]
assert len(seen)==current['previously_recorded_occurrences']==8
assert len({v['sha256'] for v in seen})==current['previously_recorded_unique_sha256']==7
assert len({v['sha256'] for v in newitems}-oldhash)==current['new_unique_sha256']==3
assert sum(v['sha256']=='e5091be0d1bd5ae339f93e99ef32e62fee2f9d8dacd67fd12fcd07724ad4a79c' for v in newitems)==current['original_workpack_copies']==2
assert current['native_tests_run'] is False and current['opaque_archives_published'] is False
known={line.split('  ',1)[1] for line in (ROOT/'SHA256SUMS').read_text().splitlines()}
for v in newitems:
 assert len(v['sha256'])==64 and all(c in '0123456789abcdef' for c in v['sha256'])
 assert v['size']>0 and v['disposition'] and v['previously_recorded']==(v['sha256'] in oldhash)
 if v['name'].endswith('.zip'): assert v['archive_file_count']>0 and v['archive_crc_verified'] is True
 for name in v.get('repository_files',[]):
  assert (ROOT/name).exists() or name in known or any(p.startswith(name) for p in known),name
for derivative in current['retained_derivatives']:
 path=ROOT/derivative['path']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==derivative['sha256'],derivative['path']
assert next(v for v in newitems if v['name']=='Resize-layout-continuation.md')['sha256']==source['sha256']
for tag,expected in [('T01','a79b03662abf61ad49b92d9cbd770ac05bca9f41a78fe6e0b745424e6940b8d5'),('T02','792db0772e6cf6db488075d4495439ed9deb27698d955425d0c996865c4a7246')]:
 diagnostic=next(v for v in newitems if '-'+tag+'-' in v['name'])
 assert diagnostic['framework_sha256']==expected
 assert diagnostic['framework_matches_package_manifest'] is True
 assert diagnostic['package_declares_device_tested'] is False
 assert diagnostic['declared_baseline_sha256']=='eb87d6e69a031b6f2fbd4845d904dc9dc132468d1c24852b8384e0e12522e8d4'
print('2026-10-31: 11 occurrences, 10 identities; 8 reattachments, 3 new identities; both retained narrative hashes verified. No raw archive/binary presence claimed.')
