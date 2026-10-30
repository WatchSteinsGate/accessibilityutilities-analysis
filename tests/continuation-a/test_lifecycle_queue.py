from emulator import *
import itertools
D=Path(__file__).parent;rows=[]
for build,m in [('original',O),('r03',P)]:
 e=E(m);e.ownership();enqueued=[];transitions=[];app=[0];messages=[]
 def dispatch(e):
  block=e.get(1);enqueued.append(dict(block=block,invoke=e.q(block+16)))
 def msg(e):
  sel=e.cs(e.get(1));messages.append(sel)
  if sel=='sharedApplication':e.set(0,0x20005000)
  elif sel=='applicationState':e.set(0,app[0])
  else:raise AssertionError(sel)
 e.calls[0x876258]=dispatch;e.calls[0x876624]=msg;e.calls[0x7b188]=lambda e:transitions.append(e.get(0)&1)
 assert e.q(0xfd9db0+16)==0x7ba04
 for blocked,other,appstate in itertools.product([0,1],[0,1],[0,1,2]):
  e.write(0x1010a58,b'\0');e.write(0x10109c1,bytes([blocked]));e.write(0x1010a29,bytes([other]));enqueued.clear();transitions.clear();messages.clear()
  for _ in range(3):e.run(0x7b8d0)
  assert len(enqueued)==1 and e.byte(0x1010a58)==1
  assert enqueued[0]['invoke']==0x7ba04
  # State is deliberately changed after enqueue to prove drain-time sampling.
  app[0]=appstate;e.run(0x7ba04,[(0,enqueued[0]['block'])])
  assert e.byte(0x1010a58)==0
  want=[] if blocked or other else [int(appstate==0)]
  assert transitions==want
  assert messages==([] if blocked or other else ['sharedApplication','applicationState'])
  # A completed or guarded callback permits a later enqueue request.
  e.run(0x7b8d0);assert len(enqueued)==2
  rows.append(dict(test='lifecycleCoalescingAndDrain',build=build,blocking_flag=blocked,secondary_blocking_flag=other,drain_application_state=appstate,requests_before_drain=3,enqueues_before_drain=1,transition_arguments=transitions.copy(),messages=messages.copy(),requeue_after_drain=True))
result=dict(passed=True,cases=len(rows),scope='Native coalescing helper and lifecycle callback; dispatch enqueue, Objective-C, ARC boundaries and final transition callee modeled. Application state changed after enqueue. No actual threads/queues/race proof; final 0x7b188 transition body not executed here.',records=rows)
(RESULTS/'lifecycle-queue-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
