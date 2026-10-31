"""Native Float/Overlay byte-zero writers with explicit GUI/gesture providers."""
from pathlib import Path
import os,sys,json,struct,itertools,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-m-writers'))
sys.path.insert(0,str(HERE.parent/'continuation-b'));from emulator import *
CONTROL=0x200b0000;GUI=0x200b1000;OBJ=0x200b3000;GESTURE=0x200b4000;RESET=0x1010c30
class Writers:
 def __init__(self,image,value=0,pointer=True,begin=True,clicked=True,style=1):
  self.e=E(image);self.e.ownership();self.events=[];self.begin=begin;self.clicked=clicked;self.style=style;self.gesture_state=3
  self.e.write(CONTROL,bytes([value])+bytes(255));self.e.write(GUI,bytes(0xe00))
  for slot in [0x1011be0,0x1011e20]:self.e.write(slot,struct.pack('<Q',CONTROL if pointer else 0))
  self.e.calls[0x1386d8]=lambda e:e.set(0,0)
  self.e.calls[0x138548]=lambda e:e.set(0,GUI)
  self.e.calls[0x123490]=self.flags
  for a in [0x13fc1c,0x14cb88,0x14ca90,0x14cb1c]:self.e.calls[a]=lambda e:None
  self.e.calls[0x13fcfc]=self.begin_window
  self.e.calls[0x123568]=lambda e:e.set(0,self.style)
  self.e.calls[0x68ad54]=lambda e:self.events.append('modeled-image-button')
  self.e.calls[0x12422c]=lambda e:self.events.append('modeled-image')
  self.e.calls[0x124250]=self.click
  self.e.calls[0x144a68]=lambda e:self.events.append('modeled-End')
  for a,n in IMPORTS.items():
   if n=='_objc_msgSend':self.e.calls[a]=self.msg
 def flags(self,e):self.events.append('modeled-window-flags')
 def begin_window(self,e):self.events.append('modeled-Begin');e.set(0,self.begin)
 def click(self,e):assert e.get(0)==0;self.events.append('modeled-IsItemClicked');e.set(0,self.clicked)
 def msg(self,e):
  if not e.get(0):e.set(0,0);return
  s=e.cs(e.get(1))
  if e.get(0)==GESTURE and s=='state':e.set(0,self.gesture_state);return
  raise AssertionError(('Unknown writer selector',hex(e.get(0)),s))
 def value(self):return self.e.byte(CONTROL)
 def reset(self):self.e.run(0x12309c,[(0,OBJ),(1,0)])
 def draw(self):self.e.run(0x1230e4,[(0,OBJ),(1,0)])
 def shortcut(self,state=3):self.gesture_state=state;self.e.run(0x686f8c,[(0,OBJ),(1,0),(2,GESTURE)])
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for value,pointer in itertools.product([0,2,255],[False,True]):
   m=Writers(image,value,pointer);m.e.write(RESET,b'\0');m.reset()
   assert m.value()==(0 if pointer else value) and m.e.byte(RESET)==1
   rows.append(dict(test='nativeFloatResetWriter',build=build,before=value,pointer_nonnull=pointer,after=m.value(),reset_flag=1))
  for reset,begin,click,pointer,style in itertools.product([0,1],[False,True],[False,True],[False,True],[1,3]):
   m=Writers(image,254,pointer,begin,click,style);m.e.write(RESET,bytes([reset]));m.draw()
   active=build=='original'
   assert m.value()==(1 if active and begin and click and pointer else 254)
   assert m.e.byte(RESET)==(0 if active and begin else reset)
   assert m.events.count('modeled-End')==int(active) and m.events.count('modeled-IsItemClicked')==int(active and begin)
   if not active:assert m.e.visited=={0x1230e4,STOP}
   rows.append(dict(test='nativeFloatDrawClickWriter',build=build,reset_before=reset,begin_provider=begin,clicked_provider=click,pointer_nonnull=pointer,style_provider=style,native_entry_immediate_return=not active,after=m.value(),reset_after=m.e.byte(RESET),events=m.events))
  for state,value,pointer in itertools.product(range(6),[0,2,255],[False,True]):
   m=Writers(image,value,pointer);m.shortcut(state)
   assert m.value()==(1 if state==3 and pointer else value)
   rows.append(dict(test='nativeOverlayShortcutGestureWriter',build=build,gesture_state_provider=state,before=value,pointer_nonnull=pointer,after=m.value(),whole_byte_set_not_xor=state==3 and pointer))
  for sequence in ['resetThenDraw','drawThenReset','resetThenShortcut','shortcutThenReset']:
   m=Writers(image,254)
   if sequence=='resetThenDraw':m.reset();m.draw()
   elif sequence=='drawThenReset':m.draw();m.reset()
   elif sequence=='resetThenShortcut':m.reset();m.shortcut()
   else:m.shortcut();m.reset()
   assert m.value()==(1 if sequence=='resetThenShortcut' or (sequence=='resetThenDraw' and build=='original') else 0)
   rows.append(dict(test='nativeSharedControlSequentialWriters',build=build,sequence=sequence,after=m.value(),same_pointer_manually_seeded=True,real_ordering_not_established=True))
 assert len(rows)==156,len(rows)
 checks=[]
 for lo in [0x12309c,0x1230e4,0x686f8c]:
  _,hi=O.bounds(lo);a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert (a==b)==(lo!=0x1230e4)
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest(),equal=a==b,expected_discrepancy=lo==0x1230e4))
 data=dict(passed=True,cases=len(rows),scope='156 paired native/model records. Complete original Float reset/draw and Overlay shortcut bodies execute; R03 drawFloatWindow returns immediately at entry, so no original draw providers/writer execute on normal invocation; GUI/ImGui calls, style, Begin/click and ObjC gesture/ARC are explicit providers. Native reset writes whole byte zero, admitted Float click and state-3 shortcut write whole byte one, unlike R03 XOR tap. Synthetic pointers/values/manual call order; no GUI event delivery, validity/lifetime, runtime ordering/race, actual off-main callback or FPS cause established.',code_equality=checks,records=rows)
 (RESULTS/'control-writer-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
