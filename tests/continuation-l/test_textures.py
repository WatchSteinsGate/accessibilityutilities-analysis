"""Local-only native texture callers with explicit decoder and Metal providers."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-textures'))
sys.path.insert(0,str(HERE.parent/'continuation-j'))
from test_overlay_return_menu import *
TDCLASS=0x200d0000;TD=0x200d0100;PIXELS=0x200d0200;DAT=0x200d1000;BYTES=0x200d2000
TEX=0x200d3000
class Texture(ReturnModel):
 def __init__(self,image,fault='ready'):
  super().__init__(image,True,True,[FLOAT,DRAW,MENU]);self.fault=fault;self.uploads=[];self.texture_calls=[];self.decode_calls=[];self.freed=[];self.draw_once=[];self.texture_count=0
  putq(self.e,0xff0998,TDCLASS);putq(self.e,0xff0990,DATACLASS)
  for slot in [0x10112f8,0x1011bd0,0x1011bd8,0x1011be8,0x1011ae0,0x10104b8]:putq(self.e,slot,0)
  # Stub only decoder leaves, not caller branch/geometry/publication bodies.
  self.e.calls[0x645228]=self.decode
  self.e.calls[0x65f974]=self.menu_pixels
  self.e.calls[0x6374b4]=self.menu_decode
  for a,n in IMPORTS.items():
   if n=='_free':self.e.calls[a]=self.free
   elif n=='_objc_retainAutorelease':self.e.calls[a]=lambda e:None
   elif n=='_objc_alloc':self.e.calls[a]=self.alloc
 def alloc(self,e):
  if e.get(0)==DATACLASS:e.set(0,DAT)
  else:self.allocate(e)
 def menu_decode(self,e):
  self.decode_calls.append(dict(role='menu-encoded-data',modeled=True));e.set(0,self.fault!='decode_nil')
 def menu_pixels(self,e):
  self.decode_calls.append(dict(role='menu-pixels',modeled=True))
  putq(e,e.get(1),0 if self.fault=='pixels_nil' else PIXELS)
  e.write(e.get(2),struct.pack('<i',2));e.write(e.get(3),struct.pack('<i',3))
 def decode(self,e):
  self.decode_calls.append(dict(role='child-image',requested_channels=e.get(5),modeled=True))
  e.write(e.get(2),struct.pack('<i',0 if self.fault=='width_zero' else 2));e.write(e.get(3),struct.pack('<i',-1 if self.fault=='height_negative' else 3));e.set(0,0 if self.fault=='decode_nil' else PIXELS)
 def free(self,e):
  self.freed.append(hex(e.get(0)));assert e.get(0)==PIXELS
 def once_boundary(self,e):
  if e.get(0)==0x10104b8:
   token=e.get(0);block=e.get(1);assert e.q(block+16)==0x18020
   self.draw_once.append('0x18020');return Work(0x18020,[(0,block)],False,lambda:putq(e,token,MASK))
  return super().once_boundary(e)
 def message(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if not r:e.set(0,0);return
  if r in [DRAW,FLOAT] and s=='initImageTexture:':
   self.texture_calls.append(dict(receiver=hex(r),selector=s));return Work(0x17f28 if r==DRAW else 0x123840,(),False,None)
  if r in [DRAW,FLOAT] and s=='loadImageTexture:::':
   self.texture_calls.append(dict(receiver=hex(r),selector=s));return Work(0x18324 if r==DRAW else 0x123b30,(),False,None)
  if r==DATACLASS and s=='alloc':e.set(0,DAT);return
  if r==DAT and s=='initWithBase64EncodedString:options:':e.set(0,DAT);return
  if r==DAT and s=='bytes':e.set(0,BYTES);return
  if r==DAT and s=='length':e.set(0,16);return
  if r==TDCLASS and s=='texture2DDescriptorWithPixelFormat:width:height:mipmapped:':
   assert a==70 and e.get(3)==2 and e.get(4)==3 and e.get(5)==0;e.set(0,0 if self.fault=='descriptor_nil' else TD);return
  if r==TD and s in ['setUsage:','setStorageMode:']:
   assert a==(1 if s=='setUsage:' else 0);return
  if r==DEVICE and s=='newTextureWithDescriptor:':
   assert a in [0,TD];self.texture_count+=1;e.set(0,0 if self.fault=='texture_nil' else TEX+self.texture_count*0x100);return
  if TEX<=r<TEX+0x10000 and s=='replaceRegion:mipmapLevel:withBytes:bytesPerRow:':
   # Region is a six-Q struct passed by address. Native callers construct it.
   region=list(struct.unpack('<6Q',e.u.mem_read(a,48)))
   self.uploads.append(dict(region=region,mipmap=e.get(3),bytes_per_row=e.get(5),modeled=True))
   assert region==[0,0,0,2,3,1] and e.get(4)==PIXELS and e.get(5)==8;return
  return super().message(e)

def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for role,receiver,entry in [('Draw',DRAW,0x18324),('Float',FLOAT,0x123b30)]:
   for fault in ['ready','decode_nil','width_zero','height_negative','descriptor_nil','texture_nil','device_nil','bytes_nil','length_zero']:
    m=Texture(image,fault);device=0 if fault=='device_nil' else DEVICE;source=0 if fault=='bytes_nil' else BYTES;length=0 if fault=='length_zero' else 16
    result=m.nested(entry,[(0,receiver),(1,0),(2,device),(3,source),(4,length)])
    upload=fault in ['ready','descriptor_nil']
    # Descriptor nil is messaged through to the modeled device; provider decides result.
    assert bool(m.uploads)==upload and bool(result)==upload,(role,fault,m.uploads,hex(result))
    rows.append(dict(test='nativeChildTextureLoader',build=build,role=role,fault=fault,returned_nonnull=bool(result),uploads=m.uploads,decode_calls=m.decode_calls,frees=m.freed,descriptor_nil_provider_may_return_texture=fault=='descriptor_nil'))
  for fault in ['ready','decode_nil','pixels_nil','descriptor_nil','texture_nil']:
   m=Texture(image,fault);m.device=DEVICE;m.nested(0x617460,[(0,MENU),(1,0),(2,SELF)])
   first=len(m.decode_calls);m.nested(0x617460,[(0,MENU),(1,0),(2,SELF)])
   cached=bool(m.e.q(0x10112f8));assert cached==(fault in ['ready','descriptor_nil'])
   assert bool(m.uploads)==cached
   rows.append(dict(test='nativeMenuTextureAndCache',build=build,fault=fault,cached=cached,decode_calls_first=first,decode_calls_total=len(m.decode_calls),uploads=m.uploads,global_overlay=hex(m.e.q(0x1011c88)),menu_image_handle=hex(m.e.q(0x1010e28)),decoder_and_gpu_modeled=True))
  # Full Overlay normal return with actual child callbacks and Menu texture body.
  m=Texture(image);m.fp(0.,0.,320.,240.);hit,result=m.initialize(0x20071000,stop=STOP)
  assert hit==STOP and result==SELF and m.uploads and m.draw_once==['0x18020']
  first_uploads=len(m.uploads)
  m.nested(0x17f28,[(0,DRAW),(1,0),(2,DEVICE)])
  assert len(m.uploads)==first_uploads and len(m.draw_once)==1
  m.nested(0x123840,[(0,FLOAT),(1,0),(2,DEVICE)])
  assert len(m.uploads)==first_uploads+1 # First Float texture refreshed; optional cached texture skipped.
  assert m.e.q(0x1011bd0) and not m.e.q(0x1011bd8)
  rows.append(dict(test='nativeOverlayTextureComposition',build=build,uploads_first=first_uploads,uploads_after_float_repeat=len(m.uploads),draw_once=m.draw_once,float_third_texture_skipped_by_native_mask=True,texture_calls=m.texture_calls,provider_boundaries=['base64 Foundation','image decode','Metal descriptor/device/upload','ObjC/ARC'],normal_return=True))
 assert len(rows)==48
 result=dict(passed=True,cases=len(rows),scope='48 native/model texture records, paired original/R03. Actual Draw once callback, Float init, both load bodies, Menu setter texture route and Overlay normal return composed. Image/base64 decode, ObjC/ARC, Metal descriptor/device/upload are explicit modeled providers. Synthetic faults, not device failures; descriptor nil does not force provider nil. No actual GPU/device/decoder success or performance claim.',records=rows)
 (RESULTS/'texture-tests.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
