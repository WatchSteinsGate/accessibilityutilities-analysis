"""Composed native size/backend/attachment caller; external providers modeled."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-i'))
sys.path.insert(0,str(HERE.parent/'continuation-h'))
from test_overlay_config import *
THREADCLASS=0x200a1000;SCREENCLASS=0x200a2000;SCREEN=0x200a3000;MAINQUEUE=0x200a4000
CACHED=0x200a5000;SAVEDBLOCK=0x200a6000
SYNC_METHODS={m['selector']:m['address'] for m in objc_methods(O) if m['cls']=='OverlayView' and m['selector'] in ['overlaySizeSyncing','setOverlaySizeSyncing:']}
class Pipeline(Fonts):
 def __init__(self,image,main_thread,eligible):
  super().__init__(image,'ready');self.main_thread=main_thread;self.eligible=set(eligible);self.trace=[];self.queued=[];self.backend_events=[];self.helper_result=0;self.scale=1.;self.drawable=(0.,0.);self.menu_device=None;self.menu_cache=CACHED
  putq(self.e,0xff09c8,THREADCLASS);putq(self.e,0xff0980,SCREENCLASS);putq(self.e,0xfd82e8,MAINQUEUE)
  putq(self.e,0x10112f8,CACHED);putq(self.e,0x1011c80,0);putq(self.e,0x1011c88,0)
  self.e.calls[0x1681cc]=lambda e:self.trace.append(dict(boundary='style',modeled=True))
  self.e.calls[0x12f1b8]=self.registration_boundary
  self.e.calls[0x12a434]=self.device_objects_boundary
  self.e.calls[0x6374b4]=self.decode_boundary
  for a,n in IMPORTS.items():
   if n=='_dispatch_async':self.e.calls[a]=self.enqueue
 def registration_boundary(self,e):
  self.trace.append(dict(boundary='backend-registration',modeled=True));Backend.registration(self,e)
 def device_objects_boundary(self,e):
  self.trace.append(dict(boundary='backend-device-objects',modeled=True));Backend.device_objects(self,e)
 def fp(self,*values):
  for i,v in enumerate(values):self.e.u.reg_write(getattr(R,'UC_ARM64_REG_D'+str(i)),struct.unpack('<Q',struct.pack('<d',v))[0])
 def fp_get(self,i=0):return struct.unpack('<d',struct.pack('<Q',self.e.u.reg_read(getattr(R,'UC_ARM64_REG_D'+str(i)))))[0]
 def enqueue(self,e):
  assert e.get(0)==MAINQUEUE and e.q(e.get(1)+16)==0x685b98
  e.write(SAVEDBLOCK,bytes(e.u.mem_read(e.get(1),0x28)))
  self.queued.append(dict(invoke='0x685b98',captured_self=hex(e.q(SAVEDBLOCK+0x20))))
  assert self.queued[-1]['captured_self']==hex(SELF)
  self.trace.append(dict(boundary='size-sync-enqueued'))
 def decode_boundary(self,e):
  self.trace.append(dict(boundary='image-decode',modeled_result=False));e.set(0,0)
 def message(self,e):
  receiver=e.get(0);sel=e.cs(e.get(1));arg=e.get(2)
  if sel=='isMainThread':assert receiver==THREADCLASS;e.set(0,self.main_thread);return
  if receiver==SELF and sel in SYNC_METHODS:return Work(SYNC_METHODS[sel],(),False,None)
  if receiver==SELF and sel=='syncOverlaySize':
   self.trace.append(dict(boundary='syncOverlaySize',main_thread=self.main_thread));return Work(0x6855c0,(),False,None)
  if sel=='mainScreen':assert receiver==SCREENCLASS;e.set(0,SCREEN);return
  if sel=='nativeScale':assert receiver==SCREEN;self.fp(2.);return
  if receiver==SELF and sel in ['bounds','frame']:self.fp(0.,0.,320.,240.);return
  if receiver==SELF and sel=='contentScaleFactor':self.fp(self.scale);return
  if receiver==SELF and sel=='drawableSize':self.fp(*self.drawable);return
  if receiver==SELF and sel=='setContentScaleFactor:':
   self.scale=self.fp_get();self.trace.append(dict(boundary=sel,value=self.scale));return
  if receiver==SELF and sel=='setDrawableSize:':
   self.drawable=(self.fp_get(),self.fp_get(1));self.trace.append(dict(boundary=sel,value=list(self.drawable)));return
  if receiver in [FLOAT,DRAW,MENU] and sel=='respondsToSelector:':
   expected='setOverlayView:' if receiver==MENU else 'initImageTexture:';assert e.cs(arg)==expected
   result=receiver in self.eligible;self.trace.append(dict(boundary='respondsToSelector:',receiver=hex(receiver),selector=expected,returned=result));e.set(0,result);return
  if receiver in [FLOAT,DRAW] and sel=='initImageTexture:':
   assert arg==DEVICE;self.trace.append(dict(boundary=sel,receiver=hex(receiver),device=hex(arg),modeled=True));e.set(0,0);return
  if receiver==MENU and sel=='setOverlayView:':
   assert arg==SELF;self.trace.append(dict(boundary=sel,receiver=hex(receiver),native=True));return Work(0x617460,(),False,None)
  if receiver==MENU and sel=='readIniConfig':self.trace.append(dict(boundary=sel,modeled=True));return
  if receiver==BACKEND and sel=='makeDeviceObjectsWithDevice:':
   self.backend_events.append(dict(selector=sel,device=hex(arg)));e.set(0,0);return
  if receiver==SELF and sel=='device' and self.menu_device is not None:e.set(0,self.menu_device);return
  return super().message(e)
 def display(self):return list(struct.unpack('<ff',self.e.u.mem_read(IO+8,8)))
 def drain(self):
  assert len(self.queued)==1;self.main_thread=True;self.nested(0x685b98,[(0,SAVEDBLOCK)])

def main():
 rows=[]
 variants={'all':[FLOAT,DRAW,MENU],'none':[],'float_only':[FLOAT],'draw_only':[DRAW],'menu_only':[MENU],'missing':[]}
 for build,image in [('original',O),('r03',P)]:
  for main_thread in [True,False]:
   for name,eligible in variants.items():
    model=Pipeline(image,main_thread,eligible);windows=(0,0,0) if name=='missing' else (DRAW,MENU,FLOAT)
    hit,_=model.initialize(0x20071000,stop=0x6854a8,windows=windows);assert hit==0x6854a8
    assert model.e.q(0x1011c88)==(SELF if MENU in eligible else 0)
    assert [r['receiver'] for r in model.trace if r['boundary']=='initImageTexture:']==[hex(v) for v in [FLOAT,DRAW] if v in eligible]
    assert len([r for r in model.trace if r['boundary']=='respondsToSelector:'])==(0 if name=='missing' else 3)
    assert 0x12a0c8 in model.e.visited and 0x12a1cc in model.e.visited and model.e.byte(IO+0xcc)==1
    before=model.display();assert before==([640.,480.] if main_thread else [0.,0.])
    assert len(model.queued)==int(not main_thread)
    before_trace=list(model.trace)
    order=[v['boundary'] for v in before_trace]
    assert order.index('syncOverlaySize')<order.index('backend-registration')<order.index('backend-device-objects')
    for boundary in ['initImageTexture:','setOverlayView:']:
     if boundary in order:assert order.index('backend-device-objects')<order.index(boundary)
    if not main_thread:assert order.index('size-sync-enqueued')<order.index('backend-registration')
    if not main_thread:model.drain()
    assert model.display()==[640.,480.] and model.drawable==(640.,480.) and model.scale==2.
    rows.append(dict(test='composedOverlaySizeBackendAttachment',build=build,main_thread=main_thread,variant=name,stop=hex(hit),initializer_return_tested=False,display_before_drain=before,display_after=list(model.display()),drawable=list(model.drawable),queue=model.queued,trace_before_drain=before_trace,trace_after_drain=model.trace[len(before_trace):],backend_boundaries=model.backend_events,menu_overlay=hex(model.e.q(0x1011c88))))
  for device,cache,label in [(0,0,'nil_device'),(DEVICE,CACHED,'existing_cache'),(DEVICE,0,'decode_false')]:
   model=Pipeline(image,True,[]);model.menu_device=device;putq(model.e,0x10112f8,cache)
   model.nested(0x617460,[(0,MENU),(1,0),(2,SELF)])
   assert model.e.q(0x1011c88)==SELF and model.e.q(0x10112f8)==cache
   assert len([v for v in model.trace if v['boundary']=='image-decode'])==int(label=='decode_false')
   assert len([v for v in model.trace if v['boundary']=='readIniConfig'])==1
   rows.append(dict(test='nativeMenuBackreferenceGuards',build=build,mode=label,overlay=hex(model.e.q(0x1011c88)),texture_cache=hex(model.e.q(0x10112f8)),trace=model.trace,ini_pointer='0x0',void_method_return_not_interpreted=True))
 assert len(rows)==30
 checks=[]
 for lo,hi in [(0x684e74,0x6854e4),(0x6855c0,0x685d6c),(0x617460,0x617874)]:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=True,sha256=hashlib.sha256(a).hexdigest()))
 data=dict(passed=True,cases=len(rows),scope='30 native/model cases. 24 composed resource/font-ready Overlay caller paths execute native size synchronization, backend initializer/helper and selector-gated child/menu calls, stopping at 0x6854a8 before final return tail. Six standalone native Menu setter normal-return guard cases use nil INI pointer and cached/absent textures with decode-false modeled. GUI creation/ABI, style, fonts, child texture callbacks, readIniConfig, backend registration/device objects, ObjC/ARC/Blocks/queue and allocation modeled. Off-main runs are synthetic boundary tests, not proven reachable startup or race. Queue capture copied and drained manually, not actual Blocks runtime. No full successful initializer return, real GPU/backend/device run, deallocation/lifetime/race proof or performance result.',code_equality=checks,records=rows)
 (RESULTS/'overlay-attachment-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),equal_ranges=len(checks))))
if __name__=='__main__':main()
