from emulator import *
from collections import Counter
import itertools
D=Path(__file__).parent;SOURCE=0x20020000;COPY=0x20021000;CONTEXT=0x20022000;VERTEX=0x20023000;INDEX=0x20024000;COMMAND=0x20025000
class Model:
 def __init__(self,m,vertex,index,weak_results,command):
  self.e=E(m);self.refs=Counter();self.events=[];self.weak=list(weak_results)
  for off,ptr in [(0x20,vertex),(0x28,index)]:
   self.e.write(SOURCE+off,struct.pack('<Q',ptr))
   if ptr:self.refs[ptr]+=1 # Seed ownership of the original block's captures.
  self.e.write(SOURCE+0x30,struct.pack('<Q',CONTEXT))
  for a,n in IMPORTS.items():
   if n=='_objc_storeStrong':self.e.calls[a]=self.strong
   elif n=='_objc_copyWeak':self.e.calls[a]=lambda e:self.copyweak(e)
   elif n=='_objc_destroyWeak':self.e.calls[a]=lambda e:self.destroyweak(e)
   elif n=='_objc_loadWeakRetained':self.e.calls[a]=self.loadweak
   elif n=='_objc_release':self.e.calls[a]=self.release
   elif n=='_objc_msgSend':self.e.calls[a]=self.msg
 def strong(self,e):
  old=e.q(e.get(0));new=e.get(1)
  if old:self.refs[old]-=1
  if new:self.refs[new]+=1
  self.events.append(dict(op='strong',old=hex(old),new=hex(new)));e.write(e.get(0),struct.pack('<Q',new))
 def release(self,e):
  if e.get(0):self.refs[e.get(0)]-=1
 def copyweak(self,e):e.write(e.get(0),struct.pack('<Q',e.q(e.get(1))));self.events.append(dict(op='copyWeak'))
 def destroyweak(self,e):e.write(e.get(0),bytes(8));self.events.append(dict(op='destroyWeak'))
 def loadweak(self,e):
  assert self.weak;ptr=self.weak.pop(0);e.set(0,ptr)
  if ptr:self.refs[ptr]+=1
  self.events.append(dict(op='weakLoadRetained',result=hex(ptr)))
 def msg(self,e):
  sel=e.cs(e.get(1));assert sel=='enqueueReusableBuffer:'
  self.events.append(dict(op='recycle_message',receiver=hex(e.get(0)),buffer=hex(e.get(2))))
rows=[]
configs=[('distinct',VERTEX,INDEX),('nil_vertex',0,INDEX),('nil_index',VERTEX,0),('both_nil',0,0),('aliased',VERTEX,VERTEX)]
for build,m in [('original',O),('r03',P)]:
 for (name,v,i),(weak_name,weak),command in itertools.product(configs,[('live_live',[CONTEXT,CONTEXT]),('live_nil',[CONTEXT,0]),('nil_nil',[0,0])],[0,COMMAND]):
  model=Model(m,v,i,weak,command);e=model.e
  e.run(0x12eea8,[(0,COPY),(1,SOURCE)]);assert e.q(COPY+0x20)==v and e.q(COPY+0x28)==i and e.q(COPY+0x30)==CONTEXT
  e.run(0x12ef14,[(0,SOURCE)])
  assert e.q(SOURCE+0x20)==0 and e.q(SOURCE+0x28)==0 and e.q(SOURCE+0x30)==0
  before=model.refs.copy();e.run(0x12edb8,[(0,COPY),(1,command)]);assert not model.weak
  assert model.refs==before # Invocation releases temporary weak loads and command-buffer local, not captures.
  calls=[x for x in model.events if x['op']=='recycle_message'];assert len(calls)==2
  assert [x['receiver'] for x in calls]==[hex(x) for x in weak] and [x['buffer'] for x in calls]==[hex(v),hex(i)]
  e.run(0x12ef14,[(0,COPY)]);assert all(n==0 for n in model.refs.values())
  assert e.q(COPY+0x20)==0 and e.q(COPY+0x28)==0 and e.q(COPY+0x30)==0
  rows.append(dict(test='completionCaptureLifecycle',build=build,buffers=name,weak_resolution=weak_name,command_present=bool(command),temporary_and_capture_deltas_balanced=True,events=model.events))
result=dict(passed=True,cases=len(rows),scope='Native completion-block copy/dispose/invoke helpers with manually prepared blocks. ARC counters, zeroing-weak resolutions and enqueueReusableBuffer: effect modeled. A live-to-nil weak sequence is forced, not proven reachable under real owner lifetime. Native buffer-cache insertion, GPU completion, actual Blocks runtime copying and concurrency not executed.',records=rows)
(RESULTS/'completion-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
