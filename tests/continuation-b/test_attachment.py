from emulator import *
from collections import Counter
D=Path(__file__).parent
STATE=0xff2798;BLOCK=0x20001000;FIELD=0x20002000;CHILD=0x20003000;GAME=0x20004000;MENU=0x20005000;DRAW=0x20006000;FLOAT=0x20007000;ARRAY=0x20008000;OVERLAY=0x20009000;OLD=0x2000a000;CTRL=0x2000b000
class Model:
 def __init__(self,m):
  self.e=E(m);self.e.journal();self.e.noop([0x262e4,0x2675c]);self.refs=Counter();self.events=[];self.parent=0;self.fault='none';self.target=CHILD if m is O else GAME
  self.e.write(STATE+0x40,struct.pack('<QQ',9,13));self.e.write(STATE+0x50,bytes([1,0,0,0,1]));self.e.write(BLOCK+32,struct.pack('<Q',9));self.e.write(0x10109c1,b'\0');self.e.write(0x1011b68,struct.pack('<Q',CTRL));self.e.write(0x1011c50,struct.pack('<Q',GAME));self.class_roles={self.e.q(slot):name for slot,name in [(0xff09d8,'MenuWindow'),(0xff0978,'DrawWindow'),(0xff09e0,'FloatView'),(0xff09e8,'FieldView'),(0xff09f0,'OverlayView')]}
  for a,name in IMPORTS.items():
   if name in ['_objc_retain','_objc_retainAutoreleasedReturnValue','_objc_retainAutoreleaseReturnValue','_objc_retainBlock']:self.e.calls[a]=self.retain
   elif name=='_objc_release':self.e.calls[a]=self.release
   elif name=='_objc_storeStrong':self.e.calls[a]=self.strong
   elif name=='_objc_msgSend':self.e.calls[a]=self.msg
 def retain(self,e):
  if e.get(0):self.refs[e.get(0)]+=1
 def release(self,e):
  if e.get(0):self.refs[e.get(0)]-=1
 def strong(self,e):
  old=e.q(e.get(0));new=e.get(1)
  if old:self.refs[old]-=1
  if new:self.refs[new]+=1
  self.events.append(dict(op='strong',old=hex(old),new=hex(new)));e.write(e.get(0),struct.pack('<Q',new))
 def dget(self,e):return [struct.unpack('<d',struct.pack('<Q',e.u.reg_read(getattr(R,'UC_ARM64_REG_D'+str(i)))))[0] for i in range(4)]
 def dset(self,e,values):
  for i,v in enumerate(values):e.u.reg_write(getattr(R,'UC_ARM64_REG_D'+str(i)),struct.unpack('<Q',struct.pack('<d',v))[0])
 def msg(self,e):
  p=e.get(0);sel=e.cs(e.get(1));role=self.class_roles.get(p,'object');ev=dict(op='message',receiver=hex(p),selector=sel,role=role,arg=hex(e.get(2)));self.events.append(ev)
  if not p:e.set(0,0);return
  if sel=='sharedInstance:':
   ptr={'MenuWindow':MENU,'DrawWindow':DRAW,'FloatView':FLOAT}[role];e.set(0,0 if self.fault==role else ptr)
  elif sel=='sharedInstance':e.set(0,0 if self.fault=='field' else FIELD)
  elif sel=='subviews':e.set(0,ARRAY)
  elif sel=='lastObject':e.set(0,0 if self.fault=='child' else CHILD)
  elif sel=='bounds':self.dset(e,[11.,17.,320.,240.]);ev['rect']=self.dget(e)
  elif sel=='sharedInstance:::::':
   ev['args']=[hex(e.get(i)) for i in [2,3,4,5]];ev['rect']=self.dget(e);e.set(0,0 if self.fault=='overlay' else OVERLAY)
  elif sel in ['setFrame:','setBounds:']:ev['rect']=self.dget(e)
  elif sel=='setAutoresizingMask:':pass
  elif sel=='superview':e.set(0,self.parent)
  elif sel=='removeFromSuperview':ev['previous_parent']=hex(self.parent);self.parent=0
  elif sel=='addSubview:':
   ev['nil_child']=e.get(2)==0
   if e.get(2):self.parent=p
  else:raise AssertionError((sel,role))
 def run(self,stage=None,transition='suspend'):
  if stage is None:self.e.run(0x76944,[(0,BLOCK)])
  else:
   e=self.e;e.run(0x76944,[(0,BLOCK)],stops=[stage]);assert e.hit==stage,(hex(stage),hex(e.hit))
   saved=e.u.context_save();self.events.append(dict(op='staged_transition',at=hex(stage),transition=transition))
   e.run(0x7b0b8,[(0,STATE)],stack_pointer=0x30010000)
   if transition=='suspend_resume':e.run(0x7b9a4,[(0,STATE)],stack_pointer=0x30010000)
   e.u.context_restore(saved);e.hit=None;e.stops={STOP};e.u.emu_start(stage,STOP+4,count=100000);assert e.hit==STOP
  return dict(final_parent=hex(self.parent),temporary_ownership_delta={hex(p):n for p,n in self.refs.items() if n},state_bytes=list(self.e.u.mem_read(STATE+0x50,5)),current_attempt=self.e.q(STATE+0x40),captured_attempt=self.e.q(BLOCK+32),events=self.events)
