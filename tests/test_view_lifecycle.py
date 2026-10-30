from pathlib import Path
import json,struct,itertools,sys
D=Path(__file__).parent
import os
OUT=Path(os.environ.get("AU_RESULTS",str(D.parent/"results/generated")));OUT.mkdir(parents=True,exist_ok=True)
import native_env
g=vars(native_env)
E,O,P,imp=g['E'],g['orig'],g['cur'],g['imp']
SELF=0x20001000;W1=0x20002000;W2=0x20003000;ARRAY=0x20004000;GEST=0x20005000;OTHER=0x20006000
class Model:
 def __init__(self,m):
  self.e=E(m);self.window=W1;self.array=None;self.objects={};self.events=[];self.next=0x20007000;self.state=0
  for a,name in imp.items():self.e.calls[a]=lambda e,name=name:self.imported(name,e)
  self.e.calls[0x6e0990]=lambda e:self.events.append(('journal-boundary',))
 def alloc(self):p=self.next;self.next+=0x100;self.objects[p]={};return p
 def sel(self,p):return bytes(self.e.u.mem_read(p,200)).split(b'\0')[0].decode()
 def imported(self,name,e):
  if name in ['_objc_msgSend','_objc_msgSendSuper2']:return self.msg(name,e)
  if name in ['_objc_retain','_objc_retainAutoreleasedReturnValue','_objc_autoreleaseReturnValue','_objc_retainBlock']:return
  if name=='_objc_release':return
  if name=='_objc_storeStrong':e.write(e.get(0),struct.pack('<Q',e.get(1)));return
  if name=='_objc_alloc':e.set(0,self.alloc());self.events.append(('alloc',));return
  if name=='_memset':e.write(e.get(0),bytes([e.get(1)&255])*e.get(2));return
  raise AssertionError(('unmodeled import',name))
 def msg(self,name,e):
  p=e.get(0);s=self.sel(e.get(1));arg=e.get(2)
  if name=='_objc_msgSendSuper2':self.events.append(('super',s));return
  if s=='window':e.set(0,self.window)
  elif s=='menuTapRecognizers':e.set(0,ARRAY if self.array is not None else 0)
  elif s=='arrayWithCapacity:':self.array=[];e.set(0,ARRAY);self.events.append(('new-array',arg))
  elif s=='initWithTarget:action:':self.objects[p].update(target=arg,action=self.sel(e.get(3)));self.events.append(('init-gesture',arg,self.sel(e.get(3))))
  elif s.startswith('setNumberOf') or s in ['setCancelsTouchesInView:','setDelaysTouchesBegan:','setDelaysTouchesEnded:','setDelegate:']:
   self.objects[p][s]=arg;self.events.append((s,arg))
  elif s=='addObject:':self.array.append(arg)
  elif s=='copy':e.set(0,p)
  elif s=='setMenuTapRecognizers:':assert arg==ARRAY
  elif s=='countByEnumeratingWithState:objects:count:':
   if not p:e.set(0,0);return
   state=arg;done=e.q(state)
   if done or not self.array:e.set(0,0);return
   buf=e.get(3);mut=0x2001e000;e.write(buf,b''.join(struct.pack('<Q',x) for x in self.array));e.write(state,struct.pack('<QQQ',1,buf,mut));e.set(0,len(self.array))
  elif s=='view':e.set(0,self.objects[p].get('view',0) if p else 0)
  elif s=='removeGestureRecognizer:':
   if p:self.objects[arg]['view']=0;self.events.append(('remove',p,arg))
  elif s=='addGestureRecognizer:':
   if p:self.objects[arg]['view']=p;self.events.append(('add',p,arg))
  elif s=='containsObject:':e.set(0,int(self.array is not None and arg in self.array))
  elif s=='state':e.set(0,self.state)
  else:raise AssertionError(('unmodeled selector',s,hex(p)))
 def run(self,a,args=()):
  e=self.e;e.set(30,0x3001f000);e.u.reg_write(g['R'].UC_ARM64_REG_SP,0x30010000);e.set(0,SELF)
  for n,v in args:e.set(n,v)
  e.run(a)
