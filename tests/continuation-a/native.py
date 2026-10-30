from pathlib import Path
import struct,sys,bisect,json,os,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RESULTS=Path(os.environ.get('AU_RESULTS',str(ROOT/'results/generated/continuation-a'))).resolve()
RESULTS.mkdir(parents=True,exist_ok=True)
from static_audit import MachO
from capstone import *
if not os.environ.get('AU_ORIGINAL') or not os.environ.get('AU_R03'):
 raise RuntimeError('Set AU_ORIGINAL and AU_R03 to the authorized framework input files; see docs/CONTINUATION-REPRODUCTION.md')
ORIGINAL=Path(os.environ['AU_ORIGINAL']).expanduser().resolve()
R03=Path(os.environ['AU_R03']).expanduser().resolve()
if ORIGINAL==R03:
 raise ValueError('AU_ORIGINAL and AU_R03 must identify distinct baseline files')
EXPECTED={ORIGINAL:'b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab',R03:'d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292'}
for path,digest in EXPECTED.items():
 assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,('Wrong input hash',str(path))
O=MachO(ORIGINAL)
P=MachO(R03)
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
def q(m,a):return struct.unpack('<Q',m.bytes(a,8))[0]
def cstr(m,a):
 try:return m.bytes(a,256).split(b'\0')[0].decode(errors='replace')
 except:return ''
def sections(m):
 out=[]
 for cmd,off,size in m.commands:
  if cmd==0x19:
   for i in range(struct.unpack_from('<I',m.b,off+64)[0]):
    s=off+72+i*80
    name,seg,va,sz,fo,al,relo,nrel,flags,r1,r2,r3=struct.unpack_from('<16s16sQQIIIIIIII',m.b,s)
    out.append(dict(name=name.rstrip(b'\0').decode(),seg=seg.rstrip(b'\0').decode(),va=va,size=sz,offset=fo,flags=flags,r1=r1,r2=r2))
 return out
def symbols(m):
 syms=[];stubs={}
 for cmd,off,size in m.commands:
  if cmd==2:
   so,n,ss,ns=struct.unpack_from('<IIII',m.b,off+8)
   for i in range(n):
    si,ty,se,de,va=struct.unpack_from('<IBBHQ',m.b,so+i*16)
    name=m.b[ss+si:].split(b'\0',1)[0].decode(errors='replace') if si else ''
    syms.append((name,va,ty))
  if cmd==0xb:indoff,nind=struct.unpack_from('<II',m.b,off+56)
 for s in sections(m):
  if s['flags']&255==8:
   for i in range(s['size']//s['r2']):
    ix=struct.unpack_from('<I',m.b,indoff+4*(s['r1']+i))[0]
    if ix<len(syms):stubs[s['va']+i*s['r2']]=syms[ix][0]
 return syms,stubs
SYMS,IMPORTS=symbols(O)
if __name__=='__main__':
 print('symbols',len(SYMS),'imports',len(IMPORTS))
 print('\n'.join(hex(a)+' '+n for n,a,t in SYMS if 'OverlayView' in n or ('drawInMTK' in n)))
 print('Imports',json.dumps({hex(a):s for a,s in IMPORTS.items() if 0x876200<=a<0x876700},indent=2))
def objc_methods(m):
 out=[]
 for s in sections(m):
  if s['name']!='__objc_classlist':continue
  for off in range(0,s['size'],8):
   cl=q(m,s['va']+off)
   for klass,kind in [(cl,'-'),(q(m,cl),'+')]:
    try:
     ro=q(m,klass+32)&~7;name=cstr(m,q(m,ro+24));ml=q(m,ro+32)
     if not ml:continue
     es,count=struct.unpack('<II',m.bytes(ml,8));stride=es&0xffff
     for i in range(count):
      a=ml+8+i*stride
      if es&0x80000000:
       n,t,imp=struct.unpack('<iii',m.bytes(a,12));sel=cstr(m,q(m,a+n));imp=a+8+imp
      else:n,t,imp=struct.unpack('<QQQ',m.bytes(a,24));sel=cstr(m,n)
      out.append(dict(cls=name,kind=kind,selector=sel,address=imp))
    except Exception:continue
 return out
