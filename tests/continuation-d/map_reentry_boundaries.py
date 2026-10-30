"""Reviewed native address/edge metadata only; no instruction dumps or binaries."""
from pathlib import Path
import sys, os, struct, json, hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-d'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from native import *

TARGETS={0x438b8:'registrationProducer',0xf6d50:'onceWrapperOuter',0xf6cf4:'onceWrapperBody',0x1077fc:'onceForwarderOuter',0x1077ec:'onceForwarderInner',0x7aa4c:'observerRegistrationInvoke',0x10791c:'suspendForwarderInner',0x10792c:'suspendForwarderOuter',0x107bf4:'transitionForwarderInner',0x107c08:'transitionForwarderOuter'}
RANGES=[('startupInitializer',0x43850,0x4388c),('startupCallbackAndProducer',0x4388c,0x438dc),('mainQueueGetterAndOnceHelpers',0xf6ccc,0xf6d60),('onceForwarders',0x1077ec,0x10780c),('suspendForwarders',0x10791c,0x10793c),('transitionForwarders',0x107bf4,0x107c1c),('constructorObjCForwarders',0x105cdc,0x105d5c),('rectangleHelper',0x76e20,0x76e6c),('startupBlock',0xfd99d0,0xfd99f0),('observerRegistrationBlock',0xfd9cd0,0xfd9cf0)]
comparison=[]
for role,lo,hi in RANGES:
 a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo)
 comparison.append(dict(role=role,start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
assert all(r['equal'] for r in comparison)
assert q(O,0xfd99e0)==q(P,0xfd99e0)==0x4388c
assert q(O,0xfd9ce0)==q(P,0xfd9ce0)==0x7aa4c
assert IMPORTS[0x876294]=='_dispatch_once' and IMPORTS[0x876258]=='_dispatch_async'
assert IMPORTS[0x876660]=='_objc_retainAutoreleaseReturnValue'

maps=[]
for build,image in [('original',O),('r03',P)]:
 text=next(s for s in sections(image) if s['name']=='__text' and s['seg']=='__TEXT')
 edges=[]
 for off in range(0,text['size']-3,4):
  pc=text['va']+off;word=struct.unpack('<I',image.bytes(pc,4))[0]
  if word&0x7c000000!=0x14000000:continue
  imm=word&0x3ffffff
  if imm&(1<<25):imm-=1<<26
  target=pc+imm*4
  if target in TARGETS:
   lo,hi=image.bounds(pc)
   edges.append(dict(site=hex(pc),kind='BL' if word&0x80000000 else 'B',target=hex(target),role=TARGETS[target],function_start=hex(lo),function_end_exclusive=hex(hi) if hi else None))
 init=next(s for s in sections(image) if s['name']=='__mod_init_func')
 slots=[hex(init['va']+i) for i in range(0,init['size'],8) if q(image,init['va']+i)==0x43850]
 assert len(slots)==1
 expected={(0x438a4,0x438b8),(0x438d0,0xf6d50),(0xf6d54,0xf6cf4),(0xf6d2c,0x1077fc),(0x107800,0x1077ec),(0x107930,0x10791c),(0x7b230,0x10792c),(0x107c10,0x107bf4),(0x7b820,0x107c08)}
 observed={(int(r['site'],16),int(r['target'],16)) for r in edges}
 assert observed==expected
 maps.append(dict(build=build,initializer_table_slots=slots,known_direct_edges=edges,observer_invoke_direct_callers=[]))

result=dict(scope='Two-build aligned immediate B/BL scan of __TEXT,__text, filtered to ten declared routing targets; exact known block descriptors, ten code/data equality windows and initializer-table membership. No indirect-call or other-state-writer completeness claim. Main-queue delivery and libdispatch contracts are external/model assumptions.',code_equality=comparison,routing_maps=maps,known_block_chain=[dict(block='0xfd99d0',invoke='0x4388c'),dict(block='0xfd9cd0',invoke='0x7aa4c')],main_dispatch_pointer_slot='0xfd82e8',once_token='0x1010a50',unresolved=['Indirect callers of blocks/registration helpers outside recovered startup route','Custom synchronous ObjC initializer/getter/setter implementations and UIKit reentry','Other lifecycle state writers and runtime swizzling','Control pointer global producer/owner lifetime beyond read at 0x1011b68'])
(RESULTS/'reentry-boundary-map.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(builds=len(maps),equal_ranges=len(comparison),direct_edges_per_build=[len(x['known_direct_edges']) for x in maps],startup_initializer='0x43850',startup_invoke='0x4388c',observer_registration_invoke='0x7aa4c'),indent=2))
