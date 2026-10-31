"""Native deferred setup routing and destructor/global-control boundaries."""
from pathlib import Path
import os,sys,json,struct,itertools
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-state'))
sys.path.insert(0,str(HERE.parent/'continuation-b'));from emulator import *
OBJECT=0x20080000;CONTROL=0x20081000;MAIN=0x20082000;DEADLINE=0x12345678
class Routes:
 def __init__(self,image,ready=False,lifecycle=False):
  self.e=E(image);self.e.ownership();self.ready=ready;self.lifecycle=lifecycle;self.scheduled=[];self.times=[];self.work=[]
  self.e.write(0xfd82e8,struct.pack('<Q',MAIN))
  for a,n in IMPORTS.items():
   if n=='_dispatch_time':self.e.calls[a]=self.time
   elif n=='_dispatch_after':self.e.calls[a]=self.after
  self.e.calls[0x394c8]=lambda e:e.set(0,self.ready)
  self.e.calls[0x3c674]=lambda e:e.set(0,self.lifecycle)
  self.e.calls[0x3973c]=lambda e:self.work.append('secondary work boundary, not executed')
 def time(self,e):
  assert e.get(0)==0 and e.get(1)==2000000000;self.times.append(dict(base='DISPATCH_TIME_NOW',delta_nanoseconds=e.get(1)));e.set(0,DEADLINE)
 def after(self,e):
  assert e.get(0)==DEADLINE and e.get(1)==MAIN and e.q(e.get(2)+16)==0x7bae0
  self.scheduled.append(dict(queue='imported main queue',block=hex(e.get(2)),invoke='0x7bae0',delay_nanoseconds=2000000000,delivery='not executed by scheduler'))
 def set_flags(self,gate,guard,request):
  for slot,v in [(0x10109c1,gate),(0x1010a2a,guard),(0x1010a37,request)]:self.e.write(slot,bytes([v]))
 def flags(self):return [self.e.byte(a) for a in [0x10109c1,0x1010a2a,0x1010a37]]
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  r=Routes(image)
  for _ in range(3):r.e.run(0x438dc)
  assert len(r.scheduled)==3
  rows.append(dict(test='nativeSecondaryTimerRequests',build=build,requests=3,scheduled=r.scheduled,times=r.times,coalescing_in_helper=False,real_execution_frequency_unknown=True))
  for gate,ready,guard,lifecycle,request in itertools.product([0,1],repeat=5):
   r=Routes(image,bool(ready),bool(lifecycle));r.set_flags(gate,guard,request);r.e.run(0x7bae0,[(0,0xfd9dd0)])
   scheduled=not gate and not ready
   invoked=not gate and ready and not (guard and lifecycle and request)
   assert len(r.scheduled)==int(scheduled) and len(r.work)==int(invoked)
   assert r.flags()==[gate,guard,request]
   rows.append(dict(test='nativeSecondaryCallbackRouting',build=build,startup_gate=gate,readiness_provider=bool(ready),secondary_guard=guard,lifecycle_provider=bool(lifecycle),secondary_request_byte=request,retry_scheduled=scheduled,work_boundary_reached=bool(invoked),flags_unchanged=True,genuine_readiness_or_work_not_executed=True))
  for name,address in [('OverlayView',0x687508),('MetalContext',0x12f140),('MetalBuffer',0x12a7ec)]:
   # Resolve the actual metadata rather than assuming a destructor address.
   method=next(m for m in objc_methods(image) if m['cls']==name and m['selector']=='.cxx_destruct');address=method['address']
   e=E(image);e.ownership();clears=[]
   for slot in [0x1011b68,0x1011e20,0x1011a18,0x1011be0]:e.write(slot,struct.pack('<Q',CONTROL))
   def strong(e):
    assert e.get(1)==0 and OBJECT<=e.get(0)<OBJECT+0x1000
    clears.append(hex(e.get(0)-OBJECT));e.write(e.get(0),bytes(8))
   for a,n in IMPORTS.items():
    if n=='_objc_storeStrong':e.calls[a]=strong
   e.run(address,[(0,OBJECT),(1,0)])
   assert all(e.q(a)==CONTROL for a in [0x1011b68,0x1011e20,0x1011a18,0x1011be0])
   assert clears
   rows.append(dict(test='nativeDestructorGlobalControlBoundary',build=build,cls=name,entry=hex(address),strong_field_offsets_cleared=clears,raw_control_globals_unchanged=True,actual_deallocation_or_pointer_lifetime_proven=False))
 assert len(rows)==72
 data=dict(passed=True,cases=len(rows),scope='72 paired native/model records: native secondary two-second main-queue timer helper and callback guards with genuine readiness/lifecycle/work boundaries modeled, and actual three ObjC destructor bodies. Synthetic input flags; no security/backend work executed or genuine success inferred. Native flag loads do not prove production callback timing. Destructors clear strong fields but do not clear tracked raw control globals; no complete allocation lifetime/free proof, actual dispatch/UIKit reentry/device timing.',records=rows)
 (RESULTS/'state-route-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
