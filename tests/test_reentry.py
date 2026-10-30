from pathlib import Path
import json
D=Path(__file__).parent
import os
OUT=Path(os.environ.get("AU_RESULTS",str(D.parent/"results/generated")));OUT.mkdir(parents=True,exist_ok=True)
g={'__file__':str(D/'test_geometry.py')};exec(compile((D/'test_geometry.py').read_text().split('\nscenarios=[')[0],'geometry-model','exec'),g)
b={'__file__':str(D/'test_button_layout.py')};exec(compile((D/'test_button_layout.py').read_text().split('\nrows=[]\n')[0],'button-model','exec'),b)
Geometry,O,P,SELF,R=g['Geometry'],g['O'],g['P'],g['SELF'],g['R'];Button=b['Button']
rows=[]
def pause_at_setter(model,selector):
 native=model.msg;state={'paused':False}
 def msg(name,e):
  selected=model.sel(e.get(1));native(name,e)
  if selected==selector and not state['paused']:
   state['paused']=True;e.hit=e.get(30);e.u.emu_stop()
 model.msg=msg
 return state
def nested(model,entry):
 e=model.e;context=e.u.context_save();continuation=e.u.reg_read(R.UC_ARM64_REG_PC);outer_sp=e.u.reg_read(R.UC_ARM64_REG_SP)
 e.u.reg_write(R.UC_ARM64_REG_SP,outer_sp-0x2000);e.set(30,0x3001f000);e.set(0,SELF);e.run(entry)
 assert e.hit==0x3001f000
 e.u.context_restore(context)
 return continuation
for build,m in [('original',O),('r03',P)]:
 for setter in ['setContentScaleFactor:','setDrawableSize:']:
  model=Geometry(m,{});paused=pause_at_setter(model,setter);model.run(0x6855c0);assert paused['paused'] and model.busy
  before=list(model.calls);pc=nested(model,0x6855c0);assert model.calls==before and model.busy
  model.e.run(pc);assert not model.busy and model.e.hit==0x3001f000
  rows.append(dict(test='native-resize-setter-reentry',build=build,paused_setter=setter,nested_setter_calls=0,outer_clears_guard=True,events=model.calls))
model=Button(center=(80.,112.));paused=pause_at_setter(model,'setCenter:');model.run(0x1016820);assert paused['paused'];before=len(model.ev)
pc=nested(model,0x1016820);inner=model.ev[before:];assert sum(e[0]=='setCenter:' for e in inner)==1 and sum(e[0]=='bringSubviewToFront:' for e in inner)==1 and not any(e[0]=='create-button' for e in inner)
model.e.run(pc);assert sum(e[0]=='setCenter:' for e in model.ev)==2 and sum(e[0]=='bringSubviewToFront:' for e in model.ev)==2
rows.append(dict(test='native-button-layout-bounded-reentry',nested_set_center_calls=1,nested_front_calls=1,nested_creations=0,events=model.ev))
report=dict(passed=True,cases=len(rows),scope='Staged, single-thread native instruction composition: pause after a modeled setter, save CPU context, execute one nested invocation with shared emulated memory and separate stack, restore context and resume. No real UIKit-generated reentry, unbounded recursion, exceptions, threads or race proof.',records=rows)
(OUT/'reentry-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
