from emulator import *
env={'__file__':str(Path(__file__).parent/'test_render.py')};exec(compile((Path(__file__).parent/'test_render.py').read_text().split('\nrows=[]\n')[0],'render_model','exec'),env)
Model=env['Model'];D=Path(__file__).parent;rows=[]
VIEW,CMD,DESC,DRAWABLE,ENC,FLOAT=[env[n] for n in ['VIEW','CMD','DESC','DRAWABLE','ENC','FLOAT']]
ERR=0x20013000
cases=[('encoderStageLandingPad',0x6866c4,[(0x100,ENC),(0xd0,DRAWABLE),(0xc8,DESC),(0xc0,CMD),(0x28,VIEW)],False),('descriptorGetterLandingPad',0x68621c,[(0xc0,CMD),(0x28,VIEW)],False),('drawableGetterLandingPad',0x68622c,[(0xc8,DESC),(0xc0,CMD),(0x28,VIEW)],False),('floatGetterLandingPad',0x686358,[(0xd0,DRAWABLE),(0xc8,DESC),(0xc0,CMD),(0x28,VIEW)],False),('floatDrawLandingPad',0x686368,[(0xd0,DRAWABLE),(0xc8,DESC),(0xc0,CMD),(0x28,VIEW)],True)]
for build,m in [('original',O),('r03',P)]:
 for label,entry,locals_,temp in cases:
  model=Model(m);e=model.e;fp=SP+0x240;e.set(29,fp)
  for delta,ptr in locals_:e.write(fp-delta,struct.pack('<Q',ptr));model.refs[ptr]=1
  if temp:e.write(SP+0x68,struct.pack('<Q',FLOAT));model.refs[FLOAT]=1
  e.run(entry,[(0,ERR),(1,1)],stops=[0x875448])
  assert e.hit==0x875448 and e.get(0)==ERR
  assert all(e.q(fp-delta)==0 for delta,ptr in locals_)
  assert all(n==0 for n in model.refs.values())
  rows.append(dict(test=label,build=build,entry=hex(entry),cleared_locals=[hex(delta) for delta,ptr in locals_],temporary_released=temp,unwind_argument_preserved=True,ownership_delta_zero=True,events=model.events))
result=dict(passed=True,cases=len(rows),scope='Direct entry into five native exception landing-pad tails per build, with manually seeded frame locals and ownership counts. Stops at _Unwind_Resume; does not throw, select landing pads using unwind metadata, execute real unwinding, or establish Objective-C exception safety.',records=rows)
(RESULTS/'cleanup-tail-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
