"""Reconstruct losslessly partitioned continuation-l static map; no native execution."""
from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parents[1]
p=root/'results/continuations/continuation-l/state-and-root-map.json'
d=json.loads(p.read_text()); assert d['recordFormat']=='static-map-parts-v1'
result=dict(scope=d['scope'], maps={})
result.update(d['otherFields'])
for build,part in d['maps'].items():
 source=(p.parent/part['path']).resolve()
 assert source.is_relative_to(p.parent.resolve())
 raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==part['sha256']
 result['maps'][build]=json.loads(raw)
canonical=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(canonical).hexdigest()==d['reconstructedCanonicalSha256']
print('Static map parts and full reconstructed canonical SHA256 verified; not native execution.')
