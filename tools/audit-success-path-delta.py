"""Read-only original/R03 structural delta ledger; no patch bytes or builders emitted."""
from pathlib import Path
import os,sys,json,hashlib,struct,bisect,zipfile,argparse,collections
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/continuation-b'));from native import *
p=argparse.ArgumentParser();p.add_argument('--r03-archive',type=Path,required=True);p.add_argument('--out',type=Path,default=ROOT/'results/generated/success-path-audit');a=p.parse_args()
EXPECTED_ZIP='dc887be38e6753c3a5316149e2a0b74463a850a4929df7f9cc59a93c962ed583'
assert hashlib.sha256(a.r03_archive.read_bytes()).hexdigest()==EXPECTED_ZIP
z=zipfile.ZipFile(a.r03_archive);manifest_raw=z.read('manifest.json');manifest=json.loads(manifest_raw)
assert manifest['output_sha256']==hashlib.sha256(P.b).hexdigest()
delta=json.loads(z.read('delta.json'));header_size=len(bytes.fromhex(delta['original_header_hex']))
assert P.b[:header_size]==bytes.fromhex(delta['new_header_hex'])
old_link=next(v for v in O.segments if v[0]=='__LINKEDIT');new_link=next(v for v in P.segments if v[0]=='__LINKEDIT')
olb=O.b[old_link[3]:old_link[3]+old_link[4]];nlb=P.b[new_link[3]:new_link[3]+new_link[4]]
# No source/build/apply member is executed or imported.
orig_sections=sections(O);patched_sections=sections(P)
methods=collections.defaultdict(list)
for m in objc_methods(O):methods[m['address']].append(dict(cls=m['cls'],selector=m['selector'],kind=m['kind']))
symbols_by_address=collections.defaultdict(list)
for name,addr,typ in SYMS:
 if addr and name:symbols_by_address[addr].append(name)
def entry_kind(image,start):
 ins=next(iter(md.disasm_lite(image.bytes(start,4),start)),None)
 if ins is None:return 'undecoded'
 if ins[2]=='ret':return 'immediate_return'
 if ins[2]=='b':return 'direct_branch'
 return 'other'
changed={};section_counts=[]
for s in orig_sections:
 try:old=O.bytes(s['va'],s['size']);new=P.bytes(s['va'],s['size'])
 except ValueError:continue
 count=sum(x!=y for x,y in zip(old,new))
 if count:section_counts.append(dict(segment=s['seg'],section=s['name'],start=hex(s['va']),size=s['size'],changed_bytes=count))
 if s['name']!='__text' or not s['flags']&0x80000000:continue
 starts=[f for f in O.starts if s['va']<=f<s['va']+s['size']]
 for i,f in enumerate(starts):
  end=starts[i+1] if i+1<len(starts) else s['va']+s['size']
  x,y=old[f-s['va']:end-s['va']],new[f-s['va']:end-s['va']]
  n=sum(u!=v for u,v in zip(x,y))
  if n:changed[f]=dict(entry=hex(f),end_exclusive=hex(end),size=end-f,changed_bytes=n,original_entry_kind=entry_kind(O,f),r03_entry_kind=entry_kind(P,f),original_sha256=hashlib.sha256(x).hexdigest(),r03_sha256=hashlib.sha256(y).hexdigest(),objc_methods=methods.get(f,[]),declared_delta_sites=[],necessity='unproven',preservation='requires original-path obligation review')
site_records=[]
for i,site in enumerate(manifest['patches'],1):
 address=site['address'];old=bytes.fromhex(site['old_hex']);new=bytes.fromhex(site['new_hex'])
 assert P.bytes(address,len(new))==new
 f,e=O.bounds(address)
 owner=changed.get(f) if e is not None and address<e else None
 if owner:owner['declared_delta_sites'].append(f'D{i:02d}')
 try:original_matches_declared_old=O.bytes(address,len(old))==old
 except ValueError:original_matches_declared_old=None
 site_records.append(dict(id=f'D{i:02d}',site=hex(address),length=len(new),patched_bytes_match_declared=True,supplied_original_matches_declared_baseline_site=original_matches_declared_old,changed_original_function=hex(f) if owner else None,role='local buffer initialization' if i>=4 else ['callback admission guard','late lifecycle render guard','journal/cache storage separation'][i-1],necessity_for_original_success='not demonstrated by declaration'))
