"""Native render registration -> manual block copy/invoke -> native cache body."""
from pathlib import Path
import os,sys,json,struct
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-backend'))
sys.path.insert(0,str(HERE));from test_cache_policy import *
sys.path.insert(0,str(HERE.parent/'continuation-e'));from test_factories import Model,Work,YieldingE,putq
DD=0x20060000;LISTS=0x20061000;DL=0x20062000;CMD=0x20063000;ENC=0x20064000;PIPE=0x20065000;COPYBLOCK=0x20066000;SOURCEV=0x20067000;SOURCEI=0x20068000;DESC_CLASS=0x20069000;DESC=0x2006a000;DEPTH=0x2006b000
W1=0x20070000;W2=0x20071000;B1=W1+0x100;B2=W2+0x100;MEM1=0x20072000;MEM2=0x20073000
class Backend(Cache,Model):
 emulator_class=YieldingE
 def __init__(self,image,geometry=1,weak_live=True,pipeline=True,command=True):
  Cache.__init__(self,image);self.depth=0;self.requests=[];self.setup=[];self.copies=[];self.recycles=[];self.weak_live=weak_live;self.pipeline=pipeline;self.command=command;self.allocations=0;self.depth_fault='ready';self.depth_state=None
  self.buffers.update({W1:(B1,20*geometry),W2:(B2,2*geometry)});self.times.update({W1:0.,W2:0.});self.dequeues=[W1,W2]
  self.e.write(DD,bytes(0x40));self.e.write(DD+4,struct.pack('<iiiQ',1,geometry,geometry,LISTS));self.e.write(DD+0x20,struct.pack('<4f',320.,240.,1.,1.));putq(self.e,LISTS,DL)
  self.e.write(DL,bytes(0x40));self.e.write(DL+0x10,struct.pack('<i',geometry));putq(self.e,DL+0x18,SOURCEI);self.e.write(DL+0x20,struct.pack('<i',geometry));putq(self.e,DL+0x28,SOURCEV)
  self.e.write(SOURCEV,bytes(range(20)));self.e.write(SOURCEI,b'\1\0')
  putq(self.e,0xff0a60,DESC_CLASS)
  for a,n in IMPORTS.items():
   if n=='_objc_retainAutorelease':self.e.calls[a]=lambda e:None
   elif n=='_objc_initWeak':self.e.calls[a]=self.initweak
   elif n=='_objc_copyWeak':self.e.calls[a]=self.copyweak
   elif n=='_objc_destroyWeak':self.e.calls[a]=lambda e:putq(e,e.get(0),0)
   elif n=='_objc_loadWeakRetained':self.e.calls[a]=self.loadweak
   elif n=='_memcpy':self.e.calls[a]=self.memcpy
 def initweak(self,e):putq(e,e.get(0),e.get(1))
 def copyweak(self,e):putq(e,e.get(0),e.q(e.get(1)))
 def loadweak(self,e):e.set(0,e.q(e.get(0)) if self.weak_live else 0)
 def memcpy(self,e):
  size=e.get(2);assert size in (0,2,20)
  if size:e.write(e.get(0),bytes(e.u.mem_read(e.get(1),size)))
  self.copies.append(size)
 def alloc(self,e):
  if e.get(0)==DESC_CLASS:e.set(0,0 if self.depth_fault=='descriptor_nil' else DESC)
  else:Cache.alloc(self,e)
 def msg(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if not r:e.set(0,0);return
  if r==CMD and s=='device':e.set(0,DEVICE);return
  if r==CONTEXT and s=='renderPipelineStateForFrameAndDevice:':e.set(0,PIPE if self.pipeline else 0);return
  if r==CONTEXT and s=='dequeueReusableBufferOfLength:device:':
   w=self.dequeues.pop(0);assert a==self.buffers[w][1] and e.get(3) in [0,DEVICE];e.set(0,w);return
  if r==CONTEXT and s.startswith('setupRenderState:'):
   self.setup.append(dict(selector=s,modeled=True));return
  if r in [B1,B2] and s=='contents':e.set(0,MEM1 if r==B1 else MEM2);return
  if r==CMD and s=='addCompletedHandler:':
   assert e.q(a+16)==0x12edb8 and e.q(a+0x20)==W1 and e.q(a+0x28)==W2
   self.e.write(COPYBLOCK,bytes(e.u.mem_read(a,0x38)))
   self.requests.append(dict(invoke=hex(e.q(a+16)),vertex=hex(e.q(a+0x20)),index=hex(e.q(a+0x28)),delivery='manual after caller return',copy_provider='native copy helper, modeled runtime allocation'))
   return Work(0x12eea8,[(0,COPYBLOCK),(1,a)],False,None)
  if r==CONTEXT and s=='enqueueReusableBuffer:':
   self.recycles.append(hex(a));return Work(0x12c06c,(),False,None)
  if r==DESC and s=='init':e.set(0,DESC);return
  if r==DESC and s in ['setDepthWriteEnabled:','setDepthCompareFunction:']:
   assert a==(0 if s=='setDepthWriteEnabled:' else 7);return
  if r==DEVICE and s=='newDepthStencilStateWithDescriptor:':
   e.set(0,0 if self.depth_fault=='state_nil' else DEPTH);return
  if r==CONTEXT and s=='setDepthStencilState:':self.depth_state=a;return
  return Cache.msg(self,e)

def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for geometry in [0,1]:
   for live,pipeline,command in [(True,True,True),(False,True,True),(True,False,True),(True,True,False)]:
    m=Backend(image,geometry,live,pipeline,command)
    m.nested(0x12e2d0,[(0,CONTEXT),(1,0),(2,DD),(3,CMD if command else 0),(4,ENC)])
    assert len(m.requests)==int(command) and len(m.setup)==1 and m.copies==[20*geometry,2*geometry]
    before=m.values()
    if command:
     assert m.e.q(COPYBLOCK+0x20)==W1 and m.e.q(COPYBLOCK+0x28)==W2
     m.nested(0x12edb8,[(0,COPYBLOCK),(1,CMD)])
     assert m.recycles==([hex(W1),hex(W2)] if live else [])
     assert m.values()==([20*geometry,2*geometry] if live else [])
     m.nested(0x12ef14,[(0,COPYBLOCK)])
     assert m.e.q(COPYBLOCK+0x20)==0 and m.e.q(COPYBLOCK+0x28)==0
    if geometry:assert bytes(m.e.u.mem_read(MEM1,20))==bytes(range(20)) and bytes(m.e.u.mem_read(MEM2,2))==b'\1\0'
    rows.append(dict(test='nativeRenderRegistrationToCache',build=build,geometry_elements=geometry,weak_live=live,pipeline_nonnull=pipeline,command_nonnull=command,requests=m.requests,copy_sizes=m.copies,cache_before=before,cache_after=m.values(),recycled=m.recycles,native_copy_invoke_dispose_executed=command,setup_render_state_modeled=True,actual_gpu_completion=False))
  for guard in ['width_zero','no_lists']:
   m=Backend(image)
   m.e.write(DD+(0x20 if guard=='width_zero' else 4),bytes(4));m.nested(0x12e2d0,[(0,CONTEXT),(1,0),(2,DD),(3,CMD),(4,ENC)])
   assert not m.requests and not m.setup and not m.copies
   rows.append(dict(test='nativeRenderDataEntryGuard',build=build,guard=guard,registered=False))
  for fault in ['ready','descriptor_nil','state_nil','device_nil']:
   m=Backend(image);m.depth_fault=fault;m.nested(0x12b364,[(0,CONTEXT),(1,0),(2,0 if fault=='device_nil' else DEVICE)])
   assert m.depth_state==(0 if fault in ['state_nil','device_nil'] else DEPTH)
   rows.append(dict(test='nativeDepthStateCreationCaller',build=build,fault=fault,published_state_nonnull=bool(m.depth_state),descriptor_device_runtime_modeled=True,return_value_not_interpreted=True))
 assert len(rows)==28
 data=dict(passed=True,cases=len(rows),scope='28 paired native/model records. Actual MetalContext renderDrawData caller, tiny/zero-geometry data copies, native block creation/copy/invoke/dispose and actual accepted cache body composed. Manual completion delivery and weak/runtime/Foundation/Metal/state providers modeled. Draw command list has no draw commands; setupRenderState and GPU pipeline/dequeue providers modeled. Actual device-object depth-state caller executes with explicit descriptors/device results. No GPU submission, real completion/ARC/thread/lifetime or performance proof.',records=rows)
 (RESULTS/'backend-completion-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
