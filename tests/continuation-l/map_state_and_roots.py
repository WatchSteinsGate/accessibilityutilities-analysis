"""Local-only bounded static provenance index; no raw instruction export."""
from pathlib import Path
import os,sys,struct,json,hashlib,bisect
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-l-static'))
sys.path.insert(0,str(HERE.parent/'continuation-b'))
from native import *
from capstone.arm64 import ARM64_OP_REG,ARM64_OP_MEM,ARM64_OP_IMM
TARGETS={0x1011b68:'controlOwnerSlot',0x1011e20:'overlayControlSlot',0x1011a18:'drawControlSlot',0x1011be0:'floatControlSlot',0x1010a37:'secondaryRequestByte',0x1010a2a:'secondaryGuardByte',0x10109c1:'startupGateByte'}
FOCUS={0x104488:'genericThreadLaunch',0x2d3f0:'workerScopeAcquire',0xf6694:'workerScopeNormalCleanup',0x3527c:'workerScopeCleanup',0x438dc:'secondaryTimer',0x7bae0:'secondaryCallback',0x76944:'constructorCallback',0x7aa4c:'lifecycleObservers',0x7b0b8:'suspend',0x7b9a4:'resume'}
def function_at(image,pc):
 start,end=image.bounds(pc)
 return hex(start) if end is not None and start<=pc<end else None
def scan(image):
 refs=[];calls=[];indirect=[];roots=[]
 detail=Cs(CS_ARCH_ARM64,CS_MODE_ARM);detail.detail=True
 text=[s for s in sections(image) if s['name']=='__text' and s['flags']&0x80000000]
 for sec in text:
  raw=image.bytes(sec['va'],sec['size'])
  for off in range(0,len(raw)-3,4):
   pc=sec['va']+off;word=struct.unpack_from('<I',raw,off)[0]
   if word&0x7c000000==0x14000000:
    imm=word&0x3ffffff
    if imm&(1<<25):imm-=1<<26
    target=pc+4*imm
    if target in FOCUS:calls.append(dict(site=hex(pc),target=hex(target),role=FOCUS[target],function=function_at(image,pc),kind='BL' if word&0x80000000 else 'B'))
   if word&0xfffffc1f in (0xd63f0000,0xd61f0000):
    owner=image.bounds(pc)[0]
    if owner in FOCUS:indirect.append(dict(site=hex(pc),function=hex(owner),kind='indirect'))
   if word&0x9f000000!=0x90000000:continue
   imm=((word>>29)&3)|(((word>>5)&0x7ffff)<<2)
   if imm&(1<<20):imm-=1<<21
   page=(pc&~4095)+(imm<<12)
   if page not in {a&~4095 for a in TARGETS}:continue
   base=word&31
   # Canonical ADRP-derived addresses only, within a straight-line 12-instruction window.
   known={base:page}
   for ins in detail.disasm(raw[off+4:off+4+48],pc+4):
    if ins.mnemonic.startswith(('b','ret','cb','tb')):break
    operands=ins.operands;updates={}
    if ins.mnemonic=='add' and len(operands)==3 and operands[0].type==ARM64_OP_REG and operands[1].type==ARM64_OP_REG and operands[2].type==ARM64_OP_IMM:
     src=ins.reg_name(operands[1].reg);dest=ins.reg_name(operands[0].reg)
     if src.startswith('x') and src[1:].isdigit() and int(src[1:]) in known:
      value=known[int(src[1:])]+operands[2].imm
      if dest.startswith('x') and dest[1:].isdigit():updates[int(dest[1:])]=value
      if value in TARGETS:refs.append(dict(site=hex(ins.address),slot=hex(value),role=TARGETS[value],access='address',function=function_at(image,ins.address)))
    for operand in operands:
     if operand.type!=ARM64_OP_MEM:continue
     name=ins.reg_name(operand.mem.base)
     if not name.startswith('x') or not name[1:].isdigit() or operand.mem.index:continue
     reg=int(name[1:])
     if reg not in known:continue
     value=known[reg]+operand.mem.disp
     if value in TARGETS:refs.append(dict(site=hex(ins.address),slot=hex(value),role=TARGETS[value],access='write' if ins.mnemonic.startswith(('st','cas','swp')) else 'read',function=function_at(image,ins.address)))
    # Invalidate all writes before retaining recognized address computations.
    try:written=ins.regs_access()[1]
    except:written=[]
    for reg in written:
     name=ins.reg_name(reg)
     if name.startswith(('x','w')) and name[1:].isdigit():known.pop(int(name[1:]),None)
    known.update(updates)
  # section instruction-window scan never treats read data as executed evidence
 for s in sections(image):
  if s['name']=='__mod_init_func':
   for off in range(0,s['size'],8):roots.append(dict(slot=hex(s['va']+off),entry=hex(q(image,s['va']+off))))
 unique={json.dumps(x,sort_keys=True):x for x in refs};refs=list(unique.values())
 methods=[dict(cls=m['cls'],selector=m['selector'],address=hex(m['address'])) for m in objc_methods(image) if m['cls'] in ['OverlayView','DrawWindow','FloatView','MetalContext','MetalBuffer'] and m['selector'] in ['.cxx_destruct','dealloc']]
 # Only metadata for possible deallocation in functions with an owner-slot reference.
 owner_funcs={int(x['function'],16) for x in refs if x['role']=='controlOwnerSlot' and x['function'] is not None}
 dealloc=[]
 for f in owner_funcs:
  _,end=image.bounds(f)
  for pc,sz,op,args in md.disasm_lite(image.bytes(f,end-f),f):
   if op not in ['bl','b'] or not args.startswith('#'):continue
   target=int(args[1:],0);name=IMPORTS.get(target,'')
   if name=='_free' or name.startswith('__Zdl') or name.startswith('__Zda'):dealloc.append(dict(site=hex(pc),function=hex(f),import_name=name))
 return dict(executable_text_sections=[dict(start=hex(s['va']),size=s['size']) for s in text],canonical_slot_references=sorted(refs,key=lambda r:int(r['site'],16)),focus_direct_edges=calls,focus_indirect_sites=indirect,initializer_roots=roots,selected_destructors=methods,owner_reference_functions_deallocation_imports=dealloc)