functions=[]
for i,(f,row) in enumerate(sorted(changed.items()),1):
 row['id']=f'F{i:03d}';row['declaration_coverage']='contains declared incremental delta site' if row['declared_delta_sites'] else 'not individually explained by incremental manifest'
 functions.append(row)
roots=[]
for s in orig_sections:
 if s['name']=='__mod_init_func':
  for off in range(0,s['size'],8):
   entry=q(O,s['va']+off)
   roots.append(dict(slot=hex(s['va']+off),original_entry=hex(entry),r03_entry=hex(q(P,s['va']+off)),table_pointer_equal=q(P,s['va']+off)==entry,entry_in_changed_function=entry in changed,entry_kind_original=entry_kind(O,entry),entry_kind_r03=entry_kind(P,entry)))
code_regions=[]
for text,code in manifest['code'].items():
 start=int(text,16);b=bytes.fromhex(code);assert P.bytes(start,len(b))==b
 code_regions.append(dict(entry=text,declared_size=len(b),patched_region_matches=True,sha256=hashlib.sha256(b).hexdigest()))
extra=[dict(segment=s['seg'],section=s['name'],start=hex(s['va']),size=s['size']) for s in patched_sections if not any(t['seg']==s['seg'] and t['name']==s['name'] and t['va']==s['va'] for t in orig_sections)]
result=dict(scope='Read-only supplied-original versus R03 byte/function/section accounting and original initializer roots. Manifest is untrusted declaration verified against output, not necessity evidence. No original path completeness, dynamic targets, security/backend success or minimality proof. No patch bytes, apply recipes or source/build/archive code execution emitted.',input_sha256=dict(original=hashlib.sha256(O.b).hexdigest(),r03=hashlib.sha256(P.b).hexdigest()),declared_incremental_baseline_sha256=manifest['baseline_sha256'],declared_baseline_is_supplied_original=manifest['baseline_sha256']==hashlib.sha256(O.b).hexdigest(),archive_sha256=EXPECTED_ZIP,loader_accounting=dict(compared_prefix_bytes=header_size,changed_prefix_bytes=sum(x!=y for x,y in zip(O.b[:header_size],P.b[:header_size])),original_load_commands_end=32+struct.unpack_from('<I',O.b,20)[0],r03_load_commands_end=32+struct.unpack_from('<I',P.b,20)[0],declared_v58_old_header_matches_supplied_original=O.b[:header_size]==bytes.fromhex(delta['original_header_hex']),r03_declared_header_matches=True,file_size_increase=len(P.b)-len(O.b),linkedit_equal=olb==nlb,original_linkedit_sha256=hashlib.sha256(olb).hexdigest(),r03_linkedit_sha256=hashlib.sha256(nlb).hexdigest()),manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),changed_original_functions=functions,changed_shared_sections=section_counts,extra_or_relocated_sections=extra,declared_incremental_sites=site_records,declared_code_regions=code_regions,original_initializer_roots=roots,summary=dict(changed_original_functions=len(functions),changed_original_text_bytes=sum(r['changed_bytes'] for r in functions),changed_functions_with_incremental_sites=sum(bool(r['declared_delta_sites']) for r in functions),immediate_return_entries=[r['id'] for r in functions if r['r03_entry_kind']=='immediate_return' and r['original_entry_kind']!='immediate_return'],initializer_roots=len(roots),declared_sites=len(site_records),all_declared_output_sites_match=True))
assert len(functions)==63 and sum(r['changed_bytes'] for r in functions)==23444 and len(roots)==13 and len(site_records)==10
a.out.mkdir(parents=True,exist_ok=True);(a.out/'original-r03-delta-ledger.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['summary']))
for r in functions:
 print(r['id'],r['entry'],r['changed_bytes'],r['r03_entry_kind'],';'.join(m['cls']+' '+m['selector'] for m in r['objc_methods']) or '(unlabeled native function)',','.join(r['declared_delta_sites']))
print('original initializer pointers unchanged:',sum(r['table_pointer_equal'] for r in roots),'/',len(roots))