rows=[]
# Whole didMoveToWindow with native normal paths; ObjC collections/ownership and journal modeled.
for build,m in [('original',O),('r03',P)]:
 for existing,old in itertools.product([False,True],[0,W1,W2]):
  model=Model(m)
  if existing:model.array=[GEST];model.objects[GEST]={'view':old}
  for window in [W1,W1,W2,0,W2]:
   model.window=window;before=list(model.array or []);before_views={p:model.objects[p].get('view',0) for p in before};start=len(model.events)
   model.run(0x6867c8);events=model.events[start:]
   assert model.array is not None and len(model.array)==1
   assert all(model.objects[p].get('view',0)==window for p in model.array)
   allocated=sum(ev[0]=='alloc' for ev in events)
   assert allocated==int(not before and bool(window))
   assert sum(ev[0]=='add' for ev in events)==sum(before_views.get(p,0)!=window and bool(window) for p in model.array)
   assert sum(ev[0]=='remove' for ev in events)==sum(bool(before_views.get(p,0)) and before_views[p]!=window for p in before)
   if allocated:
    obj=model.objects[model.array[0]]
    assert obj['setNumberOfTouchesRequired:']==5 and obj['setNumberOfTapsRequired:']==5
    assert all(obj[s]==0 for s in ['setCancelsTouchesInView:','setDelaysTouchesBegan:','setDelaysTouchesEnded:'])
   rows.append(dict(test='didMoveToWindow',build=build,existing=existing,initial_old_view=hex(old),window=hex(window),allocations=allocated,events=events))
 # Delegate membership truth table.
 for a,b in itertools.product([False,True],repeat=2):
  model=Model(m);model.array=([GEST] if a else [])+([OTHER] if b else []);model.run(0x686dac,[(2,GEST),(3,OTHER)]);got=model.e.get(0)&1;assert got==int(a and not b)
  rows.append(dict(test='simultaneousDelegate',build=build,first_member=a,second_member=b,result=got))
 # Gesture state callback writes an idempotent request byte, not a direct visibility toggle.
 for state,present,initial in itertools.product(range(6),[False,True],[0,1]):
  model=Model(m);model.state=state;model.e.write(0x1011e20,struct.pack('<Q',OTHER if present else 0));model.e.write(OTHER,bytes([initial]));model.run(0x686f8c,[(2,GEST)]);after=bytes(model.e.u.mem_read(OTHER,1))[0];assert after==(1 if present and state==3 else initial)
  rows.append(dict(test='menuShortcutTapped',build=build,state=state,request_pointer_present=present,initial=initial,after=after))
# layoutSubviews executes original sync selector, then R03 adds a second receiver-only helper call.
for build,m in [('original',O),('r03',P)]:
 model=Model(m);events=[]
 model.e.calls[0x876624]=lambda e:events.append(('message',e.get(0),model.sel(e.get(1))))
 model.e.calls[0x1016820]=lambda e:events.append(('native-button-layout-helper',e.get(0)))
 model.run(0x6870dc)
 assert events==[('message',SELF,'syncOverlaySize')]+([('native-button-layout-helper',SELF)] if build=='r03' else [])
 rows.append(dict(test='layoutSubviewsBoundary',build=build,events=events))
result=dict(passed=True,cases=len(rows),counts={t:sum(x['test']==t for x in rows) for t in sorted(set(x['test'] for x in rows))},scope='Native ARM64 original/R03 methods at unslid addresses; modeled ObjC, collection enumeration, ownership, memset and R03 journal sink. Normal paths only; no UIKit, ARC, gestures, races, dispatch timing or device proof. Layout helper stopped at call boundary, not tested internally.',records=rows)
(OUT/'view-lifecycle-tests.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
