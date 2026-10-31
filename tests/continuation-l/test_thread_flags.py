"""Benign generic thread launch/atomic flag contracts; worker body never executes."""
from pathlib import Path
import os,sys,json,struct,itertools
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-thread'))
sys.path.insert(0,str(HERE.parent/'continuation-b'));from emulator import *
FLAG=0x1010a37;TID=0x20090000;SCOPE=0x20091000;ENTRY=0x4137c;THREAD=0xabc123
class Threads:
 def __init__(self,image,initial=0,create=0,detach=0):
  self.e=E(image);self.e.write(FLAG,bytes([initial]));self.e.write(TID,struct.pack('<Q',0x9876))
  self.create_result=create;self.detach_result=detach;self.created=[];self.detached=[]
  for a,n in IMPORTS.items():
   if n=='_pthread_create':self.e.calls[a]=self.create
   if n=='_pthread_detach':self.e.calls[a]=self.detach
 def create(self,e):
  assert [e.get(i) for i in range(4)]==[TID,0,ENTRY,0]
  assert e.byte(FLAG)==1
  self.created.append(dict(entry=hex(ENTRY),argument=0,flag_at_create=1,result=self.create_result))
  if self.create_result==0:e.write(TID,struct.pack('<Q',THREAD))
  e.set(0,self.create_result)
 def detach(self,e):
  assert e.get(0)==THREAD;self.detached.append(dict(thread_id=THREAD,result=self.detach_result));e.set(0,self.detach_result)
 def launch(self):
  result=self.e.run(0x104488,[(0,TID),(1,FLAG),(2,ENTRY)])
  assert ENTRY not in self.e.visited
  return result
 def acquire(self):
  self.e.run(0x2d3f0,[(0,SCOPE),(1,FLAG)])
  assert self.e.q(SCOPE)==FLAG and self.e.byte(FLAG)==1
 def cleanup(self,exceptional=False):
  self.e.run(0x3527c if exceptional else 0xf6694,[(0,SCOPE)])
  assert self.e.byte(FLAG)==0
 def snapshot(self):return dict(flag=self.e.byte(FLAG),thread_slot=self.e.q(TID),creates=list(self.created),detaches=list(self.detached))
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for initial,create,detach in itertools.product([0,1],[0,11],[0,22]):
   t=Threads(image,initial,create,detach);r=t.launch()
   assert r==int(initial==1 or create==0)
   assert len(t.created)==int(initial==0) and len(t.detached)==int(initial==0 and create==0)
   assert t.e.byte(FLAG)==int(initial==1 or create==0)
   assert t.e.q(TID)==(0x9876 if initial else (0 if create else THREAD))
   rows.append(dict(test='nativeThreadLaunchContract',build=build,initial_flag=initial,create_result=create,detach_result=detach,returned=bool(r),state=t.snapshot(),worker_not_executed=True))
  for name in ['duplicate','failureThenRetry','cleanupThenRelaunch']:
   t=Threads(image,create=11 if name=='failureThenRetry' else 0)
   first=t.launch()
   if name=='failureThenRetry':t.create_result=0
   if name=='cleanupThenRelaunch':t.acquire();t.cleanup()
   second=t.launch()
   expected=1 if name=='duplicate' else 2
   assert len(t.created)==expected and second==1
   rows.append(dict(test='nativeThreadSequence',build=build,sequence=name,returns=[bool(first),bool(second)],state=t.snapshot(),worker_not_executed=True,scope_delivery_manual=name=='cleanupThenRelaunch'))
  for initial,exceptional in itertools.product([0,1],repeat=2):
   t=Threads(image,initial);t.acquire();t.cleanup(bool(exceptional))
   assert not t.created
   rows.append(dict(test='nativeWorkerScopeFlagHelpers',build=build,initial_flag=initial,cleanup='exception edge helper' if exceptional else 'normal edge helper',constructor_sets_one=True,cleanup_sets_zero=True,scope_pointer_retained=t.e.q(SCOPE)==FLAG,worker_body_and_exception_unwinding_not_executed=True))
 assert len(rows)==30
 data=dict(passed=True,cases=len(rows),scope='30 paired native/model records. Native launch wrappers, compare-exchange and atomic stores execute; pthread_create/detach are explicit providers and never execute the worker. Native worker scope constructor and normal/exception-edge cleanup helpers delivered manually, not worker completion or unwinder evidence. No real threading, fairness, mutex/atomic race correctness, launch frequency, backend/security success or iOS runtime behavior established.',records=rows)
 (RESULTS/'thread-flag-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
