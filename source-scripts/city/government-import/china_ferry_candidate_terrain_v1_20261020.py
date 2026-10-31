"""Stage original-source terrain against current parent; never publish or waive checks."""
import json, sys, uuid, subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-china-ferry-candidate-terrain-v1-20261020'
BASE=ROOT/'docs/astra-city/government-import'; DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-china-ferry-current-scope-v1-20261020'
GROUND=BASE/'government-xl-china-ferry-adjoining-ground-v1-20261020'
def owned():
 lease=read(LOCAL/'reservation.json'); assert reservations.owns(lease)
 pins={};refs=[HERE/'china_ferry_candidate_terrain_v1_20261020.py']
 for folder in [SCOPE,GROUND]:
  r=read(folder/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256']
   pins[e['path']]=e['sha256']
 for p,h in pins.items(): assert digest((ROOT/p).read_bytes())==h,p
 uid='landsd/285642:0';scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']==uid)
 assert not scope['overlappingInstalledTerrain']
 # Private construction is not neighbour acceptance: retain every affected actor.
 selection=BASE/'government-xl-china-ferry-current-foundations-v1-20261020/selection.json.gz'
 row=next(r for r in read(selection)['rows']if r['uid']==uid);refs.append(selection)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 builder=module('sheung_candidate_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 cells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],parent);assert cells==scope['baseReplacementCells']
 groundpath=HERE/'local'/GROUND.name/'285642:0-ground.json.gz';native=np.asarray(read(groundpath)['completeAdjoiningTerrain']);refs.append(groundpath)
 bb=builder.extent(cells,parent);lo=native[:,:,[0,2]].min(axis=1);hi=native[:,:,[0,2]].max(axis=1)
 native=native[(hi[:,0]>=bb[0])&(lo[:,0]<=bb[2])&(hi[:,1]>=bb[1])&(lo[:,1]<=bb[3])]
 print('nominated terrain triangles',len(native),flush=True)
 sources=read(GROUND/'acquisitions.json');result=dict(uids=[uid],installationApproved=False,sourceGeometryModified=False,scopeReceipt=read(SCOPE/'result.json')['jobId'],nominatedTerrainTriangles=len(native),touchingInstalledActors=len(scope['touchingBaseDomainNativeUids']),touchingInstalledUids=scope['touchingBaseDomainNativeUids'],fullPackedDomainAndNeighbourRegressionRequired=True)
 try:
  patch=builder.make_patch(dict(uids=[uid],cells=cells),parent,native,sources)
  save(LOCAL/'candidate-terrain.json',patch);refs.append(LOCAL/'candidate-terrain.json')
  result.update(candidateBuilt=True,terrainTriangles=len(patch['nativeMesh']['index'])//3,nextStep='Complete rendered-surface, boundary, owned-model and basic-neighbour acceptance before publication')
 except AssertionError as e:
  result.update(candidateBuilt=False,failedGuard=str(e),nextStep='Resolve the specific terrain constructor guard without changing government building geometry or acceptance thresholds')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins)
 save(DOC/'summary.json',result)
 module('sheung_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'china-ferry-current-parent-terrain-candidate',list(dict.fromkeys(refs)),result)
 print(result,flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
