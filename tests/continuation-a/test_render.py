from emulator import *
from collections import Counter
D=Path(__file__).parent
SELF=0x20001000;VIEW=0x20002000;DEVICE=0x20003000;QUEUE=0x20004000;APP=0x20005000;CMD=0x20006000;DESC=0x20007000;DRAWABLE=0x20008000;ENC=0x20009000;CTX=0x2000a000;IO=0x2000b000;DATA=0x2000c000;CTRL=0x2000d000;MENU=0x2000e000;FLOAT=0x2000f000;DRAW=0x20010000;GEST=0x20011000
class Model:
 def __init__(self,m):
  self.e=E(m);self.e.journal();self.refs=Counter();self.events=[];self.fault='none';self.flip=False;self.flip_at_encode=False;self.gesture_state=3
  self.e.write(0xff0988,struct.pack('<Q',0x20012000));self.e.write(0x1011e20,struct.pack('<Q',CTRL));self.e.write(CTRL,b'\1\0');self.e.write(0x1010a28,b'\1')
  for a,name in IMPORTS.items():
   if name in ['_objc_retain','_objc_retainAutoreleasedReturnValue','_objc_retainAutoreleaseReturnValue','_objc_retainBlock']:self.e.calls[a]=self.retain
   elif name=='_objc_release':self.e.calls[a]=self.release
   elif name=='_objc_storeStrong':self.e.calls[a]=self.strong
   elif name=='_objc_msgSend':self.e.calls[a]=self.msg
   elif name=='_clock_gettime':self.e.calls[a]=lambda e:e.write(e.get(1),struct.pack('<QQ',100,0)) or e.set(0,0)
  self.e.calls[0x138114]=lambda e:e.set(0,0 if self.fault=='context' else CTX)
  self.e.calls[0x138548]=lambda e:e.set(0,IO)
  self.e.calls[0x1385c8]=self.draw_data
  for a,n in [(0x12a254,'metalNewFrame'),(0x13a874,'imguiNewFrame'),(0x1451b4,'imguiRender'),(0x687ba0,'encodeDrawData')]:self.e.calls[a]=lambda e,n=n:self.events.append(n)
  self.e.calls[0x687ba0]=self.encode
 def retain(self,e):
  if e.get(0):self.refs[e.get(0)]+=1
 def release(self,e):
  if e.get(0):self.refs[e.get(0)]-=1
 def strong(self,e):
  p=e.get(0);new=e.get(1);old=e.q(p)
  if new:self.refs[new]+=1
  if old:self.refs[old]-=1
  self.events.append(('strong',hex(old),hex(new)));e.write(p,struct.pack('<Q',new))
 def draw_data(self,e):
  self.events.append('getDrawData');e.set(0,0 if self.fault=='drawData' else DATA)
  if self.flip:e.write(0x1010a28,b'\0');self.events.append('modeledInactivityBeforeLateGuard')
 def msg(self,e):
  sel=e.cs(e.get(1));p=e.get(0);self.events.append(('message',sel,hex(p)))
  vals={'device':DEVICE,'commandQueue':QUEUE,'sharedApplication':APP,'applicationState':0,'commandBuffer':CMD,'currentRenderPassDescriptor':DESC,'currentDrawable':DRAWABLE,'renderCommandEncoderWithDescriptor:':ENC,'menuWindow':MENU,'floatWindow':FLOAT,'drawWindow':DRAW,'state':self.gesture_state}
  failed={'device':'device','queue':'commandQueue','commandBuffer':'commandBuffer','descriptor':'currentRenderPassDescriptor','drawable':'currentDrawable','encoder':'renderCommandEncoderWithDescriptor:'}
  if sel in vals:
   v=vals[sel]
   if sel==failed.get(self.fault) or (sel=='applicationState' and self.fault=='inactive'):v=0 if sel!='applicationState' else 2
   if p==0:v=0
   e.set(0,v)
  elif sel in ['syncOverlaySize','setClearColor:','drawFloatWindow','drawMenuWindow','drawDrawWindow','pushDebugGroup:','popDebugGroup','endEncoding','presentDrawable:','commit']:
   pass
  else:raise AssertionError(('unknown selector',sel,hex(p)))
 def encode(self,e):
  self.events.append('encodeDrawData')
  if self.flip_at_encode:e.write(0x1010a28,b'\0');self.events.append('modeledInactivityAfterLateGuard')
 def frame(self):
  self.events=[];self.refs.clear();self.e.run(0x685d6c,[(0,SELF),(1,0),(2,0 if self.fault=='view' else VIEW)])
  unbalanced={hex(k):v for k,v in self.refs.items() if v};assert not unbalanced,unbalanced
  return self.events.copy()
 def names(self,events):return [x[1] for x in events if isinstance(x,tuple) and x[0]=='message']