def main():
 maps={name:scan(m) for name,m in [('original',O),('r03',P)]}
 checks=[]
 for lo,hi in [(0x438dc,0x4393c),(0x7bae0,0x7bb84),(0x74d08,0x74de8),(0x622dc,O.bounds(0x622dc)[1]),(0x679fc,O.bounds(0x679fc)[1]),(0x687508,O.bounds(0x687508)[1]),(0x12f140,O.bounds(0x12f140)[1])]:
  a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);checks.append(dict(start=hex(lo),end_exclusive=hex(hi),equal=a==b,original_sha256=hashlib.sha256(a).hexdigest(),r03_sha256=hashlib.sha256(b).hexdigest()))
 data=dict(scope='Static canonical ADRP-derived address/load/store references within 12 straight-line instructions; all original and appended R03 __text sections scanned as aligned words. Direct B/BL edges to declared benign routing/flag helpers; finite LC_FUNCTION_STARTS attribution only (unknown boundaries are null), initializer roots and selected destructor metadata. Does not resolve indirect pointer aliases, register/stack spills, literal pointers, heap ownership, runtime replacement, indirect worker targets or genuine backend/security transitions. No instructions or inputs edited.',maps=maps,code_windows=checks)
 (RESULTS/'state-and-root-map.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({k:dict(refs=len(v['canonical_slot_references']),roots=len(v['initializer_roots']),owner_deallocation_imports=len(v['owner_reference_functions_deallocation_imports'])) for k,v in maps.items()}))
if __name__=='__main__':main()
