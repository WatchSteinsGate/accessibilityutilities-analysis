"""Read-only queue-operand and callback-routing tests; no real scheduler/backend."""
from pathlib import Path
import sys,os,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-c'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from emulator import *
rows=[]
APP=0x20001000;CENTER=0x20002000;OPMAIN=0x20003000;ARRAY=0x20004000
MUT=0x20005000;TOKEN=0x20006000;CLASS=0x20007000
NOTIFICATIONS={0xfd80e8:('UIApplicationWillResignActiveNotification',0x7b114),0xfd80c8:('UIApplicationDidBecomeActiveNotification',0x7b77c),0xfd80d8:('UIApplicationDidEnterBackgroundNotification',0x7b7f0),0xfd80e0:('UIApplicationWillEnterForegroundNotification',0x7b864),0xfd8108:('UISceneDidActivateNotification',0x7b938),0xfd8120:('UISceneWillDeactivateNotification',0x7b938),0xfd8118:('UISceneDidEnterBackgroundNotification',0x7b938),0xfd8110:('UISceneDidDisconnectNotification',0x7b938)}
BLOCKS={0x7b114:0xfd9d10,0x7b77c:0xfd9d30,0x7b7f0:0xfd9d50,0x7b864:0xfd9d70,0x7b938:0xfd9d90}
def putq(e,a,v):e.write(a,struct.pack('<Q',v))
def setup(m):
 e=E(m);e.ownership();e.journal();e.noop([0x8766e4]);return e
for build,m in [('original',O),('r03',P)]:
 for state in [0,1,2]:
  for scenes in [False,True]:
   e=setup(m);registered=[];suspends=[];names={};scene_names=[]
   for i,(slot,(name,invoke)) in enumerate(NOTIFICATIONS.items()):
    cell=0x20010000+i*16;obj=0x20011000+i*16
    putq(e,slot,cell);putq(e,cell,obj);names[obj]=(name,invoke)
    if name.startswith('UIScene'):scene_names.append(obj)
   # Class-reference bindings are symbolic. Selectors/argument construction stay native.
   for slot in [0xff08f0,0xff0910,0xff0988,0xff08e0]:putq(e,slot,CLASS)
   def msg(e):
    sel=e.cs(e.get(1))
    if sel=='defaultCenter':e.set(0,CENTER)
    elif sel=='sharedApplication':e.set(0,APP)
    elif sel=='applicationState':assert e.get(0)==APP;e.set(0,state)
    elif sel=='mainQueue':e.set(0,OPMAIN)
    elif sel=='addObserverForName:object:queue:usingBlock:':
     assert e.get(0)==CENTER and e.get(3)==0 and e.get(4)==OPMAIN
     name,invoke=names[e.get(2)];assert e.q(e.get(5)+16)==invoke
     registered.append(dict(name=name,invoke=hex(invoke),queue='modeled main operation queue',object_filter=None));e.set(0,TOKEN)
    elif sel=='arrayWithObjects:count:':
     assert e.get(3)==4
     assert [e.q(e.get(2)+8*i) for i in range(4)]==scene_names;e.set(0,ARRAY)
    elif sel=='countByEnumeratingWithState:objects:count:':
     assert e.get(0)==ARRAY
     st,buf=e.get(2),e.get(3)
     if e.q(st):e.set(0,0)
     else:
      putq(e,st,1);putq(e,st+8,buf);putq(e,st+16,MUT)
      for i,obj in enumerate(scene_names):putq(e,buf+8*i,obj)
      e.set(0,4)
    else:raise AssertionError(('Unexpected selector',sel))
   for a,name in IMPORTS.items():
    if name=='_objc_msgSend':e.calls[a]=msg
    elif name=='_NSClassFromString':e.calls[a]=lambda e:e.set(0,CLASS if scenes else 0)
    elif name=='_memset':e.calls[a]=lambda e:e.write(e.get(0),bytes([e.get(1)&255])*e.get(2))
   # Initial suspend is deliberately a recorded boundary, not executed in this suite.
   e.calls[0x7b0b8]=lambda e:suspends.append(hex(e.get(0)))
   e.run(0x7aa4c,[(0,0x20008000)])
   assert len(registered)==(8 if scenes else 4)
   assert e.byte(0x1010a28)==(state==0)
   assert suspends==([] if state==0 else ['0xff2798'])
   rows.append(dict(test='observerRegistration',build=build,application_state=state,scene_class_available=scenes,ready=e.byte(0x1010a28),initial_suspend_boundary_calls=len(suspends),registrations=registered))
 for callback,block in BLOCKS.items():
  for pending in [0,1]:
   for argument in [0,0x20008000]:
    e=setup(m);transitions=[];queued=[];main=0x20009000
    e.write(0x1010a58,bytes([pending]));putq(e,0xfd82e8,main)
    e.calls[0x7b188]=lambda e:transitions.append(e.get(0)&1)
    def enqueue(e):
     assert e.get(0)==main
     queued.append(hex(e.q(e.get(1)+16)))
    e.calls[0x876258]=enqueue
    e.run(callback,[(0,block),(1,argument)])
    coalesced=callback in [0x7b864,0x7b938]
    assert transitions==([] if coalesced else [int(callback==0x7b77c)])
    assert queued==(['0x7ba04'] if coalesced and pending==0 else [])
    assert e.byte(0x1010a58)==(1 if coalesced else pending)
    rows.append(dict(test='notificationRouting',build=build,callback=hex(callback),notification_nil=argument==0,pending_before=pending,pending_after=e.byte(0x1010a58),transition_boundary_args=transitions,queued_invokes=queued,dispatch_queue='modeled main dispatch queue' if queued else None))
 for generation in [0,1,(1<<64)-1]:
  for main in [0x20009000,0x2000a000]:
   e=setup(m);putq(e,0xfd82e8,main);queued=[]
   # Execute only frame/queue-load prologue; skip the producer's backend body.
   e.run(0x70d00,stops=[0x70d38]);assert e.hit==0x70d38
   sp=e.u.reg_read(R.UC_ARM64_REG_SP);scratch=e.q(sp+0x538)
   assert e.q(sp+0x548)==main
   putq(e,scratch+0x2d0,generation)
   def enqueue(e):
    b=e.get(1)
    queued.append(dict(queue=hex(e.get(0)),invoke=hex(e.q(b+16)),captured_generation=e.q(b+32),flags=hex(struct.unpack('<I',e.u.mem_read(b+8,4))[0])))
   e.calls[0x876258]=enqueue
   # Resume a deliberately seeded block-construction excerpt, not backend success.
   e.hit=None;e.stops={0x7419c};e.u.emu_start(0x7413c,0x741a0,count=10000)
   assert e.hit==0x7419c
   assert queued==[dict(queue=hex(main),invoke='0x76944',captured_generation=generation,flags='0xc0000000')]
   rows.append(dict(test='constructorQueueOperand',build=build,seeded_generation=generation,main_queue_binding=hex(main),dispatch=queued[0],producer_body_executed=False))
assert len(rows)==64
scope='Native lifecycle observer initialization (12), callback routing (40), and constructor queue/block excerpts (12). UIKit/ObjC/class imports, ARC, enumeration, notification delivery and dispatch boundaries modeled. Initial suspend and full transition body not executed here. Producer backend body skipped; captured generation explicitly seeded. No real queue scheduling, reentrancy, backend success or device timing demonstrated.'
result=dict(passed=True,cases=len(rows),scope=scope,records=rows)
(RESULTS/'scheduling-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,cases=len(rows),scope=scope),indent=2))
