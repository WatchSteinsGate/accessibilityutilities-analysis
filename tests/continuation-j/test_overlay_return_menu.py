"""Native normal-return caller/R03 wrapper and Menu INI state application."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-j'))
sys.path.insert(0,str(HERE.parent/'continuation-i'))
from test_overlay_attachment import *
MODELCLASS=0x200b1000;INI=0x200b2000;STATE=0xff31f0
class ReturnModel(Pipeline):
 def __init__(self,image,class_present=True,add_result=True,eligible=()):
  super().__init__(image,True,eligible);self.class_present=class_present;self.add_result=add_result;self.additions=[];self.registered=[];self.lookups=[];self.requests=[]
  for a,n in IMPORTS.items():
   if n=='_class_addMethod':self.e.calls[a]=self.add_method
   elif n=='_sel_registerName':self.e.calls[a]=self.register_selector
   elif n=='_objc_getClass':self.e.calls[a]=self.lookup_class
  # Isolate per-test counters/flags in emulated memory only.
  self.e.write(0x1013de0,bytes(8));self.e.write(0x10137a0,bytes(4))
 def add_method(self,e):
  assert e.get(0)==MODELCLASS
  self.additions.append(dict(selector=e.cs(e.get(1)),returned=self.add_result));e.set(0,self.add_result)
 def register_selector(self,e):
  self.registered.append(e.cs(e.get(0)))
  # The source string is a symbolic SEL identity in this model.
 def lookup_class(self,e):
  self.lookups.append(e.cs(e.get(0)));e.set(0,0x200b8000+len(self.lookups)*0x100)
 def message(self,e):
  if e.get(0)==SELF and e.cs(e.get(1))=='setAutoresizingMask:':
   self.trace.append(dict(boundary='setAutoresizingMask:',argument=hex(e.get(2)),modeled=True));return
  if e.get(0)==SELF and e.cs(e.get(1)) in ['setFrame:','setBounds:']:
   self.trace.append(dict(boundary=e.cs(e.get(1)),rect=[self.fp_get(i) for i in range(4)],modeled=True));return
  if e.get(0)==SELF and e.cs(e.get(1))=='class':e.set(0,MODELCLASS if self.class_present else 0);return
  if e.get(0)==SELF and e.cs(e.get(1))=='performSelectorOnMainThread:withObject:waitUntilDone:':
   assert e.cs(e.get(2))=='v58InstallBubble:' and e.get(3)==0 and e.get(4)==0
   self.requests.append(dict(selector=e.cs(e.get(2)),object='0x0',wait_until_done=False,execution_modeled=False));e.set(0,0);return
  return super().message(e)
 def instrumentation(self):
  return dict(counter=int.from_bytes(self.e.u.mem_read(0x1013de0,4),'little'),touch_add_flags=int.from_bytes(self.e.u.mem_read(0x1013de4,4),'little'),bubble_flag=int.from_bytes(self.e.u.mem_read(0x10137a0,4),'little'),method_additions=self.additions,selector_registrations=len(self.registered),class_lookups=len(self.lookups),main_thread_requests=self.requests)
 def verify_return_hook(self,build):
  s=self.instrumentation()
  if build=='original':assert s['counter']==0 and not self.additions and not self.requests
  else:
   assert s['counter']==1 and len(self.registered)==34 and len(self.lookups)==6
   assert len(self.additions)==(7 if self.class_present else 0)
   assert len(self.requests)==int(self.class_present)
   assert s['touch_add_flags']==(15 if self.class_present and self.add_result else 0)
   assert s['bubble_flag']==int(self.class_present)
   assert 0x1017600 in self.e.visited and 0x1016700 in self.e.visited and 0x101770c in self.e.visited
  return s
class MenuIni(Pipeline):
 def __init__(self,image,style,mask,already):
  super().__init__(image,True,[]);self.values={'style':style,'enabledStyles':mask};self.reads=[]
  putq(self.e,0x1011c80,INI);self.e.write(0xff3208,b'\1')
  self.e.write(STATE,struct.pack('<iiiiBB',9,8,7,6,int(already),1))
  self.e.calls[0x8571d0]=self.ini_integer
 def ini_integer(self,e):
  assert e.get(0)==INI and e.cs(e.get(1))=='menuAppearance'
  key=e.cs(e.get(2));assert key in self.values
  self.reads.append(dict(section='menuAppearance',key=key,default=e.get(3),returned=self.values[key]));e.set(0,self.values[key])
 def state(self):
  current,selected,mask,transition,applied,dirty=struct.unpack('<IIII BB',self.e.u.mem_read(STATE,18))
  return dict(current=current,selected=selected,enabled_mask=mask,transition=transition,applied=applied,dirty=dirty)

def main():
 rows=[]
 variants={'none':[],'all':[FLOAT,DRAW,MENU],'missing':[]}
 for build,image in [('original',O),('r03',P)]:
  modes=[('not_used',True,True)] if build=='original' else [('class_nil',False,False),('adds_false',True,False),('adds_true',True,True)]
  for mode,present,added in modes:
   for name,eligible in variants.items():
    model=ReturnModel(image,present,added,eligible);windows=(0,0,0) if name=='missing' else (DRAW,MENU,FLOAT)
    model.fp(0.,0.,320.,240.);hit,result=model.initialize(0x20071000,stop=STOP,windows=windows)
    assert hit==STOP and result==SELF and model.display()==[640.,480.]
    assert model.e.q(0x1011c88)==(SELF if MENU in eligible else 0)
    hook=model.verify_return_hook(build)
    rows.append(dict(test='nativeOverlayNormalReturn',build=build,variant=name,runtime_model=mode,returned=hex(result),display=model.display(),instrumentation=hook,requested_bubble_callback_executed=False))
  # Compose the real singleton factory/once/initializer through normal return.
  for mode,present,added in ([('not_used',True,True)] if build=='original' else [('adds_false',True,False),('adds_true',True,True)]):
   model=ReturnModel(image,present,added,[FLOAT,DRAW,MENU]);returns=[]
   for control in [0x20071000,0x20072000,0x20073000]:
    model.fp(0.,0.,320.,240.);returns.append(model.nested(0x68401c,[(0,OVERLAYCLASS),(2,control),(3,DRAW),(4,MENU),(5,FLOAT)]))
   assert returns==[SELF]*3 and model.once_invokes==['0x684380']
   assert model.e.q(0x1011e20)==0x20071000 and model.e.q(0x1011620)==SELF and model.e.q(0x1011628)==MASK
   hook=model.verify_return_hook(build)
   geometry=[v for v in model.trace if v['boundary'] in ['setFrame:','setBounds:','setAutoresizingMask:']]
   assert geometry and all(v['rect']==[0.,0.,320.,240.] for v in geometry if 'rect' in v)
   rows.append(dict(test='nativeSingletonNormalReturnReuse',build=build,runtime_model=mode,returns=[hex(v) for v in returns],once_invokes=model.once_invokes,control=hex(model.e.q(0x1011e20)),geometry_boundaries=geometry,instrumentation=hook))
  for style,mask,already in [(1,1,False),(2,1,False),(3,7,False),(-1,0,False),(0,2,False),(2,-1,False),(3,4,False),(1,1,True)]:
   model=MenuIni(image,style,mask,already)
   for _ in range(2):model.nested(0x617460,[(0,MENU),(1,0),(2,SELF)])
   state=model.state();normalized=(mask&3) or 3
   requested_bit=(1<<(style-1)) if 1<=style<=3 else 0
   selected=style if requested_bit&normalized else (2 if normalized&2 else 1)
   expected=dict(current=9,selected=8,enabled_mask=7,transition=6,applied=1,dirty=1) if already else dict(current=selected,selected=selected,enabled_mask=normalized,transition=0xffffffff,applied=1,dirty=0)
   assert state==expected
   assert len(model.reads)==(0 if already else 2)
   if model.reads:assert [v['default'] for v in model.reads]==[2,3]
   assert len([v for v in model.trace if v['boundary']=='readIniConfig'])==2
   assert model.e.q(0x1011c88)==SELF
   rows.append(dict(test='nativeMenuIniApplyAndReuse',build=build,input_style=style,input_mask=mask,already_applied=already,calls=2,ini_reads=model.reads,state=state,read_ini_callback_modeled=True,state_constructor_preinitialized=True))
 assert len(rows)==31
 checks=[]
 for lo,hi in [(0x6854a8,0x68557c),(0x61776c,0x61785c),(0x617c8c,0x617d80)]:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo)
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
 assert [x['start'] for x in checks if not x['equal']]==['0x6854a8']
 data=dict(passed=True,cases=len(rows),scope='31 native/model records: 12 native complete normal-return Overlay caller paths including actual existing R03 nonnil return wrapper/helpers; 3 actual singleton/once/normal-return reuse sequences; 16 native Menu nonnil-INI apply/reuse cases with preinitialized native state getter and modeled integer reads. GUI creation/ABI/style/fonts, GPU/backend/device objects, child callbacks, readIniConfig, ObjC/ARC/Blocks/queue/class/selector registration and method-add outcomes modeled. Requested v58InstallBubble callback not executed. No binary edits, actual runtime method installation, genuine backend/device run, lifetime/race proof or performance result.',code_comparison=checks,records=rows)
 (RESULTS/'overlay-return-menu-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),equal_ranges=2,different_ranges=1)))
if __name__=='__main__':main()
