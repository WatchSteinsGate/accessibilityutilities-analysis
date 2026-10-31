"""Native cache insertion, budget, purge and best-fit caller contracts."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-cache'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from emulator import *
CONTEXT=0x20010000;CACHE=0x20011000;TEMP=0x20012000;DATECLASS=0x20013000;DATE=0x20014000;ARRAYCLASS=0x20015000;DEVICE=0x20016000;WRAPCLASS=0x20017000;NEW=0x20018000;NEWBUF=0x20019000;MUT=0x2001a000
class Cache:
 emulator_class=E
 def __init__(self,image,lengths=(),now=100.,last_purge=100.,times=None,allocation=True):
  self.e=self.emulator_class(image);self.e.ownership();self.cache=[];self.arrays={CACHE:self.cache,TEMP:[]};self.buffers={};self.times={};self.now=now;self.last_purge=last_purge;self.events=[];self.locks=0;self.allocation=allocation
  self.e.write(MUT,struct.pack('<Q',1))
  for slot,value in [(0xff0a58,DATECLASS),(0xff09d0,ARRAYCLASS),(0xff0a68,WRAPCLASS)]:self.e.write(slot,struct.pack('<Q',value))
  for i,length in enumerate(lengths):
   w=0x20020000+i*0x200;b=w+0x100;self.cache.append(w);self.buffers[w]=(b,length);self.times[w]=0. if times is None else times[i]
  for a,n in IMPORTS.items():
   if n=='_objc_msgSend':self.e.calls[a]=self.msg
   elif n=='_objc_sync_enter':self.e.calls[a]=self.enter
   elif n=='_objc_sync_exit':self.e.calls[a]=self.exit
   elif n=='_memset':self.e.calls[a]=lambda e:e.write(e.get(0),bytes([e.get(1)&255])*e.get(2))
   elif n=='_objc_alloc':self.e.calls[a]=self.alloc
 def enter(self,e):
  assert e.get(0)==CONTEXT and self.locks==0;self.locks+=1;self.events.append('lock');e.set(0,0)
 def exit(self,e):
  assert e.get(0)==CONTEXT and self.locks==1;self.locks-=1;self.events.append('unlock');e.set(0,0)
 def alloc(self,e):
  assert e.get(0)==WRAPCLASS;e.set(0,NEW)
 def fp(self,v):self.e.u.reg_write(R.UC_ARM64_REG_D0,struct.unpack('<Q',struct.pack('<d',v))[0])
 def fg(self):return struct.unpack('<d',struct.pack('<Q',self.e.u.reg_read(R.UC_ARM64_REG_D0)))[0]
 def msg(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if not r:e.set(0,0);return
  if s=='buffer':assert r in self.buffers;e.set(0,self.buffers[r][0]);return
  if s=='length':
   lengths=[length for b,length in self.buffers.values() if b==r];assert lengths;e.set(0,lengths[0]);return
  if r==CONTEXT and s=='bufferCache':e.set(0,CACHE);return
  if s=='countByEnumeratingWithState:objects:count:':
   assert r in self.arrays and e.get(4)==16
   state=a;index=e.q(state);items=self.arrays[r][index:index+16];base=e.get(3)
   for i,w in enumerate(items):e.write(base+8*i,struct.pack('<Q',w))
   e.write(state,struct.pack('<3Q',index+len(items),base,MUT));e.set(0,len(items));return
  if s=='count':assert r in self.arrays;e.set(0,len(self.arrays[r]));return
  if r==DATECLASS and s=='date':e.set(0,DATE);return
  if r==DATE and s=='timeIntervalSince1970':self.fp(self.now);return
  if s=='setLastReuseTime:':self.times[r]=self.fg();self.events.append('timestamp');return
  if s=='lastReuseTime':assert r in self.times;self.fp(self.times[r]);return
  if r==CONTEXT and s=='lastBufferCachePurge':self.fp(self.last_purge);return
  if r==CONTEXT and s=='setLastBufferCachePurge:':self.last_purge=self.fg();return
  if r==ARRAYCLASS and s=='array':self.arrays[TEMP]=[];e.set(0,TEMP);return
  if s=='addObject:':assert r in self.arrays;self.arrays[r].append(a);self.events.append('insert');return
  if s=='mutableCopy':
   assert r==TEMP;self.cache[:]=self.arrays[TEMP];e.set(0,CACHE);return
  if r==CONTEXT and s=='setBufferCache:':assert a==CACHE;return
  if s=='removeObjectIdenticalTo:':
   assert r==CACHE;self.cache[:]=[w for w in self.cache if w!=a];self.events.append('remove');return
  if r==DEVICE and s=='newBufferWithLength:options:':
   assert self.locks==0 and e.get(3)==0
   self.events.append('allocate-after-unlock');self.buffers[NEW]=(NEWBUF if self.allocation else 0,a);e.set(0,NEWBUF if self.allocation else 0);return
  if r==NEW and s=='initWithBuffer:':
   self.events.append('modeled-wrapper-init');assert a==self.buffers[NEW][0];e.set(0,NEW);return
  raise AssertionError(('Unknown cache selector',hex(r),s))
 def enqueue(self,length):
  w=0x20040000;self.buffers[w]=(w+0x100,length);self.times[w]=0.
  self.e.run(0x12c06c,[(0,CONTEXT),(1,0),(2,w)]);assert self.locks==0
  return w in self.cache
 def dequeue(self,length):
  result=self.e.run(0x12b6f4,[(0,CONTEXT),(1,0),(2,length),(3,DEVICE)]);assert self.locks==0;return result
 def values(self):return [self.buffers[w][1] for w in self.cache]
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for lengths,incoming in [((),1),((1,)*7,1),((1,)*8,1),((0x1000000-1,),1),((0x1000000,),0),((0x1000000,),1),((10,),0x1000000),((10,),0x1000001)]:
   m=Cache(image,lengths);before=m.values();accepted=m.enqueue(incoming)
   expected=incoming<=0x1000000 and len(lengths)<8 and sum(lengths)+incoming<=0x1000000
   assert accepted==expected and m.values()==list(lengths)+([incoming] if accepted else [])
   rows.append(dict(test='nativeCacheBudgetInsertion',build=build,before=before,incoming=incoming,accepted=accepted,after=m.values(),events=m.events,locks_balanced=True))
  for lengths,requested in [((),1),((64,128,96),65),((128,96,96),65),((64,128),128),((64,128),129),((0,1),0),((0x1000000,),0x1000000)]:
   m=Cache(image,lengths);old=list(m.cache);result=m.dequeue(requested)
   candidates=[w for w in old if m.buffers[w][1]>=requested]
   want=min(candidates,key=lambda w:m.buffers[w][1]) if candidates else NEW
   assert result==want and result not in m.cache
   assert ('allocate-after-unlock' in m.events)==(not candidates)
   rows.append(dict(test='nativeCacheBestFit',build=build,lengths=list(lengths),requested=requested,returned_length=m.buffers[result][1],allocated=not candidates,remaining=m.values(),events=m.events))
  for age,times in [(1.,[99.,100.,101.]),(1.000001,[99.,100.,101.]),(2.,[0.,0.,0.])]:
   m=Cache(image,[64,128,256],now=100.+age,last_purge=100.,times=times);m.dequeue(999)
   expected=[size for size,t in zip([64,128,256],times) if t>100.] if age>1 else [64,128,256]
   assert m.values()==expected and m.last_purge==(100.+age if age>1 else 100.)
   rows.append(dict(test='nativeCachePurgeThreshold',build=build,elapsed=age,times=times,remaining=m.values(),last_purge=m.last_purge))
  # Same wrapper can be enqueued twice: no deduplication in this native caller.
  m=Cache(image);assert m.enqueue(32) and m.enqueue(32) and m.values()==[32,32]
  rows.append(dict(test='nativeDuplicateCacheAdmission',build=build,remaining=m.values(),real_duplicate_delivery_established=False))
  # GPU nil is not automatically a nil wrapper in the explicit runtime provider.
  m=Cache(image,allocation=False);ret=m.dequeue(10);assert ret==NEW and m.buffers[ret][0]==0
  rows.append(dict(test='nativeCacheAllocationNilBoundary',build=build,returned_wrapper_nonnull=True,underlying_buffer_nil=True,wrapper_initializer_modeled=True,events=m.events))
 assert len(rows)==40
 checks=[]
 for lo,hi in [(0x12b6f4,0x12c06c),(0x12c06c,0x12c798)]:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b;checks.append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=hashlib.sha256(a).hexdigest(),equal=True))
 data=dict(passed=True,cases=len(rows),scope='40 native/model records. Native enqueue/dequeue caller bodies execute normal return, accepted enumeration, 8-entry/16MiB budgets, best-fit selection, timestamp/purge and native synchronization calls. Foundation arrays/dates/fast enumeration, ARC, lock effects, buffer getters and new wrapper construction modeled. Synthetic contents/time; no actual concurrency, real mutex blocking, allocator/Metal/GPU failure or lifetime proof.',code_equality=checks,records=rows)
 (RESULTS/'cache-policy-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
