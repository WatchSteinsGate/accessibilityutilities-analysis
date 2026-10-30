from pathlib import Path
import struct,json
D=Path(__file__).parent
import os
OUT=Path(os.environ.get("AU_RESULTS",str(D.parent/"results/generated")));OUT.mkdir(parents=True,exist_ok=True)
env={'__file__':str(D/'test_view_lifecycle.py')};exec(compile((D/'test_view_lifecycle.py').read_text().split('\nrows=[]\n')[0],'view-model','exec'),env)
Model,O,P,SELF=env['Model'],env['O'],env['P'],env['SELF']
rows=[]
lo,hi=O.bounds(0x6855c0);assert O.bytes(lo,hi-lo)==P.bytes(lo,hi-lo)
for build,m in [('original',O),('r03',P)]:
 for main,busy in [(False,False),(False,True),(True,False),(True,True)]:
  model=Model(m);events=[];native_msg=model.e.calls[0x876624]
  def msg(e):
   s=model.sel(e.get(1));events.append(('selector',s))
   if s=='isMainThread':e.set(0,int(main))
   elif s=='overlaySizeSyncing':e.set(0,int(busy))
   else:native_msg(e)
  model.e.calls[0x876624]=msg;model.e.calls[0x876660]=lambda e:None
  def queue(e):
   block=e.get(1);events.append(('enqueue',hex(e.q(block+16)),hex(e.q(block+32))))
  model.e.calls[0x687938]=queue
  if main and not busy:
   # Stop before geometry work: tests this decision boundary only.
   model.e.stops.add(0x6856c0)
  for invocation in range(3):
   before=len(events);model.run(0x6855c0);new=events[before:]
   assert sum(ev[0]=='enqueue' for ev in new)==int(not main)
   if not main:assert new[-1]==('enqueue','0x685b98',hex(SELF))
   if main:assert model.e.hit==(0x3001f000 if busy else 0x6856c0)
   rows.append(dict(test='sizeSyncScheduling',build=build,main_thread=main,already_syncing=busy,invocation=invocation,events=new,geometry_entered=main and not busy))
 # Execute native async block invoke, stopping at ObjC selector boundary.
 model=Model(m);block=0x20008000;model.e.write(block+32,struct.pack('<Q',SELF));events=[]
 model.e.calls[0x876624]=lambda e:events.append((e.get(0),model.sel(e.get(1))))
 model.run(0x685b98,[(0,block)]);assert events==[(SELF,'syncOverlaySize')]
 rows.append(dict(test='sizeSyncCallback',build=build,events=events))
result=dict(passed=True,cases=len(rows),native_size_sync_identical_between_builds=True,scope='Original/R03 native thread/recursion guards and block construction/invoke. ObjC thread/busy results, ownership, dispatch enqueue and callback messaging modeled. Geometry path stopped before execution. No real asynchronous execution or race proof.',records=rows)
(OUT/'size-sync-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
