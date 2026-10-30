from pathlib import Path
import ast,json,struct,math,itertools
D=Path(__file__).parent
import os
OUT=Path(os.environ.get("AU_RESULTS",str(D.parent/"results/generated")));OUT.mkdir(parents=True,exist_ok=True)
env={'__file__':str(D/'test_geometry.py')};exec(compile((D/'test_geometry.py').read_text().split('\nscenarios=[')[0],'geometry-model','exec'),env)
Geometry,P,SELF=env['Geometry'],env['P'],env['SELF'];eq=env['eq'];S=0x1013780;A=SELF;B=0x20002000;BUTTON=0x20008000
# Declarative selector/class schema only; no historical builder dependency.
lists=json.loads((D/'ui-cache-schema.json').read_text())
class Button(Geometry):
 def __init__(self,bounds=(0.,0.,430.,932.),center=(800.,1000.),main=True,cached=True,owner=A,pan_ok=True,button_ok=True):
  super().__init__(P,{});self.main=main;self.bounds=bounds;self.pan_ok=pan_ok;self.button_ok=button_ok;self.ev=[];self.number=0;self.obj={BUTTON:dict(center=center,view=owner)};self.pan=0x20007000
  pool=P.bytes(0x1230f0,0x398)
  for i,s in enumerate(lists['selectors']):
   offset=pool.find(s.encode()+b'\0');assert offset>=0,s;self.e.write(S+0x100+8*i,struct.pack('<Q',0x1230f0+offset))
  for i,c in enumerate(lists['classes']):self.e.write(S+0x80+8*i,struct.pack('<Q',0x20018000+i*0x100))
  self.e.write(S,struct.pack('<QQ',BUTTON if cached else 0,owner));self.e.write(S+32,struct.pack('<I',1))
 def msg(self,name,e):
  p=e.get(0);s=self.sel(e.get(1));arg=e.get(2)
  if s=='isMainThread':e.set(0,int(self.main))
  elif s=='buttonWithType:':
   self.ev.append(('create-button',self.button_ok));self.number+=1;v=0x20009000+self.number*0x100 if self.button_ok else 0
   if v:self.obj[v]=dict(center=(0.,0.),view=0)
   e.set(0,v)
  elif s=='removeFromSuperview':self.ev.append((s,p));self.obj[p]['view']=0
  elif s=='setFrame:':
   rect=self.ds(4);self.obj[p]['center']=(rect[0]+rect[2]/2,rect[1]+rect[3]/2);self.ev.append((s,rect))
  elif s=='stringWithUTF8String:':e.set(0,0x2001a000)
  elif s in ['whiteColor','colorWithRed:green:blue:alpha:','boldSystemFontOfSize:']:e.set(0,0x2001a100)
  elif s in ['layer','titleLabel']:e.set(0,0x2001a200)
  elif s=='alloc':e.set(0,self.pan if self.pan_ok else 0);self.ev.append(('alloc-pan',self.pan_ok))
  elif s=='initWithTarget:action:':e.set(0,p if self.pan_ok else 0)
  elif s=='addSubview:':self.obj[arg]['view']=p;self.ev.append((s,p,arg))
  elif s=='center':self.outd(self.obj[p]['center']);self.ev.append((s,p))
  elif s=='bounds':self.outd(self.bounds);self.ev.append((s,p))
  elif s=='setCenter:':self.obj[p]['center']=self.ds();self.ev.append((s,self.ds()))
  elif s=='bringSubviewToFront:':self.ev.append((s,p,arg))
  elif s in ['setTitle:forState:','setTitleColor:forState:','setBackgroundColor:','setCornerRadius:','setFont:','addTarget:action:forControlEvents:','setMaximumNumberOfTouches:','setCancelsTouchesInView:','addGestureRecognizer:']:self.ev.append((s,))
  else:raise AssertionError(('unmodeled layout selector',s,hex(p)))
 def call(self,owner=A):self.run(0x1016820,[(0,owner)]);assert self.e.get(0)==owner
 def cached(self):return self.e.q(S)
 def center(self):return self.obj[self.cached()]['center'] if self.cached() else None
rows=[]
# Cache/owner transition sequences: same owner reuses; different owner rebuilds.
for pan_ok in [False,True]:
 m=Button(cached=False,owner=0,pan_ok=pan_ok)
 for owner,want in zip([A,A,B,B,A],[1,0,1,0,1]):
  start=len(m.ev);m.call(owner);events=m.ev[start:];assert sum(x[0]=='create-button' for x in events)==want
  assert m.e.q(S+8)==owner and m.obj[m.cached()]['view']==owner
  rows.append(dict(test='owner-sequence',pan_allocation_succeeds=pan_ok,owner=hex(owner),events=events,center=m.center()))
