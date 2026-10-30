"""Native Overlay construction guards/properties and failed-once composition."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-g'))
sys.path.insert(0,str(HERE.parent/'continuation-e'))
from test_factories import *
SELF=0x20061000;DRAW=0x20062000;MENU=0x20063000;FLOAT=0x20064000;DEVICE=0x20065000
QUEUE=0x20066000;LOADER=0x20067000;LAYER=0x20068000;CLEAR=0x20069000
OVERLAYCLASS=0x2006a000;LOADERCLASS=0x2006b000;COLORCLASS=0x2006c000
METHOD_NAMES={'setDrawWindow:','drawWindow','setMenuWindow:','menuWindow','setFloatWindow:','floatWindow','setCommandQueue:','commandQueue','setLoader:','loader'}
METHODS={r['selector']:r['address'] for r in objc_methods(O) if r['cls']=='OverlayView' and r['selector'] in METHOD_NAMES}
assert len(METHODS)==10
class Overlay(Model):
 def __init__(self,image,mode):
  super().__init__(image,'DrawWindow');self.mode=mode;self.events=[];self.device=0;self.device_creations=0;self.allocations_by_role=[];self.once_invokes=[]
  putq(self.e,0xff09f0,OVERLAYCLASS);putq(self.e,0xff0bc8,LOADERCLASS);putq(self.e,0xff0a00,COLORCLASS)
  putq(self.e,0x1011620,0);putq(self.e,0x1011628,0);putq(self.e,0x1011e20,0)
  for a,n in IMPORTS.items():
   if n=='_MTLCreateSystemDefaultDevice':self.e.calls[a]=self.create_device
 def create_device(self,e):
  self.device_creations+=1;e.set(0,0 if self.mode=='device_nil' else DEVICE)
 def allocate(self,e):
  klass=e.get(0)
  if klass==OVERLAYCLASS:self.allocations_by_role.append('overlay');e.set(0,SELF)
  elif klass==LOADERCLASS:self.allocations_by_role.append('loader');e.set(0,0 if self.mode=='loader_alloc_nil' else LOADER)
  else:raise AssertionError(('Unknown class binding',hex(klass)))
 def super_message(self,e):
  assert e.cs(e.get(1))=='initWithFrame:' and e.q(e.get(0))==SELF
  self.events.append(dict(selector='inherited initWithFrame:',argument=hex(SELF)))
  e.set(0,0 if self.mode=='super_nil' else SELF)
 def once_boundary(self,e):
  token,block=e.get(0),e.get(1)
  assert token==0x1011628 and e.q(block+16)==0x684380
  self.once_invokes.append('0x684380')
  return Work(0x684380,[(0,block)],False,lambda:putq(e,token,MASK))
 def message(self,e):
  receiver=e.get(0);sel=e.cs(e.get(1));arg=e.get(2)
  if not receiver:e.set(0,0);return
  self.events.append(dict(selector=sel,receiver=hex(receiver),argument=hex(arg)))
  if receiver==SELF and sel in METHODS:return Work(METHODS[sel],(),False,None)
  if sel=='initWithFrame:::::':return Work(0x684454,(),False,None)
  if sel=='clearColor':e.set(0,CLEAR)
  elif sel=='layer':e.set(0,LAYER)
  elif sel in ('setBackgroundColor:','setOpaque:','setAutoResizeDrawable:','setDelegate:'):pass
  elif sel=='setDevice:':self.device=arg
  elif sel=='device':e.set(0,self.device)
  elif sel=='newCommandQueue':
   assert receiver==DEVICE;e.set(0,0 if self.mode=='queue_nil' else QUEUE)
  elif sel=='initWithDevice:':
   assert receiver==LOADER and arg==DEVICE;e.set(0,0 if self.mode=='loader_init_nil' else LOADER)
  else:raise AssertionError(('Unexpected message',sel,hex(receiver)))
 def initialize(self,control,stop=0x6849f8):
  e=self.e;e.pending=None
  args=[(0,SELF),(1,0),(2,control),(3,DRAW),(4,MENU),(5,FLOAT)]
  e.run(0x684454,args,stops=[stop])
  while e.pending is not None:
   work=e.pending;e.pending=None
   result=self.nested(work.address,work.args,work.prefix)
   if work.complete:work.complete()
   e.set(0,result);e.hit=None;e.u.emu_start(e.get(30),STOP+4,count=100000)
   assert e.hit is not None
  return e.hit,e.get(0)
 def properties(self):
  return {name:hex(self.nested(METHODS[name],[(0,SELF)])) for name in ['drawWindow','menuWindow','floatWindow','commandQueue','loader']}

def main():
 rows=[]
 FAILURES=['super_nil','device_nil','queue_nil','loader_alloc_nil','loader_init_nil']
 for build,image in [('original',O),('r03',P)]:
  for mode in FAILURES+['resource_prefix_ready']:
   for control in [0,0x20071000]:
    model=Overlay(image,mode);hit,returned=model.initialize(control)
    events=list(model.events);props=model.properties()
    return_tail_visited=0x6854ec in model.e.visited
    assert return_tail_visited==(mode=='super_nil')
    assert (0x1017600 in model.e.visited)==(build=='r03' and mode=='super_nil')
    assert model.e.q(0x1011e20)==control
    assert props['drawWindow']==hex(DRAW) and props['menuWindow']==hex(MENU) and props['floatWindow']==hex(FLOAT)
    delegated=[e for e in events if e['selector']=='setDelegate:']
    assert len(delegated)==int(mode not in ['super_nil','device_nil'])
    if delegated:assert delegated[0]['argument']==hex(SELF)
    if mode=='resource_prefix_ready':assert hit==0x6849f8
    else:assert hit==STOP and returned==0
    assert model.device_creations==int(mode!='super_nil')
    assert props['commandQueue']==hex(QUEUE if mode in ['loader_alloc_nil','loader_init_nil','resource_prefix_ready'] else 0)
    assert props['loader']==hex(LOADER if mode=='resource_prefix_ready' else 0)
    assert all(a in model.e.visited for a in [METHODS['setDrawWindow:'],METHODS['setMenuWindow:'],METHODS['setFloatWindow:']])
    rows.append(dict(test='overlayResourceGuards',build=build,mode=mode,control=hex(control),stop=hex(hit),returned=hex(returned) if hit==STOP else None,raw_control_slot=hex(model.e.q(0x1011e20)),properties=props,return_retain_tail_visited=return_tail_visited,r03_trampoline_visited=0x1017600 in model.e.visited,delegate_assignments=len(delegated),device_creation_calls=model.device_creations,events=events))
  for failure in FAILURES:
   model=Overlay(image,failure);returned=[]
   for i,control in enumerate([0x20071000,0x20072000,0x20073000]):
    if i:model.mode='providers_recovered'
    returned.append(model.nested(0x68401c,[(0,OVERLAYCLASS),(2,control),(3,DRAW),(4,MENU),(5,FLOAT)]))
   assert returned==[0,0,0] and model.e.q(0x1011628)==MASK and model.e.q(0x1011620)==0
   assert model.once_invokes==['0x684380'] and model.allocations_by_role.count('overlay')==1
   assert model.e.q(0x1011e20)==0x20071000
   assert sum(e['selector']=='inherited initWithFrame:' for e in model.events)==1
   rows.append(dict(test='nativeFactoryFailureThenRecovery',build=build,first_failure=failure,subsequent_providers_recovered=True,returns=returned,once_invokes=model.once_invokes,allocations=model.allocations_by_role,raw_control_slot=hex(model.e.q(0x1011e20)),device_creation_calls=model.device_creations))
 assert len(rows)==34
 ranges=[(0x684454,0x6849f8),(0x6854e4,0x68557c),(0x68401c,0x684454)]+[(a,O.bounds(a)[1]) for a in METHODS.values()]
 checks=[]
 for lo,hi in ranges:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo)
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
 assert [(c['start'],c['end_exclusive']) for c in checks if not c['equal']]==[('0x6854e4','0x68557c')]
 result=dict(passed=True,cases=len(rows),scope='34 paired-build native/model cases: actual Overlay initializer resource guards and early normal failure returns, actual ten property methods and actual singleton factory/once block for first-failure/later-provider-recovery sequences. Successful-resource cases stop before 0x6849f8 and do not execute font/GUI/backend setup or later initialization. Inherited MTK/ObjC/ARC/Blocks, allocation, device/queue/loader provision and dispatch_once completion modeled. No actual scheduler, reentry, GPU/backend/device run, object deallocation, lifetime/race proof or timing.',code_equality=checks,records=rows)
 (RESULTS/'overlay-resource-tests.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),equal_ranges=sum(c['equal'] for c in checks),different_ranges=sum(not c['equal'] for c in checks))))

if __name__=='__main__':main()
