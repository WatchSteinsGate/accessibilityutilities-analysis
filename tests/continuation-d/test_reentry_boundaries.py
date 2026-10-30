"""Read-only native routing; queue delivery and Objective-C effects are modeled."""
from pathlib import Path
import sys, os, json, struct
HERE = Path(__file__).resolve().parent
os.environ.setdefault("AU_RESULTS", str(HERE.parents[1]/"results/generated/continuation-d"))
sys.path.insert(0, str(HERE.parent/"continuation-b"))
from emulator import *
from test_attachment import Model, BLOCK, CHILD, GAME, OLD, CTRL

MASK = (1 << 64) - 1
rows = []
def putq(e, address, value):
 e.write(address, struct.pack("<Q", value))

for build, image in [("original", O), ("r03", P)]:
 # Run the actual image initializer through its enqueue boundary. No queue is drained.
 for queue in [0x2000c000, 0x2000d000]:
  e = E(image); e.ownership(); queued = []
  putq(e, 0xfd82e8, queue)
  def enqueue(e):
   queued.append(dict(queue=hex(e.get(0)), block=hex(e.get(1)), invoke=hex(e.q(e.get(1)+16))))
  e.calls[0x876258] = enqueue
  e.run(0x43850)
  assert queued == [dict(queue=hex(queue), block="0xfd99d0", invoke="0x4388c")]
  assert 0xf6ccc in e.visited and 0xf6ce4 in e.visited
  rows.append(dict(test="startupMainEnqueue", build=build, queue_binding=hex(queue), queued=queued, delivered=False))

 # Run the queued callback through native once helpers, recording dispatch_once only.
 # Completing a once token here is a model; observer body/delivery is not executed.
 for initial_token in [0, MASK]:
  e = E(image); e.ownership(); once = []; secondary = []
  putq(e, 0x1010a50, initial_token)
  def once_boundary(e):
   once.append(dict(token=hex(e.get(0)), block=hex(e.get(1)), invoke=hex(e.q(e.get(1)+16))))
   putq(e, e.get(0), MASK)
  e.calls[0x876294] = once_boundary
  e.calls[0x438dc] = lambda e: secondary.append("secondary setup boundary")
  for _ in range(2): e.run(0x4388c, [(0, 0xfd99d0)])
  expected = [] if initial_token == MASK else [dict(token="0x1010a50", block="0xfd9cd0", invoke="0x7aa4c")]
  assert once == expected and len(secondary) == 2 and e.q(0x1010a50) == MASK
  rows.append(dict(test="startupRegistrationOnceRouting", build=build, initial_token=hex(initial_token), sequential_calls=2, once_boundary_calls=once, secondary_boundary_calls=len(secondary), observer_body_executed=False))

 # Wrapper argument forwarding, not execution of full lifecycle transition bodies.
 for wrapper, target, boolean in [(0x10791c,0x7b0b8,False),(0x10792c,0x7b0b8,False),(0x107bf4,0x7b188,True),(0x107c08,0x7b188,True)]:
  for argument in [0,1,2,MASK]:
   e = E(image); seen = []
   e.calls[target] = lambda e: seen.append(e.get(0))
   e.run(wrapper, [(0,argument)])
   expected = (argument & 1) if boolean else argument
   assert seen == [expected]
   rows.append(dict(test="lifecycleWrapperForwarding",build=build,entry=hex(wrapper),terminal=hex(target),input=hex(argument),forwarded=hex(expected),terminal_body_executed=False))

 # Full native admitted callback, without staged lifecycle mutation. All Objective-C
 # methods use Model's explicit stubs; this cannot demonstrate absence of reentry.
 for initial_parent in [0, OLD, CHILD if image is O else GAME]:
  for control in [CTRL, CTRL+16]:
   model = Model(image); model.parent = initial_parent
   putq(model.e, 0x1011b68, control)
   returns = []; original_message = model.e.calls[0x876624]
   def record_message(e):
    returns.append(dict(selector=e.cs(e.get(1)),return_pc=hex(e.get(30)),control_argument=hex(e.get(2))))
    original_message(e)
   model.e.calls[0x876624] = record_message
   result = model.run()
   assert model.parent == model.target
   shared = [v for v in returns if v["selector"] in ("sharedInstance:","sharedInstance:::::")]
   assert len(shared) == 4 and all(v["control_argument"] == hex(control) for v in shared)
   # Native forwarding veneers are traversed, not replaced with entry stubs.
   for address in [0x105cec,0x105cdc,0x105d0c,0x105cfc,0x105d2c,0x105d1c,0x105d4c,0x105d3c,0x76e20]:
    assert address in model.e.visited
   rows.append(dict(test="constructorSynchronousBoundaries",build=build,initial_parent=hex(initial_parent),seeded_control=hex(control),global_pointer_slot="0x1011b68",messages=returns,final_parent=result["final_parent"],temporary_ownership_delta=result["temporary_ownership_delta"],staged_mutation=False,objc_implementations_executed=False))

 # The local rectangle helper copies four scalar bit patterns without any call.
 for values in [(0.,0.,320.,240.),(11.,17.,0.,0.),(-1.,-2.,-3.,-4.)]:
  e = E(image)
  for i,value in enumerate(values): e.u.reg_write(getattr(R,"UC_ARM64_REG_D"+str(i)), struct.unpack("<Q",struct.pack("<d",value))[0])
  e.run(0x76e20)
  output = [struct.unpack("<d",struct.pack("<Q",e.u.reg_read(getattr(R,"UC_ARM64_REG_D"+str(i)))))[0] for i in range(4)]
  assert output == list(values)
  rows.append(dict(test="rectangleHelper",build=build,input=list(values),output=output))

assert len(rows) == 58
scope = "58 scoped native/model cases: startup enqueue (4), queued callback/once routing (4), lifecycle forwarding veneers (32), admitted constructor synchronous messages (12), scalar rectangle helper (6). Dispatch/once token completion, ObjC factories/hierarchy/geometry, ARC, lock/journal and secondary setup boundaries modeled. Observer initializer is recorded but not executed here; no actual scheduler, UIKit reentry, changed real control pointer, backend success or device timing."
result = dict(passed=True,cases=len(rows),scope=scope,records=rows)
(RESULTS/"reentry-boundary-tests.json").write_text(json.dumps(result,separators=(",",":"))+"\n")
print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
