"""Bounded local def-use map from existing canonical control-slot loads to byte zero."""
from pathlib import Path
import os,sys,json,struct,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-m-static'))
sys.path.insert(0,str(HERE.parent/'continuation-b'));from native import *
from capstone.arm64 import ARM64_OP_REG,ARM64_OP_MEM,ARM64_OP_IMM
SLOTS={'controlOwnerSlot','overlayControlSlot','drawControlSlot','floatControlSlot'}
def rn(ins,operand):
 if operand.type!=ARM64_OP_REG:return None
 s=ins.reg_name(operand.reg)
 return int(s[1:]) if s.startswith(('x','w')) and s[1:].isdigit() else None
def scan(image,refs):
 d=Cs(CS_ARCH_ARM64,CS_MODE_ARM);d.detail=True;out=[];escapes=[]
 for ref in refs:
  if ref['role'] not in SLOTS or ref['access']!='read':continue
  start=int(ref['site'],16);rows=list(d.disasm(image.bytes(start,160),start))
  if not rows:continue
  load=rows[0]
  if load.mnemonic!='ldr' or not load.operands or rn(load,load.operands[0]) is None:continue
  known={rn(load,load.operands[0]):0}
  for ins in rows[1:]:
   if ins.group(CS_GRP_CALL) or ins.mnemonic in ['br','blr']:
    regs={f'x{k}':v for k,v in known.items() if k<8}
    if regs:escapes.append(dict(slot=ref['slot'],role=ref['role'],source_load=ref['site'],site=hex(ins.address),argument_offsets=regs,indirect=ins.mnemonic in ['br','blr']))
    break
   if ins.group(CS_GRP_JUMP) or ins.group(CS_GRP_RET):break
   ops=ins.operands;updates={}
   if ins.mnemonic=='mov' and len(ops)==2 and ops[1].type==ARM64_OP_REG:
    src=rn(ins,ops[1]);dst=rn(ins,ops[0])
    if src in known and dst is not None and ins.reg_name(ops[0].reg).startswith('x'):updates[dst]=known[src]
   if ins.mnemonic=='add' and len(ops)==3 and ops[2].type==ARM64_OP_IMM:
    src=rn(ins,ops[1]);dst=rn(ins,ops[0])
    if src in known and dst is not None:updates[dst]=known[src]+ops[2].imm
   for op in ops:
    if op.type!=ARM64_OP_MEM or op.mem.index:continue
    n=ins.reg_name(op.mem.base);reg=int(n[1:]) if n.startswith('x') and n[1:].isdigit() else None
    if reg not in known or known[reg]+op.mem.disp!=0:continue
    store=ins.mnemonic.startswith(('st','cas','swp'))
    width=1 if ins.mnemonic.endswith('b') else (2 if ins.mnemonic.endswith('h') else (8 if ops and ops[0].type==ARM64_OP_REG and ins.reg_name(ops[0].reg).startswith('x') else 4))
    f,e=image.bounds(ins.address)
    out.append(dict(site=hex(ins.address),source_load=ref['site'],slot=ref['slot'],role=ref['role'],access='write' if store else 'read',width_bytes=width,function=hex(f) if e is not None else None,function_entry_is_ret=bool(e is not None and image.bytes(f,4)==bytes.fromhex('c0035fd6'))))
   for r in ins.regs_access()[1]:
    n=ins.reg_name(r)
    if n.startswith(('w','x')) and n[1:].isdigit():known.pop(int(n[1:]),None)
   known.update(updates)
   if not known:break
 return dict(byte_zero_accesses=out,call_argument_escapes=escapes)
def main():
 source=HERE.parents[1]/'results/continuations/continuation-l/state-and-root-map.json';prior=json.loads(source.read_text())
 maps={b:scan(image,prior['maps'][b]['canonical_slot_references']) for b,image in [('original',O),('r03',P)]}
 data=dict(scope='Static bounded def-use after canonical control-slot LDRs retained by continuation-l; at most 39 following instructions, same straight-line block, copies/adds with overwritten-register invalidation. Records only offset-zero accesses and call-argument escapes. No branch merge, stack spills, indirect alias, heap/free completeness or runtime execution claim. Candidate access metadata flags a RET at known function entry: residual instructions in such a function are not established reachable from that entry. Width inference supports observed simple byte/half/word/doubleword loads/stores, not arbitrary atomics/vector pairs. No input edited.',source_index_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),maps=maps)
 (RESULTS/'control-pointee-map.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({b:dict(accesses=len(v['byte_zero_accesses']),writes=[x for x in v['byte_zero_accesses'] if x['access']=='write'],argument_escapes=len(v['call_argument_escapes'])) for b,v in maps.items()}))
if __name__=='__main__':main()
