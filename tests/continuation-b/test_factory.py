from emulator import *
from collections import Counter
# Reuse only definitions; do not execute the previous test suite on import.
env={'__file__':str(Path(__file__).parent/'test_attachment.py')};exec(compile((Path(__file__).parent/'test_attachment.py').read_text().split('\nrows=[]\n')[0],'attachment_model','exec'),env)
Base=env['Model'];OVERLAY=env['OVERLAY'];MENU=env['MENU'];DRAW=env['DRAW'];FLOAT=env['FLOAT'];CTRL=env['CTRL']
D=Path(__file__).parent
class Factory(Base):
 def __init__(self,m):
  super().__init__(m);self.alloc_fail=False;self.properties={};self.e.write(0x1011620,bytes(16));self.e.write(0x1011e20,bytes(8));self.allocations=0;self.prefixes=0
  self.e.calls[0x876540]=self.alloc
  self.e.calls[0x876570]=self.release # Net of native retain plus return autorelease; not a real autorelease pool.
  self.e.calls[0x876294]=lambda e:(_ for _ in ()).throw(AssertionError('dispatch_once must be explicitly staged'))
 def alloc(self,e):
  self.allocations+=1;e.set(0,0 if self.alloc_fail else OVERLAY)
  if e.get(0):self.refs[e.get(0)]+=1
  self.events.append(dict(op='allocation_boundary',nil_result=self.alloc_fail))
 def msg(self,e):
  p=e.get(0);sel=e.cs(e.get(1))
  if sel in ['setDrawWindow:','setMenuWindow:','setFloatWindow:']:
   self.events.append(dict(op='message',receiver=hex(p),selector=sel,arg=hex(e.get(2))))
   if p:self.properties[sel]=e.get(2)
   return
  if sel=='initWithFrame:::::':
   assert p==0,'nonnil initialization should be staged through its native publication prefix'
   self.events.append(dict(op='nil_initializer_message'));e.set(0,0);return
  super().msg(e)
 def continue_native(self,a,stops=()):
  e=self.e;e.hit=None;e.stops={STOP,*stops};e.u.emu_start(a,STOP+4,count=100000);assert e.hit is not None
 def invoke(self,ctrl,draw,menu,floating,rect):
  e=self.e;self.dset(e,rect)
  e.run(0x68401c,[(0,e.q(0xff09f0)),(1,0),(2,ctrl),(3,draw),(4,menu),(5,floating)],stops=[0x876294],stack_pointer=0x30020000)
  once_executed=False
  if e.hit==0x876294:
   once_executed=True;outer=e.u.context_save();token=e.get(0);block=e.get(1);invoke=e.q(block+16);assert invoke==0x684380
   # Execute the native once block, pausing before the initializer message.
   e.run(invoke,[(0,block)],stops=[0x876624],stack_pointer=0x30018000)
   assert e.cs(e.get(1))=='initWithFrame:::::'
   if e.get(0):
    inner=e.u.context_save();args=[(i,e.get(i)) for i in range(6)];refs=self.refs.copy()
    e.run(0x684454,args,stops=[0x6844ec],stack_pointer=0x30010000)
    assert e.q(0x1011e20)==ctrl;self.prefixes+=1
    # The rest of init is modeled, so partial-prefix ownership is not scored.
    self.refs=refs;e.u.context_restore(inner);e.set(0,OVERLAY);self.continue_native(e.get(30))
   else:
    # Native nil ObjC initializer semantics at the modeled dispatch boundary.
    e.set(0,0);self.continue_native(e.get(30))
   assert e.hit==STOP
   e.write(token,struct.pack('<Q',(1<<64)-1));e.u.context_restore(outer);self.continue_native(e.get(30))
  assert e.hit==STOP
  return dict(returned=hex(e.get(0)),once_block_executed=once_executed,allocation_attempts=self.allocations,initializer_prefix_executions=self.prefixes,published_control_pointer=hex(e.q(0x1011e20)),properties={k:hex(v) for k,v in self.properties.items()},events=self.events.copy())
rows=[]
for build,m in [('original',O),('r03',P)]:
 for allocation_failure in [False,True]:
  model=Factory(m);model.alloc_fail=allocation_failure
  for iteration in range(3):
   before=len(model.events);ctrl=CTRL+iteration*0x100;draw=DRAW+iteration*0x100;menu=MENU+iteration*0x100;floating=FLOAT+iteration*0x100
   r=model.invoke(ctrl,draw,menu,floating,[float(iteration),2.,320.+iteration,240.]);r['events']=r['events'][before:]
   assert r['once_block_executed']==(iteration==0)
   assert r['allocation_attempts']==1
   if allocation_failure:
    assert r['returned']=='0x0' and r['published_control_pointer']=='0x0' and not r['properties']
    if iteration==0:model.alloc_fail=False # Restoring allocation later does not reset a completed once token.
   else:
    assert r['returned']==hex(OVERLAY) and r['published_control_pointer']==hex(CTRL)
    assert r['initializer_prefix_executions']==1
    assert r['properties']=={'setDrawWindow:':hex(draw),'setMenuWindow:':hex(menu),'setFloatWindow:':hex(floating)}
    setters=[x for x in r['events'] if x.get('selector') in ['setFrame:','setBounds:']];assert len(setters)==2
   rows.append(dict(test='nativeFactoryOnceAndReuse',build=build,first_allocation_failed=allocation_failure,iteration=iteration,requested_control_pointer=hex(ctrl),**r))
result=dict(passed=True,cases=len(rows),scope='Native shared factory, native once block and native initializer publication prefix. dispatch_once completion/token state modeled explicitly; no real dispatch_once or concurrency. Allocation, rest of initialization, ObjC property implementations, ARC and journal boundaries modeled. Pointer identities are symbolic; no real pointer lifetime guarantee.',records=rows)
(RESULTS/'factory-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
