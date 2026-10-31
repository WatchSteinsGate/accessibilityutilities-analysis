"""Native nonempty render-command routing with explicit Metal/callback providers."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-m-render'))
sys.path.insert(0,str(HERE.parent/'continuation-l'));from test_backend_completion import *
CMDS=0x200a0000;TEXTURE=0x200a1000;CALLBACK=0x200a2000;DL2=0x200a3000;CMDS2=0x200a4000
class Render(Backend):
 def __init__(self,image,commands,origin=(0.,0.),scale=(1.,1.),two_lists=False):
  super().__init__(image);self.scissors=[];self.textures=[];self.offsets=[];self.draws=[];self.callbacks=[];self.setup_offsets=[]
  self.e.write(DD+8,struct.pack('<ii',8,8));self.e.write(DL+0x10,struct.pack('<i',8));self.e.write(DL+0x20,struct.pack('<i',8))
  self.e.write(SOURCEV,bytes(range(160)));self.e.write(SOURCEI,struct.pack('<8H',0,1,2,0,1,2,0,1));self.buffers[W1]=(B1,160);self.buffers[W2]=(B2,16)
  self.e.write(DD+0x18,struct.pack('<2f',*origin));self.e.write(DD+0x28,struct.pack('<2f',*scale))
  self.commands(DL,CMDS,commands)
  if two_lists:
   putq(self.e,LISTS+8,DL2);self.e.write(DL2,bytes(self.e.u.mem_read(DL,0x40)));self.commands(DL2,CMDS2,commands)
   self.e.write(DD+4,struct.pack('<iii',2,16,16));self.buffers[W1]=(B1,320);self.buffers[W2]=(B2,32)
  self.e.calls[CALLBACK]=self.callback
 def memcpy(self,e):
  assert e.get(2) in [160,16];e.write(e.get(0),bytes(e.u.mem_read(e.get(1),e.get(2))));self.copies.append(e.get(2))
 def commands(self,dl,base,cmds):
  self.e.write(dl,struct.pack('<iiQ',len(cmds),len(cmds),base))
  for i,c in enumerate(cmds):
   a=base+i*0x38;self.e.write(a,bytes(0x38));self.e.write(a,struct.pack('<4fQIII',*c.get('clip',(10.,20.,110.,120.)),c.get('texture',TEXTURE),c.get('voff',0),c.get('ioff',0),c.get('elements',3)));putq(self.e,a+0x28,c.get('callback',0))
 def callback(self,e):
  assert e.get(0) in [DL,DL2] and CMDS<=e.get(1)<CMDS2+0x100
  self.callbacks.append(dict(list=hex(e.get(0)),command=hex(e.get(1)),delivery='native BLR to modeled callback'))
 def msg(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if r==ENC:
   if s=='setScissorRect:':self.scissors.append(list(struct.unpack('<4Q',e.u.mem_read(a,32))));return
   if s=='setFragmentTexture:atIndex:':assert e.get(3)==0;self.textures.append(a);return
   if s=='setVertexBufferOffset:atIndex:':assert e.get(3)==0;self.offsets.append(a);return
   if s=='drawIndexedPrimitives:indexCount:indexType:indexBuffer:indexBufferOffset:':
    assert a==3 and e.get(4)==0 and e.get(5)==B2
    self.draws.append(dict(index_count=e.get(3),index_type=e.get(4),index_buffer_offset=e.get(6)));return
  if r==CONTEXT and s.startswith('setupRenderState:'):self.setup_offsets.append(e.get(7))
  return super().msg(e)
 def render(self):self.nested(0x12e2d0,[(0,CONTEXT),(1,0),(2,DD),(3,CMD),(4,ENC)])
 def state(self):return dict(scissors=self.scissors,texture_bindings=[hex(x) for x in self.textures],vertex_byte_offsets=self.offsets,draws=self.draws,callbacks=self.callbacks,setup_vertex_byte_offsets=self.setup_offsets,completion_requests=len(self.requests))
def main():
 rows=[]
 specs=[('normal',(10,20,110,120),[10,20,100,100]),('negativeClamp',(-10,-20,10,20),[0,0,10,20]),('overflowClamp',(310,230,400,300),[310,230,10,10]),('outsideLeft',(-20,0,-1,10),None),('outsideRight',(400,0,500,10),None),('empty',(1,1,1,3),None),('inverted',(5,5,1,1),None),('fractionalPositive',(1.5,2.5,1.75,2.75),[1,2,0,0]),('zeroElements',(0,0,10,10),None),('nilTexture',(0,0,10,10),[0,0,10,10]),('offsetScale',(15,30,65,80),[20,40,100,100]),('negativeOrigin',(0,0,10,10),[5,10,10,10])]
 for build,image in [('original',O),('r03',P)]:
  for name,clip,want in specs:
   c=dict(clip=clip,voff=2,ioff=3,elements=0 if name=='zeroElements' else 3,texture=0 if name=='nilTexture' else TEXTURE)
   m=Render(image,[c],origin=(5,10) if name=='offsetScale' else ((-5,-10) if name=='negativeOrigin' else (0,0)),scale=(2,2) if name=='offsetScale' else (1,1));m.render()
   assert m.scissors==([want] if want is not None else []),(name,m.state())
   assert len(m.draws)==int(want is not None) and len(m.requests)==1
   if want is not None:
    assert m.offsets==[40] and m.draws[0]['index_buffer_offset']==6
    assert m.textures==([] if name=='nilTexture' else [TEXTURE])
   else:assert not m.textures and not m.offsets
   rows.append(dict(test='nativeDrawCommandClipAndOffsets',build=build,case=name,state=m.state(),synthetic_geometry_with_offsets_in_buffer_capacity=True))
  for cb in ['custom','reset']:
   m=Render(image,[dict(callback=CALLBACK if cb=='custom' else (1<<64)-1)]);m.render()
   assert not m.draws and not m.scissors and len(m.callbacks)==int(cb=='custom') and len(m.setup)==(2 if cb=='reset' else 1)
   rows.append(dict(test='nativeDrawCommandCallback',build=build,case=cb,state=m.state(),callback_or_setup_body_modeled=True))
  m=Render(image,[dict(),dict(texture=0,voff=1,ioff=2)]);m.render()
  assert len(m.draws)==2 and m.textures==[TEXTURE] and m.offsets==[0,20] and [d['index_buffer_offset'] for d in m.draws]==[0,4]
  rows.append(dict(test='nativeDrawCommandSequence',build=build,state=m.state(),nil_texture_skips_rebinding_not_clearing=True))
  m=Render(image,[dict()],two_lists=True);m.render()
  assert m.offsets==[0,160] and [d['index_buffer_offset'] for d in m.draws]==[0,16] and m.copies==[160,16,160,16]
  assert bytes(m.e.u.mem_read(MEM1+160,160))==bytes(range(160)) and bytes(m.e.u.mem_read(MEM2+16,16))==struct.pack('<8H',0,1,2,0,1,2,0,1)
  rows.append(dict(test='nativeTwoDrawListOffsets',build=build,state=m.state(),copy_sizes=m.copies,second_list_native_byte_copies_verified=True))
 assert len(rows)==32
 lo,hi=0x12e2d0,0x12ecf8;a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
 data=dict(passed=True,cases=len(rows),scope='32 paired native/model records. Nonempty synthetic draw-command lists execute native render body, clip conversion/clamp/rejection, callback/reset routing, texture and vertex/index offset calculations, and multi-list byte copies. External Metal encoder/state/buffer/callback providers modeled; no shader/GPU or actual draw. Eight synthetic vertices/indices per list keep tested normal offsets/counts within supplied buffer capacity; no genuine GPU-validity claim. No performance/root-cause, actual completion, concurrency or pointer lifetime proof.',code_equality=dict(start=hex(lo),end_exclusive=hex(hi),sha256=hashlib.sha256(a).hexdigest(),equal=True),records=rows)
 (RESULTS/'render-command-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
