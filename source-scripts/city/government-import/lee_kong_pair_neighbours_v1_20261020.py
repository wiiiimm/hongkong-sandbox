"""Full changed-domain basic neighbour checks for private Lee Kong terrain."""
from pathlib import Path
import subprocess,numpy as np,json,sys,uuid
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong-pair-neighbours-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-lee-kong-pair-runtime-v1-20261020';SCOPE=BASE/'government-xl-lee-kong72296-current-scope-v1-20261020';UID='landsd/72296:0'
def owned():
 lease=read(HERE/'local'/BATCH/'reservation.json');assert reservations.owns(lease)
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SCOPE]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
 assert read(BASE/'government-xl-lee-kong72296-private-ground-v1-20261020/result.json')['guardFailure'] is None # Terrain validator passed; neighbour checks remain independent.
 scope=dict(changedParentExtent=read(SCOPE/'scope.json')['rows'][0]['overlappingInstalledTerrain'][0]['extent']);inventory=read(SCOPE/'complete-bounds.json.gz')['rows'];required=[r['uid']for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],scope['changedParentExtent'])];save(DOC/'actor-scope.json',dict(completeActorCount=len(inventory),changedParentExtent=scope['changedParentExtent'],requiredNativeUids=required));refs.append(HERE/'heritage_saved_native_bounds_binding_v1_20261014.py')
 final=module('fu_neighbour_context',HERE/'xl-final-script-pass.py');near=final.load_forms(scope['changedParentExtent']);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for entry in read(path)['models']:entries[entry['uid']]=entry
 needed=set(required)
 for uid in required:needed.update(d['uid']for d in entries[uid].get('supportDependencies',[]))
 byuid={b['uid']:(b,tile)for b,_,tile in near}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']in needed and b['uid']not in byuid:byuid[b['uid']]=(b,tile['url'])
 assert needed<=set(byuid)
 inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for _,tile in byuid.values()};patches=read(CAP/'terrain-candidates.json');save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in entries)for b,_ in byuid.values()],patches=patches,candidateIds=[UID,'landsd/253697:0'],requiredNativeUids=required,inputHashes=inputs))
 for tool in ['check-neighbours.mjs','check-native-neighbours.mjs']:
  subprocess.run(['node',str(HERE/tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 native=read(DOC/'native-neighbour-checks.json')
 geometrypath=HERE/'local'/CAP.name/'runtime-geometry.json.gz';foundation=next(x['foundation'] for x in read(CAP/'result.json')['foundations'] if x['uid']==UID);save(DOC/'foundation.json',foundation)
 report=read(DOC/'neighbour-checks.json');summary=dict(uid=UID,neighbourForms=len(byuid),requiredNativeUids=required,nativeChecks=native['rows'],flagged=[dict(uid=x['uid'],reasons=x['reasons'],beforeGap=x['beforeGap'],afterGap=x['afterGap'])for x in report['rows']if x['reasons']],foundation={k:v for k,v in foundation.items()if k!='components'},installationApproved=False);save(DOC/'summary.json',summary);print(dict(uid=UID,neighbourForms=len(byuid),requiredNativeActors=len(required),flagged=len(summary['flagged'])),flush=True)
 for p,h in {**pins,**report['inputHashes'],**native['inputHashes'],**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([geometrypath,HERE/'xl-final-script-pass.py',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs'])
 module('times_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lee-kong72296-full-parent-neighbours-and-foundation',list(dict.fromkeys(refs)),dict(uids=[UID,'landsd/253697:0'],summary=summary,installationApproved=False))
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists()
 scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']==UID)
 retained=scope['overlappingInstalledTerrain'][0]['parentNativeUids']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(set(['building:'+UID,'building:landsd/253697:0','terrain-patch:'+UID]+['building:'+u for u in retained])),batch=BATCH,ttl=3600);assert claim['ok']
 lease=claim['reservation'];path=HERE/'local'/BATCH/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

