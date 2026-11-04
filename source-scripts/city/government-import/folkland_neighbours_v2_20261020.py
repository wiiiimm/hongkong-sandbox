"""Full changed-domain basic neighbour checks for private Folkland terrain."""
from pathlib import Path
import subprocess,numpy as np,json,sys,uuid
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-neighbours-v2-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-folkland-pair-candidate-foundations-v2-20261020';SCOPE=BASE/'government-xl-folkland-current-scope-v1-20261020';UID='landsd/264677:0'
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
 scope=dict(changedParentExtent=next(p for r in read(SCOPE/'scope.json')['rows']if r['uid']==UID for p in r['overlappingInstalledTerrain']if p['url']=='city/data/terrain/unnamed147996-private-v1.json')['extent'])
 candidate=read(CAP/'terrain-candidates.json')[0];positions=np.asarray(read(ROOT/candidate['path'])['nativeMesh']['position']).reshape(-1,3);packed=np.concatenate([positions,positions.astype('<f4').astype(float)]);lo=packed.min(0);hi=packed.max(0);bb=scope['changedParentExtent'];scope['changedParentExtent']=[min(bb[0],float(lo[0])),min(bb[1],float(lo[2])),max(bb[2],float(hi[0])),max(bb[3],float(hi[2]))]
 inventory=read(SCOPE/'complete-bounds.json.gz')['rows'];required=[r['uid']for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],scope['changedParentExtent'])];save(DOC/'actor-scope.json',dict(completeActorCount=len(inventory),changedParentExtent=scope['changedParentExtent'],requiredNativeUids=required));refs.append(HERE/'heritage_saved_native_bounds_binding_v1_20261014.py')
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
 inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for _,tile in byuid.values()};patches=read(CAP/'terrain-candidates.json');save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in entries)for b,_ in byuid.values()],patches=patches,candidateIds=[UID,'landsd/225387:0'],requiredNativeUids=required,inputHashes=inputs))
 subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 resolution_folder=BASE/'government-xl-park-avenue239350-native-regression-v1-20261018'
 resolution_receipt=read(resolution_folder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(resolution_receipt['jobId'],)).fetchone()==('complete',resolution_receipt)
 path=resolution_folder/'installed-dependency-resolution.json';expected=next(e['sha256']for e in resolution_receipt['evidenceRefs']if e['path']==str(path.relative_to(ROOT)));assert digest(path.read_bytes())==expected
 resolution=read(path);original=ROOT/resolution['installedReceipt']['path'];assert digest(original.read_bytes())==resolution['installedReceipt']['sha256']
 save(DOC/'installed-dependency-resolution.json',resolution);refs.extend([resolution_folder/'result.json',path,original])
 subprocess.run(['node',str(HERE/'park_avenue239350_native_neighbours_v1_20261018.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 native=read(DOC/'native-neighbour-checks.json')
 geometrypath=HERE/'local'/CAP.name/'runtime-geometry.json.gz';foundation=read(CAP/'summary.json')['rows'];save(DOC/'foundation.json',foundation)
 report=read(DOC/'neighbour-checks.json');summary=dict(uid=UID,neighbourForms=len(byuid),requiredNativeUids=required,nativeChecks=native['rows'],flagged=[dict(uid=x['uid'],reasons=x['reasons'],beforeGap=x['beforeGap'],afterGap=x['afterGap'])for x in report['rows']if x['reasons']],foundation=foundation,installationApproved=False);save(DOC/'summary.json',summary);print(dict(uid=UID,neighbourForms=len(byuid),requiredNativeActors=len(required),flagged=len(summary['flagged'])),flush=True)
 for p,h in {**pins,**report['inputHashes'],**native['inputHashes'],**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([geometrypath,HERE/'xl-final-script-pass.py',HERE/'check-neighbours.mjs',HERE/'park_avenue239350_native_neighbours_v1_20261018.mjs'])
 module('times_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'folkland-full-parent-neighbours-and-foundations',list(dict.fromkeys(refs)),dict(uids=[UID],summary=summary,installationApproved=False))
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists()
 scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']==UID)
 retained=next(p for p in scope['overlappingInstalledTerrain']if p['url']=='city/data/terrain/unnamed147996-private-v1.json')['parentNativeUids']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(set(['building:'+UID,'building:landsd/225387:0','terrain-patch:'+UID]+['building:'+u for u in retained])),batch=BATCH,ttl=3600);assert claim['ok']
 lease=claim['reservation'];path=HERE/'local'/BATCH/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