rows=[]
for build,m in [('original',O),('r03',P)]:
 model=Model(m)
 for fault in ['none','view','device','queue','inactive','context','commandBuffer','descriptor','drawable','drawData','encoder']:
  model.fault=fault;model.flip=False;model.e.write(0x1010a28,b'\1');events=model.frame();names=model.names(events)
  success=fault=='none'
  assert ('commit' in names)==success and ('presentDrawable:' in names)==success and ('endEncoding' in names)==success,(build,fault,names,events)
  assert ('encodeDrawData' in events)==success
  rows.append(dict(test='renderAcquisitionAndCleanup',build=build,fault=fault,committed=success,ownership_delta_zero=True,events=events))
  if not success:
   model.fault='none';model.e.write(0x1010a28,b'\1');recovery=model.frame();assert 'commit' in model.names(recovery)
   rows.append(dict(test='renderRecoveryAfterFailure',build=build,preceding_fault=fault,committed=True,ownership_delta_zero=True,events=recovery))
 # Staged state change inside the modeled draw-data boundary, not actual concurrency.
 model.fault='none';model.flip=True;model.e.write(0x1010a28,b'\1');events=model.frame();names=model.names(events)
 assert ('commit' in names)==(build=='original')
 if build=='r03':assert struct.unpack('<d',model.e.u.mem_read(0x1011630,8))[0]==0
 rows.append(dict(test='inactivityBeforeLateGuard',build=build,committed='commit' in names,ownership_delta_zero=True,events=events))
 # Real native shortcut callback composed with native frame control flow.
 model.flip=False;model.e.write(0x1010a28,b'\1');model.e.write(CTRL,b'\0\0')
 events=model.frame();assert 'drawMenuWindow' not in model.names(events)
 for iteration in range(2):
  model.e.run(0x686f8c,[(0,SELF),(1,0),(2,GEST)]);assert model.e.byte(CTRL)==1
  events=model.frame();assert 'drawMenuWindow' in model.names(events)
  assert model.e.byte(CTRL)==1
  rows.append(dict(test='shortcutToMenuConsumer',build=build,iteration=iteration,request_after_callback=1,request_after_frame=1,menu_draw_reached=True,events=events))
 # A later staged change is beyond the late guard's observation point.
 model.fault='none';model.flip=False;model.flip_at_encode=True;model.e.write(0x1010a28,b'\1');events=model.frame()
 assert 'commit' in model.names(events)
 rows.append(dict(test='inactivityAfterLateGuard',build=build,committed=True,ownership_delta_zero=True,events=events))
 model.flip_at_encode=False
 # Compose each gesture state with frame menu/float consumers, with/without pointer.
 for state in range(6):
  for pointer in [False,True]:
   for hidden in [0,1]:
    model.gesture_state=state;model.e.write(0x1011e20,struct.pack('<Q',CTRL if pointer else 0));model.e.write(CTRL,bytes([0,hidden]));model.e.write(0x1010a28,b'\1')
    model.e.run(0x686f8c,[(0,SELF),(1,0),(2,GEST)]);events=model.frame();names=model.names(events)
    menu=pointer and state==3;floating=pointer and not hidden
    assert ('drawMenuWindow' in names)==menu
    assert ('drawFloatWindow' in names)==floating
    rows.append(dict(test='shortcutStateToFrameComposition',build=build,gesture_state=state,pointer_present=pointer,second_control_byte=hidden,menu_draw_reached=menu,float_draw_reached=bool(floating),events=events))
 # Initializer prefix publishes its raw x2 argument, independently of later construction.
 for ptr in [0,CTRL,CTRL+0x100]:
  model.e.run(0x684454,[(0,SELF),(1,0),(2,ptr),(3,0),(4,0),(5,0)],stops=[0x6844ec]);assert model.e.q(0x1011e20)==ptr
  rows.append(dict(test='initializerControlPointerPublication',build=build,published_pointer=hex(ptr),prefix_only=True))
result=dict(passed=True,cases=len(rows),scope='Native original/R03 frame control flow, normal cleanup, shortcut callback, wrappers and R03 late guard. Objective-C getters/effects, clock, ARC accounting, ImGui/Metal frame and encoding callees, context/data results and journal sink modeled. Faults synthetic. No real ARC/UIKit/Metal, GPU submission, physical gesture/touch timing, exceptions or races.',records=rows)
(RESULTS/'render-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
