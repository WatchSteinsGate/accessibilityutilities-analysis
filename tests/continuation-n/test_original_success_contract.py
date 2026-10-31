"""Original frame success obligations composed with actual Float writer; no FPS testing."""
from pathlib import Path
import os,sys,json,ast,struct,itertools,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-n'))
sys.path.insert(0,str(HERE.parent/'continuation-e'));from test_factories import Model as NestedModel,Work,YieldingE
sys.path.insert(0,str(HERE.parent/'continuation-m'));from test_control_writers import Writers
# Load only reviewed helper declarations, never the earlier module's top-level case loop.
source=HERE.parent/'continuation-a/test_render.py';tree=ast.parse(source.read_text())
body=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in node.targets):break
 body.append(node)
ns={'__file__':str(source),'__name__':'success_contract_frame_helper'}
exec(compile(ast.Module(body=body,type_ignores=[]),str(source),'exec'),ns)
ns['E']=YieldingE
Frame=ns['Model'];O=ns['O'];P=ns['P'];RESULTS=ns['RESULTS'];STOP=ns['STOP'];SELF=ns['SELF'];VIEW=ns['VIEW'];CTRL=ns['CTRL'];FLOAT=ns['FLOAT'];IO=ns['IO']
class Contract(Frame,NestedModel):
 def __init__(self,image,menu,hidden,click):
  Frame.__init__(self,image);self.depth=0
  w=Writers(image,0,True,True,click,3)
  for address in [0x1386d8,0x123490,0x13fc1c,0x14cb88,0x14ca90,0x14cb1c,0x13fcfc,0x123568,0x68ad54,0x12422c,0x124250,0x144a68]:self.e.calls[address]=w.e.calls[address]
  w.e=self.e;self.writer=w
  for slot in [0x1011bd0,0x1011bd8,0x1011be8]:self.e.write(slot,struct.pack('<Q',0x2001a000))
  self.e.write(IO,bytes(0xe00));self.e.write(CTRL,bytes([menu,hidden]));self.e.write(0x1011be0,struct.pack('<Q',CTRL));self.e.write(0x1010c30,b'\1')
 def msg(self,e):
  sel=e.cs(e.get(1));r=e.get(0)
  Frame.msg(self,e)
  if r==FLOAT and sel=='drawFloatWindow':return Work(0x1230e4,(),False,None)
 def success(self):
  self.events=[];self.refs.clear();self.nested(0x685d6c,[(0,SELF),(1,0),(2,VIEW)])
  assert not {p:n for p,n in self.refs.items() if n}
  names=self.names(self.events)
  assert 'presentDrawable:' in names and 'commit' in names and 'endEncoding' in names
  assert names.index('endEncoding')<names.index('presentDrawable:')<names.index('commit')
  return dict(message_order=names,control_after=self.e.byte(CTRL),reset_after=self.e.byte(0x1010c30),float_gui_events=self.writer.events,balanced_modeled_frame_ownership=True)
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for menu,hidden,click in itertools.product([0,1],[0,1],[False,True]):
   c=Contract(image,menu,hidden,click);state=c.success()
   assert ('drawFloatWindow' in state['message_order'])==bool(not hidden)
   assert state['control_after']==(1 if build=='original' and not hidden and click else menu)
   assert ('drawMenuWindow' in state['message_order'])==bool(menu or (build=='original' and not hidden and click))
   assert state['reset_after']==(0 if build=='original' and not hidden else 1)
   assert bool(state['float_gui_events'])==(build=='original' and not hidden)
   rows.append(dict(test='nativeOriginalFrameFloatSuccessObligation',build=build,menu_before=menu,float_hidden=hidden,click_provider=click,preserves_original_float_gui_invocation=build=='original' or bool(hidden),preserves_original_same_frame_menu_invocation=('drawMenuWindow' in state['message_order'])==bool(menu or (not hidden and click)),**state))
 assert len(rows)==16
 d=dict(passed=True,cases=16,scope='Original-success preservation contract, not FPS/crash testing. Actual native Overlay frame body composes with actual Float draw body and shared control allocation; R03 immediate return is expected divergence. Eligible lifecycle/resources, GUI Begin/click, other Draw/Menu bodies, collector, backend encoding, ObjC/ARC/UIKit/Metal remain providers. Native end/present/commit order and modeled temporary ownership checked; no actual visible rendering or whole-original-success/minimality proof.',helper_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),records=rows)
 (RESULTS/'original-success-contract-tests.json').write_text(json.dumps(d,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=16)))
 for r in rows:
  if r['menu_before']==0 and not r['float_hidden'] and r['click_provider']:print(r['build'],'control',r['control_after'],'menu-call', 'drawMenuWindow' in r['message_order'],'GUI',r['float_gui_events'])
if __name__=='__main__':main()
