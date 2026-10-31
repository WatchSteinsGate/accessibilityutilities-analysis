"""Actual native state setup composed with nonempty render/reset callbacks."""
from pathlib import Path
import os,sys,json,struct,math,hashlib,itertools
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-m-state'))
sys.path.insert(0,str(HERE));from test_render_commands import *
class State(Render):
 def __init__(self,image,commands,origin=(0.,0.),scale=(1.,1.),pipeline=True,depth=True):
  super().__init__(image,commands,origin,scale);self.viewports=[];self.matrices=[];self.states=[];self.vertex_bindings=[];self.native_setup_requests=[];self.pipeline=pipeline;self.depth_live=depth
  putq(self.e,0x1010c48,CONTEXT)
 def memcpy(self,e):
  if e.get(2)==48:e.write(e.get(0),bytes(e.u.mem_read(e.get(1),48)));return
  return super().memcpy(e)
 def msg(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if r==CONTEXT and s.startswith('setupRenderState:'):
   self.native_setup_requests.append(e.get(7));return Work(0x12de90,(),False,None)
  if r==CONTEXT and s=='depthStencilState':e.set(0,DEPTH if self.depth_live else 0);return
  if r==ENC:
   if s=='setCullMode:':assert a==0;self.states.append(dict(selector=s,value=a));return
   if s=='setDepthStencilState:':assert a==(DEPTH if self.depth_live else 0);self.states.append(dict(selector=s,value=a));return
   if s=='setViewport:':self.viewports.append(list(struct.unpack('<6d',e.u.mem_read(a,48))));return
   if s=='setVertexBytes:length:atIndex:':
    assert e.get(3)==64 and e.get(4)==1;self.matrices.append(list(struct.unpack('<16f',e.u.mem_read(a,64))));return
   if s=='setRenderPipelineState:':assert a==(PIPE if self.pipeline else 0);self.states.append(dict(selector=s,value=a));return
   if s=='setVertexBuffer:offset:atIndex:':
    assert a==B1 and e.get(3)==0 and e.get(4)==0;self.vertex_bindings.append(dict(buffer=hex(a),offset=e.get(3),index=e.get(4)));return
  return super().msg(e)
def near(a,b):return len(a)==len(b) and all(math.isclose(x,y,rel_tol=1e-6,abs_tol=1e-6) for x,y in zip(a,b))
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for origin,scale in [((0.,0.),(1.,1.)),((5.,10.),(2.,3.)),((-20.,-30.),(.5,.25))]:
   for pipeline,depth in itertools.product([False,True],repeat=2):
    m=State(image,[dict(callback=(1<<64)-1),dict()],origin,scale,pipeline,depth);m.render()
    assert len(m.native_setup_requests)==2 and m.native_setup_requests==[0,0]
    assert len(m.draws)==1 and len(m.viewports)==2 and len(m.vertex_bindings)==2 and len(m.requests)==1
    expected_viewport=[0.,0.,320.*scale[0],240.*scale[1],0.,1.]
    expected_matrix=[2/320,0,0,0,0,-2/240,0,0,0,0,1,0,-1-2*origin[0]/320,1+2*origin[1]/240,0,1]
    assert all(near(v,expected_viewport) for v in m.viewports)
    assert all(near(v,expected_matrix) for v in m.matrices)
    rows.append(dict(test='nativeRenderStateComposition',build=build,origin=origin,scale=scale,pipeline_provider_nonnull=pipeline,depth_provider_nonnull=depth,native_setup_offsets=m.native_setup_requests,viewports=m.viewports,projection_matrices=m.matrices,state_calls=m.states,vertex_bindings=m.vertex_bindings,indexed_draw_calls=m.draws,completion_registration=len(m.requests),actual_gpu_validation=False))
 assert len(rows)==24
 lo,hi=0x12de90,O.bounds(0x12de90)[1];a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
 data=dict(passed=True,cases=len(rows),scope='24 paired native/model records. Native setupRenderState body replaces prior setup provider and composes with actual render body, reset sentinel, nonempty command and completion registration. Native viewport, orthographic matrix, cull/depth/pipeline/vertex bindings verified. Metal encoder, state objects, cached depth getter, buffer providers and Objective-C/ARC modeled. Nil depth/pipeline messages still forwarded; no valid real pipeline, shader/GPU submission/completion, device behavior or performance inference.',code_equality=dict(start=hex(lo),end_exclusive=hex(hi),sha256=hashlib.sha256(a).hexdigest(),equal=True),records=rows)
 (RESULTS/'render-state-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
