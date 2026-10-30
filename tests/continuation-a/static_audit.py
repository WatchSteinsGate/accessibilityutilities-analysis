from pathlib import Path
import sys,struct,json,bisect
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
class MachO:
 def __init__(self,path):
  self.path=Path(path);self.b=self.path.read_bytes();self.segments=[];self.starts=[];self.commands=[]
  assert struct.unpack_from('<I',self.b)[0]==0xfeedfacf
  off=32
  for _ in range(struct.unpack_from('<I',self.b,16)[0]):
   cmd,size=struct.unpack_from('<II',self.b,off);assert size>=8 and off+size<=len(self.b);self.commands.append((cmd,off,size))
   if cmd==0x19:
    name,va,vs,fo,fs=struct.unpack_from('<16sQQQQ',self.b,off+8);self.segments.append((name.rstrip(b'\0').decode(),va,vs,fo,fs))
   off+=size
  text=next(s[1] for s in self.segments if s[0]=='__TEXT')
  for cmd,off,size in self.commands:
   if cmd==0x26:
    begin,length=struct.unpack_from('<II',self.b,off+8);pos=begin;end=begin+length;addr=text
    while pos<end:
     value=0;shift=0
     while True:
      v=self.b[pos];pos+=1;value|=(v&127)<<shift
      if not v&128:break
      shift+=7
     if value==0:break
     addr+=value;self.starts.append(addr)
 def bytes(self,va,size):
  for _,base,vs,fo,fs in self.segments:
   if base<=va and va+size<=base+fs:return self.b[fo+va-base:fo+va-base+size]
  raise ValueError(f'Unmapped address {va:x}, size {size:x}')
 def bounds(self,va):
  i=bisect.bisect_right(self.starts,va)-1
  return self.starts[i],self.starts[i+1] if i+1<len(self.starts) else None
 def dump(self,start,end,path):
  md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);rows=list(md.disasm_lite(self.bytes(start,end-start),start))
  path.write_text('\n'.join(f'{a:010x}: {m:9} {o}' for a,size,m,o in rows)+'\n');return rows
