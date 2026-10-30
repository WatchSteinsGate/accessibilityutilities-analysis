"""Bounded static metadata only; emits no raw instruction windows or binaries."""
from pathlib import Path
import sys,os,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-c'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from native import *
ranges=[('observerInitialization',0x7aa4c,0x7b0b8),('notificationAndCoalescingCallbacks',0x7b77c,0x7b9a4),('reevaluationCallback',0x7ba04,0x7bae0),('resumeMutatorComparison',0x7b9a4,0x7ba04),('resignCallback',0x7b114,0x7b188),('producerQueueLoadExcerpt',0x70d00,0x70d38),('producerBlockConstructionExcerpt',0x7413c,0x7419c)]
equality=[]
for name,lo,hi in ranges:
 a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo)
 equality.append(dict(role=name,start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
assert all(row['equal'] for row in equality if row['role']!='resumeMutatorComparison')
assert next(row for row in equality if row['role']=='resumeMutatorComparison')['equal'] is False
# Direct immediate B/BL only; no pointer/indirect-call completeness claim.
targets={0x7b188:'lifecycleTransition',0x7b0b8:'suspendMutator',0x7b9a4:'resumeMutator',0x7b8d0:'coalescingEnqueue'}
callers=[];callback_calls=[]
text=next(s for s in sections(O) if s['name']=='__text' and s['seg']=='__TEXT')
for off in range(0,text['size']-3,4):
 pc=text['va']+off;word=struct.unpack('<I',O.bytes(pc,4))[0]
 if (word&0x7c000000)!=0x14000000:continue
 imm=word&0x3ffffff
 if imm&(1<<25):imm-=1<<26
 target=pc+imm*4;kind='BL' if word&0x80000000 else 'B'
 if target in targets:
  lo,hi=O.bounds(pc)
  callers.append(dict(site=hex(pc),kind=kind,target=hex(target),role=targets[target],containing_function=hex(lo),function_end=hex(hi) if hi else None))
 if 0x76944<=pc<0x76e20:
  callback_calls.append(dict(site=hex(pc),kind=kind,target=hex(target),direct_import=IMPORTS.get(target)))
# Resolve import pointer slots through the indirect symbol table, not raw class pointers.
for cmd,off,size in O.commands:
 if cmd==0xb:indoff,nind=struct.unpack_from('<II',O.b,off+56)
roles={}
for s in sections(O):
 if s['flags']&255 not in [6,7]:continue
 for i in range(s['size']//8):
  si=struct.unpack_from('<I',O.b,indoff+4*(s['r1']+i))[0]
  if si<len(SYMS):
   addr=s['va']+8*i
   if addr in [0xfd82e8,0xff08f0,0xff0910,0xff08e0,0xff0988,0xfd80c8,0xfd80d8,0xfd80e0,0xfd80e8,0xfd8108,0xfd8110,0xfd8118,0xfd8120]:roles[hex(addr)]=SYMS[si][0]
result=dict(scope='Original __text aligned direct B/BL target index plus specified original/R03 code-range equality and relevant imported pointer roles. Excludes indirect calls, runtime delivery and unknown callback callees. Constructor direct-call index is a scoped body inspection, not transitive absence of reentry.',code_equality=equality,import_pointer_roles=roles,lifecycle_direct_callers=callers,constructor_direct_branches=callback_calls)
(RESULTS/'scheduling-map.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(compared_ranges=len(equality),equal_ranges=sum(row['equal'] for row in equality),lifecycle_direct_callers=callers,import_pointer_roles=roles),indent=2))
