"""Native Overlay path/IO setup; GUI creation and Foundation/allocator modeled."""
from pathlib import Path
import os,sys,json,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-h'))
sys.path.insert(0,str(HERE.parent/'continuation-g'))
from test_overlay_resources import *
CTX=0x20081000;IO=CTX+8;HOME=0x20089000;PATH1=0x20089100;PATH2=0x20089200
FMCLASS=0x20089300;FM=0x20089400;DATACLASS=0x20089500;DATA=0x20089600
UTF8=0x2008a000;COPY=0x2008b000;SENTINEL=0x2008c000
class Config(Overlay):
 def __init__(self,image,file_mode,pointer_mode):
  super().__init__(image,'resource_prefix_ready');self.file_mode=file_mode;self.pointer_mode=pointer_mode;self.gui=[];self.duplicates=[];self.file_creations=[]
  putq(self.e,0xff08f8,FMCLASS);putq(self.e,0xff0990,DATACLASS)
  self.e.write(UTF8,b'/modeled/home/Documents/imgui.ini\0')
  # Existing IO fields are intentionally nonzero to observe the native writes.
  putq(self.e,IO+0x18,SENTINEL);putq(self.e,IO+0x20,SENTINEL);putq(self.e,IO,0x99999999)
  self.e.calls[0x14e514]=self.compatibility_boundary
  self.e.calls[0x13813c]=self.context_boundary
  for a,n in IMPORTS.items():
   if n=='_NSHomeDirectory':self.e.calls[a]=lambda e:e.set(0,HOME)
   elif n=='_strdup':self.e.calls[a]=self.duplicate
   elif n=='_objc_retainAutorelease':self.e.calls[a]=lambda e:None
 def compatibility_boundary(self,e):
  self.gui.append(dict(boundary='0x14e514',arguments=[hex(e.get(i)) for i in range(7)]));e.set(0,1)
 def context_boundary(self,e):
  assert e.get(0)==0
  self.gui.append(dict(boundary='0x13813c',shared_font_atlas='0x0',modeled_current_context=hex(CTX)))
  putq(e,0x1011bf0,CTX);e.set(0,CTX)
 def duplicate(self,e):
  assert e.get(0)==UTF8;self.duplicates.append(e.cs(e.get(0)))
  if self.pointer_mode=='copy_nil':e.set(0,0)
  else:e.write(COPY,e.cs(UTF8).encode()+b'\0');e.set(0,COPY)
 def message(self,e):
  receiver=e.get(0);sel=e.cs(e.get(1));arg=e.get(2)
  if sel in ['stringByAppendingPathComponent:','defaultManager','fileExistsAtPath:','data','createFileAtPath:contents:attributes:','UTF8String']:
   self.events.append(dict(selector=sel,receiver=hex(receiver),argument=hex(arg)))
   assert receiver!=0
   if sel=='stringByAppendingPathComponent:':
    assert receiver in [HOME,PATH1]
    assert arg==(0xfddda0 if receiver==HOME else 0xfdf0a0)
    e.set(0,PATH1 if receiver==HOME else PATH2)
   elif sel=='defaultManager':assert receiver==FMCLASS;e.set(0,FM)
   elif sel=='data':assert receiver==DATACLASS;e.set(0,DATA)
   elif sel=='fileExistsAtPath:':assert receiver==FM and arg==PATH2;e.set(0,self.file_mode=='existing')
   elif sel=='createFileAtPath:contents:attributes:':
    assert receiver==FM and arg==PATH2 and e.get(3)==DATA and e.get(4)==0
    self.file_creations.append(self.file_mode=='create_true');e.set(0,self.file_creations[-1])
   elif sel=='UTF8String':assert receiver==PATH2;e.set(0,0 if self.pointer_mode=='utf8_nil' else UTF8)
   return
  return super().message(e)
ATLAS=0x2008d000;FONT1=0x2008e000;FONT3=0x2008f000;BACKEND=0x20090000
class Fonts(Config):
 def __init__(self,image,font_mode):
  super().__init__(image,'existing','copied');self.font_mode=font_mode;self.font_calls=[]
  putq(self.e,IO+0x48,ATLAS)
  self.e.calls[0x6601a0]=self.add_memory_font
  self.e.calls[0x660340]=self.add_compressed_font
  for a,n in IMPORTS.items():
   if n=='_memset':self.e.calls[a]=self.zero
 def zero(self,e):
  assert e.get(2)<=0x10000;e.write(e.get(0),bytes([e.get(1)&255])*e.get(2))
 def add_memory_font(self,e):
  assert e.get(0)==ATLAS
  role='primary' if not self.font_calls else 'merge'
  result=0 if (role=='primary' and self.font_mode in ['primary_nil','both_nil']) or (role=='merge' and self.font_mode=='merge_nil') else FONT1
  self.font_calls.append(dict(role=role,returned=hex(result),config=hex(e.get(3))))
  e.set(0,result)
 def add_compressed_font(self,e):
  assert e.get(0)==ATLAS
  result=0 if self.font_mode in ['third_nil','both_nil'] else FONT3
  self.font_calls.append(dict(role='third',returned=hex(result),config=hex(e.get(3))))
  e.set(0,result)
