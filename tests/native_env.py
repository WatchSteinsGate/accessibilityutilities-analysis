# Read-only native instruction harness; all writes target emulated memory.
from pathlib import Path
import sys,struct,json,itertools
from macho import MachO
import os,hashlib
from unicorn import *
from unicorn import arm64_const as R
from capstone import *
def load_input(variable, expected):
 path=os.environ.get(variable)
 if not path: raise RuntimeError(f'Set {variable} to an authorized local input; binaries are not distributed here.')
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError(f'{variable} input SHA-256 does not match this bounded test suite')
 return MachO(path)
orig=load_input('AU_ORIGINAL','b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab')
cur=load_input('AU_R03','d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292')
# Independently resolve imported stubs using original Mach-O indirect symbol table.
def imports(m):
 b=m.b; sy=next(o for c,o,s in m.commands if c==2);dy=next(o for c,o,s in m.commands if c==11)
 sym,n,st,sz=struct.unpack_from('<IIII',b,sy+8);ind,ni=struct.unpack_from('<II',b,dy+56);out={}
 for c,o,s in m.commands:
  if c!=25:continue
  for k in range(struct.unpack_from('<I',b,o+64)[0]):
   q=o+72+k*80;name=b[q:q+16].rstrip(b'\0')
   if name!=b'__stubs':continue
   a,z=struct.unpack_from('<QQ',b,q+32);base,stride=struct.unpack_from('<II',b,q+68)
   for j in range(z//stride):
    ix=struct.unpack_from('<I',b,ind+4*(base+j))[0]
    if ix&0xc0000000:continue
    si=struct.unpack_from('<I',b,sym+16*ix)[0];end=b.find(b'\0',st+si);out[a+j*stride]=b[st+si:end].decode()
 return out
imp=imports(orig)
assert imp[0x87666c]=='_objc_retainAutoreleasedReturnValue' and imp[0x87663c]=='_objc_release' and imp[0x8766b4]=='_objc_storeStrong'
class E:
 def __init__(self,m,slide=0):
  self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.slide=slide;self.u.mem_map(slide,0x1100000)
  for _,a,v,o,n in m.segments:
   if n:self.u.mem_write(slide+a,m.b[o:o+n])
  self.u.mem_map(0x20000000,0x20000);self.u.mem_map(0x30000000,0x20000);self.set(30,0x3001f000);self.u.reg_write(R.UC_ARM64_REG_SP,0x30010000);self.stops={0x3001f000};self.calls={};self.hit=None;self.u.hook_add(UC_HOOK_CODE,self.hook)
 def set(self,n,x):self.u.reg_write(getattr(R,'UC_ARM64_REG_X'+str(n)),x)
 def get(self,n):return self.u.reg_read(getattr(R,'UC_ARM64_REG_X'+str(n)))
 def write(self,a,b):self.u.mem_write(a,b)
 def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def hook(self,u,a,n,d):
  if a in self.stops:self.hit=a;u.emu_stop();return
  if a-self.slide in self.calls:self.calls[a-self.slide](self);u.reg_write(R.UC_ARM64_REG_PC,self.get(30))
 def run(self,a):
  self.hit=None;self.u.emu_start(self.slide+a,self.slide+0x1100000,count=100000);assert self.hit is not None
