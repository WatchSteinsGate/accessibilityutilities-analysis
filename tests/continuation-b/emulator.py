from native import *
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn import arm64_const as R
REGS=[getattr(R,'UC_ARM64_REG_X'+str(i)) for i in range(29)]+[R.UC_ARM64_REG_X29,R.UC_ARM64_REG_X30]
STOP=0x3003f000;SP=0x30030000
class E:
 def __init__(self,m):
  self.m=m;self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.calls={};self.stops={STOP};self.hit=None;self.events=[];self.visited=set()
  end=max(v+vs for _,v,vs,fo,fs in m.segments);self.u.mem_map(0,(end+4095)&~4095)
  for _,v,vs,fo,fs in m.segments:
   if fs:self.u.mem_write(v,m.b[fo:fo+fs])
  self.u.mem_map(0x20000000,0x100000);self.u.mem_map(0x30000000,0x40000)
  self.u.reg_write(R.UC_ARM64_REG_CPACR_EL1,3<<20)
  # Bind only the external stack-canary reference used by these methods.
  if self.q(0xfd82e0)==0:
   self.write(0xfd82e0,struct.pack('<Q',0x200ff000));self.write(0x200ff000,struct.pack('<Q',0x94a7bcd10866e513))
  self.u.hook_add(UC_HOOK_CODE,self.hook)
  self.u.hook_add(UC_HOOK_MEM_READ,self.read_guard)
 def read_guard(self,u,access,address,size,value,data):
  if address<4096:raise AssertionError(('unexpected low-page dereference',hex(address)))
 def get(self,n):return self.u.reg_read(REGS[n])
 def set(self,n,v):self.u.reg_write(REGS[n],v&((1<<64)-1))
 def write(self,a,v):self.u.mem_write(a,v)
 def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
 def byte(self,a):return self.u.mem_read(a,1)[0]
 def cs(self,a):return bytes(self.u.mem_read(a,256)).split(b'\0')[0].decode(errors='replace')
 def hook(self,u,a,size,data):
  self.visited.add(a)
  if a in self.stops:self.hit=a;u.emu_stop();return
  if a in self.calls:
   self.calls[a](self);self.u.reg_write(R.UC_ARM64_REG_PC,self.get(30));return
  if a in IMPORTS:raise AssertionError(('Unmodeled import',IMPORTS[a],hex(a)))
 def run(self,a,args=(),stops=(),stack_pointer=SP):
  self.hit=None;self.stops={STOP,*stops};self.set(30,STOP);self.u.reg_write(R.UC_ARM64_REG_SP,stack_pointer)
  for n,v in args:self.set(n,v)
  try:self.u.emu_start(a,STOP+4,count=100000)
  except Exception as ex:raise RuntimeError((str(ex),'pc='+hex(self.u.reg_read(R.UC_ARM64_REG_PC)))) from ex
  assert self.hit is not None,('instruction bound exhausted',hex(self.u.reg_read(R.UC_ARM64_REG_PC)))
  return self.get(0)
 def noop(self,addresses):
  for a in addresses:self.calls[a]=lambda e:None
 def journal(self):self.calls[0x6e0990]=lambda e:None
 def ownership(self):
  for a,n in IMPORTS.items():
   if n in ['_objc_retain','_objc_retainAutoreleasedReturnValue','_objc_retainAutoreleaseReturnValue','_objc_autoreleaseReturnValue','_objc_retainBlock']:self.calls[a]=lambda e:None
   if n=='_objc_release':self.calls[a]=lambda e:None
   if n=='_objc_storeStrong':self.calls[a]=lambda e:e.write(e.get(0),struct.pack('<Q',e.get(1)))
