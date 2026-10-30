from pathlib import Path
import sys,json,struct,math,itertools,ctypes
D=Path(__file__).parent
import os
OUT=Path(os.environ.get("AU_RESULTS",str(D.parent/"results/generated")));OUT.mkdir(parents=True,exist_ok=True)
env={'__file__':str(D/'test_view_lifecycle.py')};exec(compile(Path(env['__file__']).read_text().split('\nrows=[]\n')[0],'view-model','exec'),env)
Model,O,P,SELF=env['Model'],env['O'],env['P'],env['SELF'];R=env['g']['R'];CTX=0x20012000;SCREEN=0x20013000
class Geometry(Model):
 def __init__(self,m,spec,context=True):
  super().__init__(m);self.spec=spec;self.busy=False;self.scale=spec.get('existing_scale',1.);self.size=spec.get('existing_size',(1.,1.));self.calls=[];self.reentry_guard=[]
  self.e.write(0x1011bf0,struct.pack('<Q',CTX if context else 0));self.e.write(CTX+16,struct.pack('<ff',123.,456.));self.e.write(CTX+104,struct.pack('<ff',7.,8.))
 def ds(self,n=2):return tuple(struct.unpack('<d',struct.pack('<Q',self.e.u.reg_read(getattr(R,'UC_ARM64_REG_D'+str(i)))))[0] for i in range(n))
 def outd(self,values):
  for i,v in enumerate(values):self.e.u.reg_write(getattr(R,'UC_ARM64_REG_D'+str(i)),struct.unpack('<Q',struct.pack('<d',v))[0])
 def msg(self,name,e):
  p=e.get(0);s=self.sel(e.get(1))
  if s=='isMainThread':e.set(0,1)
  elif s=='overlaySizeSyncing':e.set(0,int(self.busy))
  elif s=='mainScreen':e.set(0,SCREEN if self.spec.get('screen',True) else 0)
  elif s=='nativeScale':self.outd([self.spec.get('native_scale',2.)])
  elif s=='bounds':self.outd((0.,0.,*self.spec.get('screen_bounds',(320.,640.))) if p==SCREEN else self.spec.get('bounds',(0.,0.,640.,320.)))
  elif s=='frame':self.outd(self.spec.get('frame',(0.,0.,600.,300.)))
  elif s=='contentScaleFactor':self.outd([self.scale])
  elif s=='drawableSize':self.outd(self.size)
  elif s=='setOverlaySizeSyncing:':self.busy=bool(e.get(2));self.calls.append((s,self.busy))
  elif s=='setContentScaleFactor:':self.reentry_guard.append(self.busy);self.scale=self.ds(1)[0];self.calls.append((s,self.scale))
  elif s=='setDrawableSize:':self.reentry_guard.append(self.busy);self.size=self.ds();self.calls.append((s,self.size))
  else:return super().msg(name,e)
def eq(a,b):
 if isinstance(a,(tuple,list)):return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
 return a==b or isinstance(a,float) and isinstance(b,float) and math.isnan(a) and math.isnan(b)
def expected(spec,context):
 scale=spec.get('native_scale',2.) if spec.get('screen',True) else 1.
 if not math.isfinite(scale) or scale<=0:scale=1.
 w,h=spec.get('bounds',(0.,0.,640.,320.))[2:]
 if w<=0 or h<=0:w,h=spec.get('frame',(0.,0.,600.,300.))[2:]
 if w<=0 or h<=0:w,h=spec.get('screen_bounds',(320.,640.)) if spec.get('screen',True) else (0.,0.)
 w,h=w*scale,h*scale
 if h>w:w,h=h,w
 changes=[]
 if not abs(spec.get('existing_scale',1.)-scale)<0.01:changes.append(('setContentScaleFactor:',scale))
 old=spec.get('existing_size',(1.,1.))
 if not all(abs(x-y)<0.5 for x,y in zip(old,(w,h))):changes.append(('setDrawableSize:',(w,h)))
 calls=[('setOverlaySizeSyncing:',True)]+changes+[('setOverlaySizeSyncing:',False)] if changes else []
 publish=context and all(math.isfinite(x) and x>0 for x in (w,h))
 io=tuple(ctypes.c_float(x).value for x in (w,h)) if publish else (123.,456.)
 fb=(1.,1.) if publish else (7.,8.)
 return calls,io,fb
