"""Native pipeline cache hit/miss/clear routes; shader creation remains a provider."""
from pathlib import Path
import os,sys,json,hashlib
HERE=Path(__file__).resolve().parent
os.environ.setdefault('AU_RESULTS',str(HERE.parents[1]/'results/generated/continuation-m-pipeline'))
sys.path.insert(0,str(HERE));from test_render_state import *
PCACHE=0x200c7000;KEY=0x200c8000;KEY2=0x200c9000;DEVICE2=0x200ca000
class Pipeline(State):
 def __init__(self,image,seed=False,success=True,cache_live=True):
  super().__init__(image,[dict()],pipeline=success);self.pc={KEY:PIPE} if seed else {};self.builds=[];self.cache_events=[];self.key=KEY;self.cache_live=cache_live
 def msg(self,e):
  r=e.get(0);s=e.cs(e.get(1));a=e.get(2)
  if not r:e.set(0,0);return
  if r==CONTEXT:
   if s=='renderPipelineStateForFrameAndDevice:':return Work(0x12c798,(),False,None)
   if s=='renderPipelineStateCache':e.set(0,PCACHE if self.cache_live else 0);return
   if s=='framebufferDescriptor':e.set(0,self.key);return
   if s=='_renderPipelineStateForFramebufferDescriptor:device:':
    assert a==self.key and e.get(3) in [DEVICE,DEVICE2]
    self.builds.append(dict(key=hex(a),device=hex(e.get(3)),nonnull=self.pipeline));e.set(0,PIPE if self.pipeline else 0);return
  if r==PCACHE:
   if s=='objectForKeyedSubscript:':self.cache_events.append('lookup');e.set(0,self.pc.get(a,0));return
   if s=='setObject:forKeyedSubscript:':
    key=e.get(3);assert key in [KEY,KEY2]
    if a:self.pc[key]=a;self.cache_events.append('insert')
    else:self.pc.pop(key,None);self.cache_events.append('nil-subscript-removal-provider')
    return
   if s=='removeAllObjects':self.pc.clear();self.cache_events.append('clear');return
  return super().msg(e)
 def get(self,device=DEVICE):return self.nested(0x12c798,[(0,CONTEXT),(1,0),(2,device)])
 def clear(self):self.nested(0x12de18,[(0,CONTEXT),(1,0)])
 def state(self):return dict(builds=self.builds,cache_events=self.cache_events,cache={hex(k):hex(v) for k,v in self.pc.items()})
def main():
 rows=[]
 for build,image in [('original',O),('r03',P)]:
  for case in ['hit','coldSuccess','coldNil','failureThenRecovery','clearThenRebuild','keyChange','deviceChangeSameKey','nilCacheGetter']:
   m=Pipeline(image,seed=case in ['hit','clearThenRebuild','deviceChangeSameKey'],success=case not in ['coldNil','failureThenRecovery'],cache_live=case!='nilCacheGetter')
   if case=='clearThenRebuild':m.clear()
   first=m.get()
   if case=='failureThenRecovery':m.pipeline=True
   if case=='keyChange':m.key=KEY2
   second=m.get(DEVICE2 if case=='deviceChangeSameKey' else DEVICE)
   count=0 if case in ['hit','deviceChangeSameKey'] else (2 if case in ['coldNil','failureThenRecovery','keyChange','nilCacheGetter'] else 1)
   assert len(m.builds)==count,(case,m.state())
   assert first==(0 if case in ['coldNil','failureThenRecovery'] else PIPE)
   assert second==(0 if case=='coldNil' else PIPE)
   if case=='keyChange':assert len(m.pc)==2
   if case in ['coldNil','nilCacheGetter']:assert not m.pc
   rows.append(dict(test='nativePipelineCacheSequence',build=build,case=case,returns_nonnull=[bool(first),bool(second)],state=m.state(),device_change_synthetic_not_established=case=='deviceChangeSameKey'))
  for case in ['coldSuccess','cacheHit','buildNil','nilCacheGetter']:
   m=Pipeline(image,seed=case=='cacheHit',success=case!='buildNil',cache_live=case!='nilCacheGetter');m.render()
   assert len(m.draws)==1 and len(m.native_setup_requests)==1 and len(m.requests)==1 and len(m.builds)==int(case!='cacheHit')
   rows.append(dict(test='nativePipelineCacheToStateAndDraw',build=build,case=case,state=m.state(),native_setup_calls=len(m.native_setup_requests),draws=m.draws,completion_registration=len(m.requests),modeled_encoder_acceptance_not_gpu_success=True))
 assert len(rows)==24
 checks=[]
 for lo in [0x12c798,0x12de18]:
  hi=O.bounds(lo)[1];a,b=O.bytes(lo,hi-lo),P.bytes(lo,hi-lo);assert a==b
  checks.append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=hashlib.sha256(a).hexdigest(),equal=True))
 data=dict(passed=True,cases=len(rows),scope='24 paired native/model records. Native pipeline cache lookup/miss/insertion and empty-cache bodies, including full render -> native cache -> native state -> native nonempty draw -> completion registration composition. Dictionary/getters/keys, shader/pipeline creation and Metal encoder/ARC are explicit providers. Nil keyed-subscript insertion modeled as removal; not a Foundation runtime test. Synthetic key/device changes and recovery, no actual multi-device occurrence, cache races, shader compilation/GPU validity/completion or performance inference.',code_equality=checks,records=rows)
 (RESULTS/'pipeline-cache-tests.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
if __name__=='__main__':main()
