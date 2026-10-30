from emulator import *
import itertools
D=Path(__file__).parent;STATE=0xff2798;BLOCK=0x20001000
rows=[]
for build,m in [('original',O),('r03',P)]:
 e=E(m);e.journal();e.ownership()
 # Lock construction/destruction are synchronization boundaries, not simulated mutexes.
 e.noop([0x262e4,0x2675c])
 # The blocking-flag accessor remains native.
 for start in [7,(1<<64)-1]:
  for sequence in ['none','suspend','suspend_resume','suspend_resume_reactivated','flagA','flagB','busy']:
   e.write(STATE+0x40,struct.pack('<QQ',start,31));e.write(STATE+0x50,bytes([1,0,0,0,1]));e.write(0x10109c1,b'\0')
   e.write(BLOCK+32,struct.pack('<Q',start))
   if sequence.startswith('suspend'):
    e.run(0x7b0b8,[(0,STATE)])
    assert e.byte(STATE+0x54)==0 and e.byte(STATE+0x50)==0
   if 'resume' in sequence:
    e.run(0x7b9a4,[(0,STATE)])
    assert e.byte(STATE+0x54)==1 and e.byte(STATE+0x50)==0
   if sequence.endswith('reactivated'):e.write(STATE+0x50,b'\1')
   if sequence in ['flagA','flagB','busy']:e.write(STATE+{'flagA':0x51,'flagB':0x52,'busy':0x53}[sequence],b'\1')
   e.run(0x76944,[(0,BLOCK)],stops=[0x769b4,0x76dc8])
   admitted=e.hit==0x769b4
   assert admitted==(build=='r03' or sequence=='none')
   expected=(start+int(sequence.startswith('suspend'))+int('resume' in sequence))&((1<<64)-1)
   assert e.q(STATE+0x40)==expected
   rows.append(dict(test='queuedConstructorAfterStateChange',build=build,initial_attempt=start,sequence=sequence,captured_attempt=start,current_attempt=e.q(STATE+0x40),current_event=e.q(STATE+0x48),state_bytes=list(e.u.mem_read(STATE+0x50,5)),reached_ui_boundary=admitted))
 # Fresh callback truth table: local seeded state, not genuine backend success.
 for bits in itertools.product([0,1],repeat=5):
  e.write(STATE+0x40,struct.pack('<QQ',19,23));e.write(STATE+0x50,bytes(bits));e.write(0x10109c1,b'\0');e.write(BLOCK+32,struct.pack('<Q',19))
  e.run(0x76944,[(0,BLOCK)],stops=[0x769b4,0x76dc8]);admitted=e.hit==0x769b4
  assert admitted==(build=='r03' or bits==(1,0,0,0,1))
  rows.append(dict(test='freshConstructorStateComposition',build=build,state_bytes=bits,reached_ui_boundary=admitted))
 # Blocking flag tested separately from shared-state flags.
 e.write(STATE+0x50,bytes([1,0,0,0,1]));e.write(0x10109c1,b'\1')
 e.run(0x76944,[(0,BLOCK)],stops=[0x769b4,0x76dc8]);assert (e.hit==0x769b4)==(build=='r03')
 rows.append(dict(test='freshConstructorBlocked',build=build,reached_ui_boundary=e.hit==0x769b4))
result=dict(passed=True,cases=len(rows),scope='Sequential native suspend/resume mutators plus constructor eligibility prefix; stopped before UI construction. Mutex boundaries and journal sink modeled. Reactivation and initial state seeded, not authenticated or end-to-end. No concurrency, real queued block ownership, UI effect, or timing proof.',records=rows)
(RESULTS/'cancellation-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