# Main thread and receiver nil guards perform no UI work.
for owner,main in [(0,True),(A,False),(0,False)]:
 m=Button(main=main);m.call(owner);assert not m.ev;rows.append(dict(test='entry-guard',owner=hex(owner),main=main,events=m.ev))
# Missing button paired with matching owner skips recreation; detached existing child is not re-added.
m=Button(cached=False,owner=A);m.call();assert not m.ev and m.cached()==0;rows.append(dict(test='matching-owner-nil-cache',events=m.ev))
m=Button();m.obj[BUTTON]['view']=0;m.call();assert m.obj[BUTTON]['view']==0 and not any(x[0]=='addSubview:' for x in m.ev);rows.append(dict(test='same-owner-detached-child',events=m.ev))
# Allocation failure removes old child, clears button, leaves old owner field unchanged.
m=Button(button_ok=False);m.call(B);assert m.cached()==0 and m.e.q(S+8)==A and m.obj[BUTTON]['view']==0
rows.append(dict(test='replacement-allocation-failure',events=m.ev,owner_retained=hex(m.e.q(S+8))))
m.ev=[];m.button_ok=True;m.call(A);assert m.cached()==0 and not m.ev;rows.append(dict(test='old-owner-after-failure',events=m.ev))
m.call(B);assert m.cached()!=0 and m.e.q(S+8)==B;rows.append(dict(test='new-owner-retry-after-failure',events=m.ev))
# Cold allocation failure retries because cache owner is still different.
m=Button(cached=False,owner=0,button_ok=False)
for step,success in [('failed',False),('retry',True)]:
 m.ev=[];m.button_ok=success;m.call();assert bool(m.cached())==success;rows.append(dict(test='cold-allocation-'+step,events=m.ev))
# Fully native clamp execution at cached-owner path.
scenarios=[('ordinary',(0.,0.,430.,932.),(800.,1000.),(398.,900.),True),('nonzero-origin',(10.,20.,430.,932.),(-100.,2000.),(42.,920.),True),('exact-size',(10.,20.,64.,64.),(100.,100.),(42.,52.),True),('small-width',(0.,0.,63.,932.),(800.,1000.),(800.,1000.),False),('small-height',(0.,0.,430.,63.),(800.,1000.),(800.,1000.),False),('zero-size',(0.,0.,0.,0.),(80.,112.),(80.,112.),False),('negative-size',(0.,0.,-1.,932.),(80.,112.),(80.,112.),False),('nan-width',(0.,0.,float('nan'),932.),(80.,112.),(80.,112.),False),('nan-height',(0.,0.,430.,float('nan')),(80.,112.),(80.,112.),False),('nan-center',(0.,0.,430.,932.),(float('nan'),112.),(float('nan'),112.),True),('infinite-center',(0.,0.,430.,932.),(float('inf'),-float('inf')),(398.,32.),True),('infinite-origin',(float('inf'),0.,430.,932.),(80.,112.),(float('inf'),112.),True)]
for name,bounds,center,want,sets in scenarios:
 m=Button(bounds=bounds,center=center);m.call();assert eq(m.center(),want),(name,m.center(),want);assert any(x[0]=='setCenter:' for x in m.ev)==sets
 assert sum(x[0]=='bringSubviewToFront:' for x in m.ev)==1
 rows.append(dict(test='clamp-'+name,bounds=bounds,initial_center=center,after=m.center(),events=m.ev))
# Repeated valid layout still sends setters/front messages, even when unchanged.
m=Button(center=(80.,112.))
for i in range(3):
 m.ev=[];m.call();assert sum(x[0]=='setCenter:' for x in m.ev)==1 and sum(x[0]=='bringSubviewToFront:' for x in m.ev)==1;assert not any(x[0]=='create-button' for x in m.ev)
 rows.append(dict(test='unchanged-repeat',invocation=i,events=m.ev))
report=dict(passed=True,cases=len(rows),scope='Native R03 install/layout/clamp instructions at unslid addresses with modeled initialized selector/class caches and Objective-C/UI operations. Allocation failures and caller sequences are synthetic. No real target/action, touch routing, UIKit reentry/exception or device timing execution. No binary edits.',records=rows)
(OUT/'button-layout-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