scenarios=[
 ('landscape',{}),('portrait',{'bounds':(0.,0.,320.,640.)}),('offset-origin',{'bounds':(11.,23.,640.,320.)}),
 ('zero-bounds-frame-fallback',{'bounds':(0.,0.,0.,0.)}),('negative-bounds-frame-fallback',{'bounds':(0.,0.,-1.,40.)}),
 ('screen-fallback',{'bounds':(0.,0.,0.,0.),'frame':(0.,0.,0.,0.)}),
 ('all-zero',{'bounds':(0.,0.,0.,0.),'frame':(0.,0.,0.,0.),'screen_bounds':(0.,0.)}),
 ('negative-screen-fallback',{'bounds':(0.,0.,0.,0.),'frame':(0.,0.,0.,0.),'screen_bounds':(-2.,-4.)}),
 ('nil-screen',{'screen':False}),('nil-screen-invalid-geometry',{'screen':False,'bounds':(0.,0.,0.,0.),'frame':(0.,0.,0.,0.)}),
 ('zero-scale',{'native_scale':0.}),('negative-scale',{'native_scale':-3.}),('nan-scale',{'native_scale':float('nan')}),('infinite-scale',{'native_scale':float('inf')}),
 ('nan-width',{'bounds':(0.,0.,float('nan'),320.)}),('nan-height',{'bounds':(0.,0.,640.,float('nan'))}),
 ('infinite-width',{'bounds':(0.,0.,float('inf'),320.)}),('finite-double-float-overflow',{'bounds':(0.,0.,1e100,320.)}),
 ('double-product-overflow',{'bounds':(0.,0.,1e308,320.)}),
 ('unchanged',{'existing_scale':2.,'existing_size':(1280.,640.)}),
 ('scale-below-tolerance',{'existing_scale':2.009,'existing_size':(1280.,640.)}),('scale-over-tolerance',{'existing_scale':2.011,'existing_size':(1280.,640.)}),
 ('size-below-tolerance',{'existing_scale':2.,'existing_size':(1280.499,640.499)}),('size-at-tolerance',{'existing_scale':2.,'existing_size':(1280.5,640.)}),
 ('size-over-tolerance',{'existing_scale':2.,'existing_size':(1280.501,640.)}),('small-fractional-size',{'bounds':(0.,0.,.1,.05),'native_scale':1.})]
rows=[]
for build,m in [('original',O),('r03',P)]:
 for (name,spec),context in itertools.product(scenarios,[False,True]):
  model=Geometry(m,spec,context);model.run(0x6855c0);calls,io,fb=expected(spec,context)
  actual=struct.unpack('<ff',model.e.u.mem_read(CTX+16,8));actualfb=struct.unpack('<ff',model.e.u.mem_read(CTX+104,8))
  assert eq(model.calls,calls),(build,name,model.calls,calls)
  assert eq(actual,io) and eq(actualfb,fb),(build,name,actual,io,actualfb,fb)
  assert not model.busy and all(model.reentry_guard)
  rows.append(dict(build=build,scenario=name,context=context,setter_calls=model.calls,published_display_size=actual,published_framebuffer_scale=actualfb,busy_at_setters=model.reentry_guard))
 # Stateful zero geometry -> valid -> repeated valid; normal-path return and publication recovery.
 model=Geometry(m,{'bounds':(0.,0.,0.,0.),'frame':(0.,0.,0.,0.),'screen_bounds':(0.,0.)})
 for step,bounds in [('zero',(0.,0.,0.,0.)),('valid',(0.,0.,640.,320.)),('repeat-valid',(0.,0.,640.,320.))]:
  model.spec['bounds']=bounds;model.calls=[];model.run(0x6855c0)
  got=struct.unpack('<ff',model.e.u.mem_read(CTX+16,8));assert eq(got,(123.,456.) if step=='zero' else (1280.,640.))
  if step=='repeat-valid':assert not model.calls
  rows.append(dict(build=build,scenario='recovery-'+step,context=True,setter_calls=model.calls,published_display_size=got))
# Pair records exactly, including numeric edge-case outcomes.
original=[{k:v for k,v in x.items() if k!='build'} for x in rows if x['build']=='original'];patched=[{k:v for k,v in x.items() if k!='build'} for x in rows if x['build']=='r03'];assert repr(original)==repr(patched)
report=dict(passed=True,cases=len(rows),scenarios_per_build=len(original),paired_records_equal=True,scope='Full native syncOverlaySize normal-path geometry, numeric helpers and size publication, with modeled ObjC getters/setters and ownership. Real UIKit setter behavior, reentry and exceptions not executed; unslid only; no binary edits.',records=rows)
(OUT/'geometry-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
