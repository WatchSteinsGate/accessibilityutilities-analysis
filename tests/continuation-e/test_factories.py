"""Read-only factory composition. Real ObjC/libdispatch and Menu init are modeled."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-e'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from emulator import *
from collections import namedtuple
Work=namedtuple('Work','address args prefix complete')
class YieldingE(E):
 def hook(self,u,a,size,data):
  self.visited.add(a)
  if a in self.stops:self.hit=a;u.emu_stop();return
  if a in self.calls:
   work=self.calls[a](self)
   if isinstance(work,Work):self.pending=work;self.hit=a;u.emu_stop();return
   u.reg_write(R.UC_ARM64_REG_PC,self.get(30));return
  if a in IMPORTS:raise AssertionError(('Unmodeled import',IMPORTS[a],hex(a)))
MASK=(1<<64)-1;OBJ=0x20011000;ARRAY=0x20012000;CHILD=0x20013000;SCREEN=0x20014000;COLOR=0x20015000
CONFIG={
 'DrawWindow':(0x10ab0,0x10b68,0x10bc4,0x10104b0,0x10104a8,0x1011a18),
 'FloatView':(0x122e38,0x122ef0,0x122fd8,0x1010c28,0x1010c20,0x1011be0),
 'FieldView':(0x608170,0x6081f0,0x6082ec,0x1010dd0,0x1010dc8,None),
 'MenuWindow':(0x616f5c,0x617014,0x617070,0x1011310,0x1011308,None)}

def putq(e,a,v):e.write(a,struct.pack('<Q',v))
class Model:
 def __init__(self,image,role,fault='none',child=True):
  self.e=YieldingE(image);self.e.ownership();self.role=role;self.fault=fault;self.child=child;self.depth=0
  self.allocations=0;self.initializations=0;self.once=[];self.ui=[];self.supers=[];self.controls=[]
  for a,name in IMPORTS.items():
   if name=='_objc_msgSend':self.e.calls[a]=self.message
   elif name=='_objc_msgSendSuper2':self.e.calls[a]=self.super_message
   elif name=='_objc_alloc':self.e.calls[a]=self.allocate
   elif name=='_dispatch_once':self.e.calls[a]=self.once_boundary
  for _,cfg in CONFIG.items():
   putq(self.e,cfg[3],0);putq(self.e,cfg[4],0)
   if cfg[5]:putq(self.e,cfg[5],0)
 def nested(self,address,args=(),prefix=False):
  e=self.e;context=e.u.context_save();stops=e.stops.copy();hit=e.hit;self.depth+=1
  try:
   e.pending=None
   result=e.run(address,args,stops=[0x10c2c] if prefix else [],stack_pointer=SP-self.depth*0x7000)
   while e.pending is not None:
    work=e.pending;e.pending=None
    result=self.nested(work.address,work.args,work.prefix)
    if work.complete is not None:work.complete()
    e.set(0,result);e.hit=None
    e.u.emu_start(e.get(30),STOP+4,count=100000)
    assert e.hit is not None,'resumed instruction bound exhausted'
   result=e.get(0)
   if prefix:
    assert e.hit==0x10c2c;result=e.q(e.get(29)-8)
  finally:
   self.depth-=1;e.u.context_restore(context);e.stops=stops;e.hit=hit
  return result
 def allocate(self,e):
  self.allocations+=1;e.set(0,0 if self.fault=='allocation_nil' else OBJ)
 def super_message(self,e):
  receiver=e.q(e.get(0));sel=e.cs(e.get(1));self.supers.append(sel)
  assert sel in ('init','initWithFrame:')
  e.set(0,0 if self.fault=='super_nil' else receiver)
 def once_boundary(self,e):
  token,block=e.get(0),e.get(1);invoke=e.q(block+16)
  assert token==CONFIG[self.role][3] and invoke==CONFIG[self.role][1]
  self.once.append(hex(invoke));return Work(invoke,[(0,block)],False,lambda:putq(e,token,MASK))
 def message(self,e):
  receiver=e.get(0);sel=e.cs(e.get(1))
  if not receiver:e.set(0,0);return
  if sel in ('init:','initWithFrame::','initWithFrame:'):
   self.initializations+=1;self.controls.append(hex(e.get(2)))
   if self.role=='MenuWindow':result=0 if self.fault=='super_nil' else receiver
   else:return Work(CONFIG[self.role][2],(),self.role=='DrawWindow',None)
   e.set(0,result)
  elif sel=='mainScreen':e.set(0,SCREEN)
  elif sel=='bounds':
   for i,v in enumerate([0.,0.,320.,240.]):e.u.reg_write(getattr(R,'UC_ARM64_REG_D'+str(i)),struct.unpack('<Q',struct.pack('<d',v))[0])
  elif sel=='subviews':e.set(0,ARRAY)
  elif sel=='lastObject':e.set(0,CHILD if self.child else 0)
  elif sel=='clearColor':e.set(0,COLOR)
  elif sel in ('setSecureTextEntry:','setUserInteractionEnabled:','setBackgroundColor:'):
   self.ui.append(dict(selector=sel,arg=hex(e.get(2))))
  else:raise AssertionError(('Unexpected selector',self.role,sel))
 def snapshot(self):
  cfg=CONFIG[self.role]
  return dict(allocations=self.allocations,initializer_calls=self.initializations,once_invokes=self.once,super_selectors=self.supers,ui_messages=self.ui,published_control=hex(self.e.q(cfg[5])) if cfg[5] else None,native_initializer_scope={'DrawWindow':'through control store; remainder skipped','FloatView':'full normal/nil-return body','FieldView':'full normal/nil-return body','MenuWindow':'entire initializer modeled'}[self.role])

rows=[]
for build,image in [('original',O),('r03',P)]:
 for role,cfg in CONFIG.items():
  for fault in ['none','allocation_nil','super_nil']:
   model=Model(image,role,fault);returned=[]
   for control in [0x20021000,0x20022000,0x20023000]:
    returned.append(model.nested(cfg[0],[(0,0x20030000),(1,0),(2,control)]))
   expected=OBJ if fault=='none' else 0
   assert returned==[expected]*3 and model.allocations==1
   assert model.initializations==(0 if fault=='allocation_nil' else 1)
   assert model.e.q(cfg[3])==MASK and model.e.q(cfg[4])==expected and len(model.once)==1
   if cfg[5]:assert model.e.q(cfg[5])==(0 if fault=='allocation_nil' else 0x20021000)
   if role=='FieldView' and fault!='none':assert not model.ui
   rows.append(dict(test='factorySequentialReuse',build=build,role=role,fault=fault,changed_control_arguments=True,returns=[hex(v) for v in returned],**model.snapshot()))
 for role in ['FloatView','DrawWindow']:
  for control in [0,0x20021000]:
   for super_nil in [False,True]:
    model=Model(image,role,'super_nil' if super_nil else 'none');model.e.set(0,OBJ);model.e.set(2,control)
    result=model.nested(CONFIG[role][2],prefix=role=='DrawWindow')
    assert result==(0 if super_nil else OBJ) and model.e.q(CONFIG[role][5])==control
    rows.append(dict(test='initializerControlPublication',build=build,role=role,control=hex(control),super_nil=super_nil,returned=hex(result),**model.snapshot()))
 for super_nil in [False,True]:
  for child in [False,True]:
   model=Model(image,'FieldView','super_nil' if super_nil else 'none',child);model.e.set(0,OBJ)
   result=model.nested(CONFIG['FieldView'][2])
   assert result==(0 if super_nil else OBJ)
   if super_nil:assert model.ui==[]
   else:assert [x['selector'] for x in model.ui]==(['setSecureTextEntry:','setBackgroundColor:','setUserInteractionEnabled:'] if not child else ['setSecureTextEntry:','setUserInteractionEnabled:','setBackgroundColor:','setUserInteractionEnabled:'])
   rows.append(dict(test='fieldInitializer',build=build,super_nil=super_nil,backing_child_available=child,returned=hex(result),**model.snapshot()))
# Execute only the control-state construction/publication excerpt, not its
# enclosing worker/backend. Existing-slot reuse is sequential, not race proof.
for build,image in [('original',O),('r03',P)]:
 for existing in [0,0x20041000,0x20042000]:
  e=E(image);allocations=[];subobjects=[];heap=0x20043000
  putq(e,0x1011b68,existing)
  for address in [heap,0x20041000,0x20042000]:e.write(address,b'\xa5'*256)
  def allocate_state(e):
   assert e.get(0)==256;allocations.append(256);e.set(0,heap)
  e.calls[0x875fdc]=allocate_state
  for address in [0x1771c,0x16a58]:
   e.calls[address]=lambda e:subobjects.append(hex(e.get(0)-heap))
  def zero(e):
   assert e.get(1)==0 and e.get(2)==0x28 and e.get(0)==heap+0xa8
   e.write(e.get(0),bytes(e.get(2)))
  e.calls[0x8764f8]=zero
  for _ in range(2):e.run(0x70e68,stops=[0x71008])
  assert e.q(0x1011b68)==(existing or heap)
  assert allocations==([] if existing else [256])
  if existing:
   assert bytes(e.u.mem_read(existing,256))==b'\xa5'*256 and subobjects==[]
  else:
   assert len(subobjects)==4 and e.byte(heap)==0 and e.byte(heap+0xd0)==0
   assert bytes(e.u.mem_read(heap+0xd4,0x28))==bytes(0x28)
   assert 0x1037b8 in e.visited and 0x1037a8 in e.visited
  rows.append(dict(test='controlStateProducerExcerpt',build=build,initial_slot=hex(existing),published=hex(e.q(0x1011b68)),sequential_calls=2,allocation_sizes=allocations,subobject_boundaries=subobjects,allocation_import='__Znwm',whole_producer_executed=False))
assert len(rows)==54
# Equality checks cover only the tested factory/once/init ranges, not all downstream callees.
ranges=[(cfg[0],O.bounds(cfg[0])[1]) for cfg in CONFIG.values()]+[(cfg[1],O.bounds(cfg[1])[1]) for cfg in CONFIG.values()]+[(0x122fd8,0x12309c),(0x6082ec,0x608534),(0x10bc4,0x10c2c),(0x70e68,0x70fb8),(0x1037a8,0x1037c8)]
equality=[]
for lo,hi in ranges:
 a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo)
 if lo!=0x70e68:assert a==b
 else:assert a!=b
 equality.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
result=dict(passed=True,cases=len(rows),scope='54 paired-build native/model cases: four native singleton factories and once blocks, full FloatView/FieldView initializer bodies, DrawWindow prefix through control publication. dispatch_once execution/completion, allocation, inherited init, ARC, UIKit properties and screen geometry modeled; DrawWindow remainder skipped, MenuWindow initializer fully modeled. Control-state producer is only a bounded construction/publication excerpt with modeled allocation and four subobject construction boundaries; enclosing producer/backend not executed. No real queue delivery, reentry, lifetime/race proof, backend/device execution or performance measurement.',code_equality=equality,records=rows)
(RESULTS/'factory-tests.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print(json.dumps(dict(passed=True,cases=len(rows),compared_ranges=len(equality),equal_ranges=sum(r['equal'] for r in equality),runtime='modeled ObjC/once; no device run')))
