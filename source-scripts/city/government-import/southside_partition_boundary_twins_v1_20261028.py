"""Bind legacy-negative seam vertices to exact opposite-side original-face twins."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from collections import defaultdict
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-partition-boundary-twins-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PART='government-xl-southside-six-strip-partition-diagnostic-v1-20261028';SEAMS='government-xl-southside-partition-existing-seams-v1-20261028';LAYERS='government-xl-southside-all-layer-seam-proof-v1-20261028';UID='landsd/315025:0'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 for name in [PART,SEAMS,LAYERS]:
  _,bound=authenticate(BASE/name);pins.update(bound);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 part=take(BASE/PART/'summary.json');seams=take(BASE/SEAMS/'summary.json');layers=take(BASE/LAYERS/'summary.json');assert layers['allFiveBidirectionalLayerProofsPassed']and layers['legacyNegativeResultsPreserved'];assert not part['missingParentFaces']and not part['heightDriftViolations']and part['allNodeBudgetsPassed'];tables={}
 for strip in part['strips']:
  data=take(ROOT/strip['asset']['path']);node=take(HERE/'local'/SEAMS/('strip-'+str(strip['strip'])+'-unbound.json'));assert node['nativeMesh']['position']==data['position']and node['nativeMesh']['index']==data['index'];tri=np.asarray(data['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(data['index']).reshape(-1,3)];assert len(tri)==len(data['parentFaceIndices']);table=defaultdict(set)
  for face,parent in zip(tri,data['parentFaceIndices']):
   for point in face:table[tuple(point)].add(parent)
  tables[str(strip['strip'])]=table
 rows=[]
 for pair in seams['pairs']:
  for side in pair['sides']:
   assert side['finitePairConstructionPassed'];own=side['member'];mate=next(n for n in pair['pair']if n!=own)
   for failure in side['failures']:
    p=tuple(failure['position']);a=tables[own].get(p,set());b=tables[mate].get(p,set());shared=sorted(a&b);rows.append(dict(pair=pair['pair'],own=own,mate=mate,position=list(p),legacyReason=failure['reason'],exactOppositeRuntimeVertexPresent=bool(b),sameOriginalMasterFaceIDs=shared,exactSharedOriginalFaceTwin=bool(shared)))
 assert len(rows)==22;result=dict(uids=[UID],legacyNegativeVertices=len(rows),allLegacyNegativeVerticesHaveExactOppositeSourceFaceTwins=all(r['exactSharedOriginalFaceTwin']for r in rows),rows=rows,allLayerFiniteSeamProofPassed=True,productionGuardChanges=False,terrainValidatorPassed=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='No legacy rejection removed. Each rejected runtime vertex is checked for an identical Float32 3D vertex on the opposite strip and at least one identical original master-face provenance ID. Complete all-layer seam proof is separately hash-bound. This supports a future explicit partition-boundary contract; no adapter, publisher, terrain or model approval is changed.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_partition_vertex_twins_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-face-twins-for-all-preserved-legacy-seam-negatives',refs,result);print(dict(vertices=len(rows),allTwins=result['allLegacyNegativeVerticesHaveExactOppositeSourceFaceTwins']),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-exact-partition-boundary-twins-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
