from pathlib import Path
import argparse, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'continuation-a':232,'continuation-b':210,'continuation-c':64,'continuation-d':58,'continuation-e':54,'continuation-f':46}
parser=argparse.ArgumentParser(description='Verify stored record integrity, not native execution.')
parser.add_argument('--group',choices=sorted(EXPECTED),help='Validate one group in a partial checkout; default requires all groups.')
args=parser.parse_args();groups=[args.group] if args.group else list(EXPECTED)
total=0
for group in groups:
 count=0
 for p in sorted((ROOT/'results/continuations'/group).glob('*-tests.json')):
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
  count+=len(records)
  print(p.relative_to(ROOT),len(records),'records verified')
 assert count==EXPECTED[group],(group,count,EXPECTED[group])
 total+=count
print(f'{total} continuation scoped records verified in {len(groups)} group(s); artifact integrity only, not a runtime rerun.')