class Backend(Config):
 def __init__(self,image,helper_result):
  super().__init__(image,'existing','copied');self.helper_result=helper_result;self.backend_events=[]
  putq(self.e,0x1011bf0,CTX);self.e.write(IO+4,struct.pack('<I',0x20))
  self.e.calls[0x12f1b8]=self.registration
  self.e.calls[0x12a434]=self.device_objects
 def registration(self,e):
  self.backend_events.append(dict(boundary='registration',token=hex(e.get(0)),block=hex(e.get(1))))
  putq(e,0x1010c48,BACKEND)
 def device_objects(self,e):
  self.backend_events.append(dict(boundary='device-object-helper',device=hex(e.get(0)),returned=self.helper_result));e.set(0,self.helper_result)
 def message(self,e):
  if e.get(0)==BACKEND and e.cs(e.get(1))=='makeDeviceObjectsWithDevice:':
   self.backend_events.append(dict(selector='makeDeviceObjectsWithDevice:',device=hex(e.get(2))));e.set(0,0);return
  return super().message(e)
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for file_mode in ['existing','create_true','create_false']:
   for pointer_mode in ['copied','utf8_nil','copy_nil']:
    model=Config(image,file_mode,pointer_mode);hit,_=model.initialize(0x20071000,stop=0x684cec)
    e=model.e;assert hit==0x684cec
    assert e.q(0x1011bf0)==CTX and e.q(IO+0x20)==0
    assert int.from_bytes(e.u.mem_read(IO,4),'little')==0x200000
    assert e.q(IO+0x18)==(COPY if pointer_mode=='copied' else 0)
    assert len(model.duplicates)==int(pointer_mode!='utf8_nil')
    assert len(model.file_creations)==int(file_mode!='existing')
    assert 0x138548 in e.visited and 0x6876e8 in e.visited
    assert 0x65ef08 not in e.visited and 0x12a0c8 not in e.visited
    rows.append(dict(test='nativeOverlayConfigSetup',build=build,file_mode=file_mode,pointer_mode=pointer_mode,stop=hex(hit),gui_boundaries=model.gui,io=hex(IO),config_flags=hex(int.from_bytes(e.u.mem_read(IO,4),'little')),ini_filename=hex(e.q(IO+0x18)),log_filename=hex(e.q(IO+0x20)),file_creation_returns=model.file_creations,duplicate_inputs=model.duplicates,path_components=[cstr(image,q(image,a+16)) for a in [0xfddda0,0xfdf0a0]],events=[v for v in model.events if v['selector'] in ['stringByAppendingPathComponent:','defaultManager','fileExistsAtPath:','data','createFileAtPath:contents:attributes:','UTF8String']]))
 for build,image in [('original',O),('r03',P)]:
  for mode in ['ready','primary_nil','third_nil','both_nil','merge_nil']:
   model=Fonts(image,mode);hit,result=model.initialize(0x20071000,stop=0x684e74)
   success=mode in ['ready','merge_nil']
   assert hit==(0x684e74 if success else STOP)
   if not success:assert result==0
   assert [v['role'] for v in model.font_calls]==(['primary','third'] if mode in ['primary_nil','both_nil'] else ['primary','merge','third'])
   assert 0x65ee88 in model.e.visited and 0x674dc8 in model.e.visited
   assert 0x12a0c8 not in model.e.visited
   rows.append(dict(test='nativeFontReturnGuards',build=build,mode=mode,stop=hex(hit),returned=None if success else hex(result),font_providers=model.font_calls,constructors_native=True))
  for device in [0,DEVICE]:
   for helper_result in [0,1]:
    model=Backend(image,helper_result);returned=model.nested(0x12a0c8,[(0,device)])
    assert returned==1
    assert int.from_bytes(model.e.u.mem_read(IO+4,4),'little')==0x28
    assert model.e.q(IO+0x80)!=0
    assert 0x12a1cc in model.e.visited and 0x138548 in model.e.visited
    assert [v['device'] for v in model.backend_events if 'device' in v]==[hex(device),hex(device)]
    rows.append(dict(test='nativeBackendInitializerReturn',build=build,device=hex(device),subordinate_result=helper_result,returned=returned,backend_flags='0x28',backend_name=model.e.cs(model.e.q(IO+0x80)),events=model.backend_events))
 assert len(rows)==36
 checks=[]
 for lo,hi in [(0x6849f8,0x684cec),(0x6876e8,0x687770),(0x138548,0x1385c8),(0x684cec,0x684edc),(0x65ee88,0x65ef34),(0x12a0c8,0x12a254)]:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=True,sha256=hashlib.sha256(a).hexdigest()))
 result=dict(passed=True,cases=len(rows),scope='36 native/model records: 18 resource-ready native Overlay path/IO cases stopping at 0x684cec; 10 native font-constructor/return-guard cases stopping before syncOverlaySize at 0x684e74 or returning nil; 8 standalone native backend initializer/helper cases. GUI ABI/context creation, font-add providers, Foundation/ARC/allocation and backend registration/device-object work are modeled boundaries. Current-context getter, forwarding wrappers, font-config constructors, backend initializer 0x12a0c8 and helper 0x12a1cc execute natively. No full successful Overlay initializer, real GUI context/GPU/backend/device run, deallocation/lifetime/race proof or performance measurement.',code_equality=checks,records=rows)
 (RESULTS/'overlay-config-tests.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),equal_ranges=len(checks))))
if __name__=='__main__':main()
