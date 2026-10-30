from emulator import *
from collections import Counter
D=Path(__file__).parent;CONTEXT=0x20030000;WRAPPER=0x20031000;BUFFER=0x20032000
rows=[]
for build,m in [('original',O),('r03',P)]:
 for name,wrapper,buffer,length,accept in [('nil_wrapper',0,BUFFER,1,False),('nil_buffer',WRAPPER,0,1,False),('zero_length',WRAPPER,BUFFER,0,True),('one_byte',WRAPPER,BUFFER,1,True),('below_limit',WRAPPER,BUFFER,0xffffff,True),('at_limit',WRAPPER,BUFFER,0x1000000,True),('above_limit',WRAPPER,BUFFER,0x1000001,False),('max_unsigned',WRAPPER,BUFFER,(1<<64)-1,False)]:
  e=E(m);refs=Counter();events=[]
  def strong(e):
   old=e.q(e.get(0));new=e.get(1)
   if old:refs[old]-=1
   if new:refs[new]+=1
   e.write(e.get(0),struct.pack('<Q',new))
  def retain(e):
   if e.get(0):refs[e.get(0)]+=1
  def release(e):
   if e.get(0):refs[e.get(0)]-=1
  def msg(e):
   sel=e.cs(e.get(1));events.append(sel)
   assert sel in ['buffer','length']
   e.set(0,buffer if sel=='buffer' else length)
  for a,n in IMPORTS.items():
   if n=='_objc_storeStrong':e.calls[a]=strong
   elif n=='_objc_retainAutoreleasedReturnValue':e.calls[a]=retain
   elif n=='_objc_release':e.calls[a]=release
   elif n=='_objc_msgSend':e.calls[a]=msg
  e.run(0x12c06c,[(0,CONTEXT),(1,0),(2,wrapper)],stops=[0x12c27c]);assert (e.hit==0x12c27c)==accept
  delta={hex(p):v for p,v in refs.items() if v};assert delta==({hex(WRAPPER):1} if accept else {})
  rows.append(dict(test='bufferCacheAdmissionPrefix',build=build,case=name,length=length,entered_cache_body=accept,temporary_ownership_delta=delta,events=events))
result=dict(passed=True,cases=len(rows),scope='Native enqueueReusableBuffer: entry guard and rejecting normal exits, or stop before accepted cache-body synchronization. Underlying buffer/length getters and ARC accounting modeled. Accepted cache insertion, locking, enumeration, capacity policy and real allocator/Metal behavior not executed.',records=rows)
(RESULTS/'cache-guard-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
