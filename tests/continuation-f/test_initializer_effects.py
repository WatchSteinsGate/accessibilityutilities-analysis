"""Full native Draw/Menu initializer bodies with explicit external boundaries."""
from pathlib import Path
import sys,os,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-f'))
sys.path.insert(0,str(HERE.parent/'continuation-e'))
from test_factories import *
HOME=0x20051000;PATH=0x20052000;MANAGER=0x20053000;DATA=0x20054000;INI=0x20055000;CPATH=0x20056000;ZERO=0x20057000
STATE=0xff2780
class Complete(Model):
 def __init__(self,image,role,fault='none',exists=True,created=True,loaded=False,read_value=1):
  super().__init__(image,role,fault);self.exists=exists;self.created=created;self.loaded=loaded;self.read_value=read_value
  self.effects=[];self.integers=[]
  putq(self.e,0xff08f8,0x20058000);putq(self.e,0xff0990,0x20059000)
  putq(self.e,0xfd8008,ZERO);self.e.write(ZERO,bytes(16));self.e.write(CPATH,b'modeled-preferences.ini\0')
  self.e.write(STATE,bytes(16));self.e.write(0x1011a28,b'\xa5'*16)
  for a,n in IMPORTS.items():
   if n=='_NSHomeDirectory':self.e.calls[a]=lambda e:e.set(0,HOME)
   elif n=='_objc_retainAutorelease':self.e.calls[a]=lambda e:None
  self.e.calls[0x855e50]=self.load_ini
  self.e.calls[0x8571d0]=self.read_integer
  self.e.calls[0x857384]=self.write_integer
 def load_ini(self,e):
  assert e.get(0)==CPATH;self.effects.append('ini_load boundary');e.set(0,INI if self.loaded else 0)
 def read_integer(self,e):
  assert e.get(0)==INI
  self.integers.append(dict(op='read',default=hex(e.get(3)&0xffffffff)))
  e.set(0,self.read_value)
 def write_integer(self,e):
  assert e.get(0)==INI
  self.integers.append(dict(op='write',value=e.get(3)&0xffffffff));e.set(0,1)
 def message(self,e):
  receiver=e.get(0);sel=e.cs(e.get(1))
  if not receiver:e.set(0,0);return
  if sel in ('init:','initWithFrame::','initWithFrame:'):
   self.initializations+=1;self.controls.append(hex(e.get(2)))
   return Work(CONFIG[self.role][2],(),False,None)
  if sel=='stringByAppendingPathComponent:':self.effects.append('path append');e.set(0,PATH)
  elif sel=='defaultManager':e.set(0,MANAGER)
  elif sel=='fileExistsAtPath:':self.effects.append('file existence boundary');e.set(0,self.exists)
  elif sel=='data':e.set(0,DATA)
  elif sel=='createFileAtPath:contents:attributes:':self.effects.append('file creation boundary');e.set(0,self.created)
  elif sel=='UTF8String':e.set(0,CPATH)
  else:super().message(e)
 def result(self):
  return dict(native_scope='full DrawWindow/MenuWindow initializer normal/false/nil-return paths',effects=self.effects,integers=self.integers,super_selectors=self.supers,setup_byte=self.e.byte(STATE+4),setting_byte=self.e.byte(STATE),published_draw_control=hex(self.e.q(0x1011a18)),reset_size=bytes(self.e.u.mem_read(0x1011a28,16)).hex())

rows=[]
for build,image in [('original',O),('r03',P)]:
 for control in [0,0x20021000]:
  for super_nil in [False,True]:
   model=Complete(image,'DrawWindow','super_nil' if super_nil else 'none')
   result=model.nested(0x10bc4,[(0,OBJ),(2,control)])
   assert result==(0 if super_nil else OBJ)
   assert model.e.q(0x1011a18)==control and model.e.byte(STATE+4)==1
   assert bytes(model.e.u.mem_read(0x1011a28,16))==bytes(16)
   assert all(a in model.e.visited for a in [0x10cac,0x18a00,0x18a0c])
   rows.append(dict(test='drawCompleteInitializer',build=build,super_nil=super_nil,control=hex(control),returned=hex(result),**model.result()))
 cases=[('existing_no_ini',True,True,False,1,False),('create_fails',False,False,False,1,False),('created_no_ini',False,True,False,1,False),('value_minus_one',True,True,True,-1,False),('value_zero',True,True,True,0,False),('value_one',True,True,True,1,False),('value_two',True,True,True,2,False),('late_super_nil',True,True,True,1,True),('created_loaded',False,True,True,1,False)]
 for label,exists,created,loaded,value,super_nil in cases:
  model=Complete(image,'MenuWindow','super_nil' if super_nil else 'none',exists,created,loaded,value)
  result=model.nested(0x617070,[(0,OBJ),(2,0x20021000)])
  assert result==(0 if super_nil else OBJ)
  assert model.supers==['init'] and model.effects.count('ini_load boundary')==1
  assert model.effects.count('file existence boundary')==1
  assert model.effects.count('file creation boundary')==int(not exists)
  assert model.e.q(0x1011c80)==(INI if loaded else 0)
  assert model.e.byte(STATE)==int(loaded and value==1)
  assert len([x for x in model.integers if x['op']=='read'])==int(loaded)
  writes=[x['value'] for x in model.integers if x['op']=='write']
  assert writes==([0] if loaded and value not in (0,1) else [])
  rows.append(dict(test='menuCompleteInitializer',build=build,case=label,returned=hex(result),**model.result()))
 for value in [-1,0,1,2]:
  model=Complete(image,'MenuWindow');model.nested(0x617420,[(0,value)])
  assert model.e.byte(STATE)==int(value==1)
  rows.append(dict(test='menuSettingNativeHelper',build=build,input=value,stored=model.e.byte(STATE)))
 for role in ['DrawWindow','MenuWindow']:
  for fault in ['none','allocation_nil','super_nil']:
   model=Complete(image,role,fault);cfg=CONFIG[role];returns=[]
   for control in [0x20021000,0x20022000,0x20023000]:returns.append(model.nested(cfg[0],[(0,0x20030000),(2,control)]))
   assert returns==([OBJ]*3 if fault=='none' else [0]*3)
   assert model.allocations==1 and model.initializations==int(fault!='allocation_nil') and len(model.once)==1
   if role=='DrawWindow':assert model.e.byte(STATE+4)==int(fault!='allocation_nil')
   else:assert model.effects.count('ini_load boundary')==int(fault!='allocation_nil')
   rows.append(dict(test='completeFactoryInitializerComposition',build=build,role=role,fault=fault,returns=[hex(x) for x in returns],allocations=model.allocations,initializer_calls=model.initializations,**model.result()))
assert len(rows)==46
ranges=[(0x10bc4,0x10cac),(0x10cac,0x10ce8),(0x617070,0x617420),(0x617420,0x617460)]
checks=[]
for lo,hi in ranges:
 a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
 checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=True,sha256=hashlib.sha256(a).hexdigest()))
result=dict(passed=True,cases=len(rows),scope='46 native/model cases: full DrawWindow and MenuWindow initializer bodies and selected native state setters/forwarders; full factory/once composition for both classes. Inherited ObjC init, ARC, filesystem/NSString/NSData, ini_load/read/write and once/allocation modeled; no real filesystem mutation, real queue delivery, exception handling, ownership/lifetime/reentry proof, backend/device run or timing.',code_equality=checks,records=rows)
(RESULTS/'initializer-tests.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print(json.dumps(dict(passed=True,cases=len(rows),equal_ranges=len(checks))))
