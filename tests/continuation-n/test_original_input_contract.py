"""Original input pass-through policy versus R03 modal replacement; no latency tests."""
from pathlib import Path
import os,sys,json,struct,itertools
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-n-input'))
sys.path.insert(0,str(HERE.parent/'continuation-b'));from emulator import *
SELF=0x200d0000;CHILD=0x200d1000;CONTROL=0x200d2000;EVENT=0x200d3000
class Input:
 def __init__(self,image,super_result,control,opened):
  self.e=E(image);self.e.ownership();self.super_result=super_result;self.requests=[]
  self.e.write(0x1011e20,struct.pack('<Q',CONTROL if control else 0));self.e.write(CONTROL,bytes([opened]))
  for a,n in IMPORTS.items():
   if n=='_objc_msgSendSuper2':self.e.calls[a]=self.super_call
 def super_call(self,e):
  assert e.q(e.get(0))==SELF and e.cs(e.get(1))=='hitTest:withEvent:' and e.get(2)==EVENT
  point=[struct.unpack('<d',struct.pack('<Q',e.u.reg_read(getattr(R,'UC_ARM64_REG_D'+str(i)))))[0] for i in [0,1]]
  assert point==[5.,7.];self.requests.append(dict(point=point,event=hex(EVENT)));e.set(0,self.super_result)
 def run(self):
  for i,v in enumerate([5.,7.]):self.e.u.reg_write(getattr(R,'UC_ARM64_REG_D'+str(i)),struct.unpack('<Q',struct.pack('<d',v))[0])
  return self.e.run(0x687130,[(0,SELF),(1,0),(2,EVENT)])
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for super_result,control,opened in itertools.product([0,SELF,CHILD],[False,True],[0,1]):
   m=Input(image,super_result,control,opened);got=m.run()
   expected_original=CHILD if super_result==CHILD else 0
   divergence=build=='r03' and super_result==SELF and control and opened==1
   assert got==(SELF if divergence else expected_original) and len(m.requests)==1
   rows.append(dict(test='nativeOriginalInputPassThroughContract',build=build,super_result=hex(super_result),control_present=control,menu_open_bit=opened,returned=hex(got),original_policy_result=hex(expected_original),preserves_original_policy=got==expected_original,expected_policy_change=bool(divergence),super_requests=m.requests))
 assert len(rows)==24
 data=dict(passed=True,cases=24,scope='Original-success functional preservation audit, not FPS/crash/latency testing. Actual Overlay hitTest body and existing R03 observation/modal trampolines execute with symbolic super hit-test return, point/event forwarding and ARC providers. Original nil/self hits pass through as nil, child hit returned; R03 open-menu self hit returns overlay instead. Expected policy divergence is not preservation success. No actual touch dispatch, hierarchy, UIKit/ARC or exception/device behavior.',records=rows)
 (RESULTS/'original-input-contract-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=24,expected_original_policy_divergences=sum(r['expected_policy_change'] for r in rows))))
if __name__=='__main__':main()
