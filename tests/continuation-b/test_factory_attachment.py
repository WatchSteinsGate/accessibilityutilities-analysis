from emulator import *
env={'__file__':str(Path(__file__).parent/'test_factory.py')};exec(compile((Path(__file__).parent/'test_factory.py').read_text().split('\nrows=[]\n')[0],'factory_model','exec'),env)
Factory=env['Factory'];CTRL=env['CTRL'];OVERLAY=env['OVERLAY'];BLOCK=0x20001000;STATE=0xff2798
D=Path(__file__).parent;rows=[]
for build,m in [('original',O),('r03',P)]:
 for initial_allocation_failure in [False,True]:
  model=Factory(m);model.alloc_fail=initial_allocation_failure
  for iteration in range(3):
   e=model.e;start=len(model.events);ctrl=CTRL+iteration*0x100;e.write(0x1011b68,struct.pack('<Q',ctrl));e.write(STATE+0x50,bytes([1,0,0,0,1]));e.write(BLOCK+32,struct.pack('<Q',e.q(STATE+0x40)))
   # Native callback prepares all arguments for the native factory.
   e.run(0x76944,[(0,BLOCK)],stops=[0x76be8]);assert e.hit==0x76be8
   callback=e.u.context_save();args=[e.get(i) for i in range(2,6)];rect=model.dget(e)
   fr=model.invoke(*args,rect);result=e.get(0)
   # Cancel only after the factory returns, before callback attachment resumes.
   e.run(0x7b0b8,[(0,STATE)],stack_pointer=0x30008000)
   e.u.context_restore(callback);e.set(0,result);e.set(30,0x76bec);model.continue_native(0x76bec)
   assert e.hit==STOP and e.q(STATE+0x40)!=e.q(BLOCK+32)
   events=model.events[start:];adds=[x for x in events if x.get('selector')=='addSubview:']
   if initial_allocation_failure:
    assert result==0 and len(adds)==1 and adds[0]['nil_child'];model.alloc_fail=False
   else:
    assert result==OVERLAY and model.parent==model.target and len(adds)==int(iteration==0)
   assert model.allocations==1
   rows.append(dict(test='nativeFactoryToAttachmentAfterCancellation',build=build,iteration=iteration,initial_allocation_failed=initial_allocation_failure,returned=hex(result),final_parent=hex(model.parent),allocation_attempts=model.allocations,published_control_pointer=hex(e.q(0x1011e20)),requested_control_pointer=hex(ctrl),attempted_nil_child_add=any(x.get('nil_child') for x in adds),current_attempt=e.q(STATE+0x40),captured_attempt=e.q(BLOCK+32),events=events))
result=dict(passed=True,cases=len(rows),scope='Native admitted constructor composed with native shared factory/once block/publication prefix, then native suspend on a separate stack before callback resumes. Each invocation starts from seeded eligible state. dispatch_once, ObjC/runtime, rest of init, property ownership and hierarchy effects remain modeled; attempted addSubview:nil is recorded without throwing. No asynchronous/runtime proof.',records=rows)
(RESULTS/'factory-attachment-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
