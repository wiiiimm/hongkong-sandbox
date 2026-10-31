"""Rebind existing exact podium roles to the complete original terrain candidate."""
from pathlib import Path
from fractions import Fraction
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-original-patch-roles-v1-20261017';DOC=BASE/BATCH
FULL=BASE/'government-xl-opus-assembly-original-patch-v1-20261017';ROLE=BASE/'government-xl-opus-podium-role-review-v1-20261017';LOCAL=BASE/'government-xl-opus-podium-local-roles-v1-20261017';CAP=BASE/'government-xl-opus-actual-render-attributes-v2-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'original_bound_facet_wall_context_v2_20261010.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [FULL,ROLE,LOCAL,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 old=consume(ROLE/'ROOT-SOURCE-REVIEW.json');roles=consume(LOCAL/'context.json');worlds=consume(WORLD/'world-triangles.json.gz');world=worlds['original'];uids=sorted(world);tri=np.concatenate([np.array(world[u]) for u in uids]);pod=np.array(world['landsd/248432:0']);assert digest(pod.tobytes())==old['worldSHA256'];assert all(np.array_equal(tri,np.concatenate([np.array(w[u]) for u in uids])) for w in worlds.values())
 finite=consume(FULL/'proofs.json.gz');assert digest(tri.tobytes())==finite['worldSHA256'];faces=finite['rows'];assert len(faces)==13557 and all(r['proof']['groundProjectionCovered'] for r in faces);bad=[r['sourceFace'] for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']];assert bad==old['rawStrictFailuresRetained']
 cap=consume(FULL/'drawn-patch.json.gz');ground=np.array(cap['position']).reshape(-1,3)[np.array(cap['index']).reshape(-1,3)];assert digest(ground.tobytes())==finite['groundSHA256']
 exposure=[]
 for i in old['wallFaces']:
  height=pod[i,:,1].max();proofs=[exposure_at_vertex(v,ground) for v in pod[i] if v[1]==height];positive=any(p and p['maximumObservedGapM']>0 for p in proofs);assert positive or i==610
  exposure.append(dict(face=i,exactHighestVertexExposure=proofs,positive=positive))
 assert next(x for x in exposure if x['face']==611)['positive']
 for row in roles['wallPaths']:
  path=row['pathToStrictClearRoof'];assert path and path[0]==row['sourceFace'];assert faces[path[-1]]['proof']['existingOrdinaryClearanceBoundProved']
 assert faces[618]['proof']['existingOrdinaryClearanceBoundProved'];assert old['exactHigherOriginalSurfaceCoverage']['exactProjectionCovered']
 source=consume(CAP/'input.json.gz');polygon=shapely.union_all([Polygon(r['building']['rings'][0],r['building']['rings'][1:]) for r in source['rows']]);helper=module('opus_original_assembly_foundation',HERE/'xl-final-script-pass.py');foundation=helper.foundation_context(tri,ground,polygon)
 review=dict(priorSourceRoleReview=old,sourceSHA256=old['sourceSHA256'],worldSHA256=finite['worldSHA256'],groundSHA256=finite['groundSHA256'],rawStrictFailuresRetained=bad,exactCurrentExposures=exposure,strictOrdinaryFaces=13557-len(bad),sourceRoleInterpretationAccepted=True,sourceGeometryChanges=0,terrainChanges=0,foundation=foundation,fullAcceptance=False,publicationApproved=False,qualification='Reuses only exact unchanged source topology and lower-skin interpretation. All 13557 current terrain coverage and finite clearance proofs recomputed; every ordinary strict face remains strict, all130 wall roof paths terminate at current strict faces, all129 direct exposures and wall611 continuation exposure rechecked. All131 raw flags remain. Complete support/identity/runtime acceptance is separate.')
 DOC.mkdir();save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs += [HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__)]
 result=module('opus_original_roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-assembly-current-terrain-role-rebind-v1',refs,dict(uids=uids,sourceRoleInterpretationAccepted=True,foundation=foundation,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],foundation=foundation),flush=True)
if __name__=='__main__':main()