rows=[]
for build,m in [('original',O),('r03',P)]:
 for old_parent in [0,OLD,CHILD if m is O else GAME]:
  for stage in [None,0x769b4,0x76a78,0x76b5c,0x76be8,0x76c4c,0x76cf8,0x76d80]:
   for transition in ['suspend','suspend_resume'] if stage else ['none']:
    model=Model(m);model.parent=old_parent;r=model.run(stage,transition)
    assert model.parent==model.target
    moves=[x['selector'] for x in model.events if x.get('selector') in ['removeFromSuperview','addSubview:']]
    assert moves==([] if old_parent==model.target else ['removeFromSuperview','addSubview:'])
    if stage:assert r['current_attempt']!=r['captured_attempt'] and r['state_bytes'][0]==0
    expected={} if build=='original' else {hex(FIELD):1,hex(GAME):-1}
    assert r['temporary_ownership_delta']==expected
    rows.append(dict(test='acceptedCallbackAttachment',build=build,initial_parent=hex(old_parent),stage=hex(stage) if stage else None,transition=transition,**r))
 # Between removal and addition, only detached/wrong-parent cases can reach the stage.
 for stage in [0x76d38,0x76d48]:
  for transition in ['suspend','suspend_resume']:
   model=Model(m);model.parent=OLD;r=model.run(stage,transition);assert model.parent==model.target
   rows.append(dict(test='cancellationBetweenDetachAndAttach',build=build,stage=hex(stage),transition=transition,**r))
 # Return-value faults at modeled factory boundaries, without manufacturing exceptions.
 for fault in ['field','child','overlay','MenuWindow','DrawWindow','FloatView']:
  model=Model(m);model.parent=OLD;model.fault=fault;r=model.run();messages=[x for x in model.events if x['op']=='message'];adds=[x for x in messages if x['selector']=='addSubview:']
  if fault in ['field','child'] and build=='original':assert not adds
  elif fault=='overlay':assert len(adds)==1 and adds[0]['nil_child']
  else:assert model.parent==model.target
  rows.append(dict(test='constructorFactoryFailureBoundary',build=build,fault=fault,attempted_nil_child_add=any(x.get('nil_child') for x in adds),**r))
result=dict(passed=True,cases=len(rows),scope='Native constructor callback and sequential/staged native suspend/resume mutators; Objective-C factories, hierarchy effects, geometry getters/setters, ARC accounting, mutex boundaries and journal sink modeled. Factory/init internals and UIKit exceptions not executed. Paused native callback register context restored around a separate-stack native lifecycle mutator; no real concurrency or asynchronous block ownership.',records=rows)
(RESULTS/'attachment-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
