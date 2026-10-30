from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
total=0
for p in sorted((ROOT/'results/continuations').glob('*/*-tests.json')):
 data=json.loads(p.read_text())
 if data.get('recordFormat')=='partitioned-v1':
  records=[]
  for part in data['parts']:
   source=(p.parent/part['path']).resolve()
   assert source.is_relative_to((ROOT/'results/continuations').resolve())
   assert hashlib.sha256(source.read_bytes()).hexdigest()==part['sha256']
   rows=json.loads(source.read_text())['records'];assert len(rows)==part['records'];records.extend(rows)
 else:records=data['records']
 assert data['passed'] and len(records)==data['cases'],p
 total+=len(records)
 print(p.relative_to(ROOT),len(records),'records verified')
assert total==442,total
print('All 442 new scoped records verified; this is artifact integrity, not a runtime rerun.')
