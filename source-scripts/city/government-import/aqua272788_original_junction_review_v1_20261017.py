"""Exact-source role review of two near-coincident original tower/podium side skins."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua272788-original-junction-review-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-aqua272788-junction-role-views-v1-20261017','government-xl-aqua272788-facet32-subdivision-v2-20261017','government-xl-aqua272788-complete-conflict-facets-v1-20261017','government-xl-aqua272788-current-physical-v2-20261017']
T='landsd/272788:0';P='landsd/193086:0';SHA='dba1c8804136ce3c086cef7f6a7ac013b3b15eb17648160e9ffb899442872da5';HOST='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:pins.setdefault(e['path'],set()).add(e['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 views=consume(BASE/NAMES[0]/'role-context.json.gz');tree=consume(BASE/NAMES[1]/'proof-tree.json.gz');full=consume(BASE/NAMES[2]/'association.json.gz');assert tree['complete'] and next(x for x in full['rows']if x['sourceFace']==1836)['wholeFacetAssociated']
 physical=BASE/NAMES[3];f=consume(physical/'foundation.json')['rows'][0];terrain=consume(physical/'terrain-only-foundation.json');support=consume(physical/'support-checks.json.gz')['rows'][0];assert f['sourceSHA256']==SHA and f['foundation']['fullyBuriedTriangles']==2 and f['foundation']['fullyBuriedUpwardTriangles']==0;assert terrain['fullyBuriedTriangles']==0 and terrain['completeTerrainTriangles']==11045;assert support['sourceSHA256']==SHA and support['supportSHA256']==HOST and support['interface']['strictContacts']==support['interface']['samples']==340 and support['interface']['passed']
 runtime=consume(HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz');tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in runtime['rows']}
 def normal(t):
  v=np.cross(t[1]-t[0],t[2]-t[0]);return v/np.linalg.norm(v)
 rows=[]
 for face in [32,1836]:
  proofs=[(n['orthogonalProof'],n['edgeProof'])for n in tree['nodes']if not n.get('children')]if face==32 else [(x['orthogonalProof'],x['finiteEdgeProof'])for x in full['rows']if x['sourceFace']==face]
  ids=set()
  for o,e in proofs:
   assert o['wholeFacetAssociated']or (e and e['wholeFacetFiniteEdgeUnionAssociated'])
   ids.update(x['originalHostFace']for x in o.get('completeExactFootRegionRecords',[]))
   if e:ids.update(x['originalHostFace']for x in e['allCompleteRegionCertificates'])
  sn=normal(tri[T][face]);hosts=[dict(face=i,normal=normal(tri[P][i]).tolist(),normalDotSource=float(np.dot(sn,normal(tri[P][i]))))for i in sorted(ids)];assert abs(sn[1])<.25 and hosts and all(abs(x['normal'][1])<.25 for x in hosts)
  rows.append(dict(sourceFace=face,sourceVertices=tri[T][face].tolist(),sourceNormal=sn.tolist(),completeSourceFacetWithinExistingPointOneMetreBand=True,nearbyFiniteHostSideFaces=hosts))
 image=BASE/NAMES[0]/'junction-orthographic.png';assert digest(image.read_bytes())in pins[str(image.relative_to(ROOT))];refs.append(image)
 review=dict(reviewer='Codex ROOT',sourceSHA256ByUid={T:SHA,P:HOST},literalSourceWorldSHA256=digest(tri[T].tobytes()),literalHostWorldSHA256=digest(tri[P].tobytes()),sourceRoleInterpretationAccepted=True,sourceRole='Two near-coincident source-authored side-wall skins at the original tower/podium junction',sourceSpecificFaces=[32,1836],rows=rows,rawWholeSourceFoundation=f,rawWarningsRetained=True,terrainOnlyFoundation=terrain,strictSupportContacts=340,imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],basis='Both narrow facets are connected to the main tower source and align along adjacent original podium side skins in all three orthographic views. Complete finite-facet coverage proves every point is within the existing0.1m host band, not merely its perimeter. All contributing finite-host facets are near vertical. The height-envelope test compares these side skins to higher podium surfaces, producing the retained buried-face flags; neither flagged face is an upward exposed floor. The tower itself clears terrain and all340 canonical rim contacts meet the exact original podium.',qualification='Interpretation applies only to these exact two source faces and captured literal source/host worlds. This is not a generic wall exemption or standalone foundation acceptance. Original/four runtime coordinate modes, complete current source and neighbour checks, support installation binding, browser verification and guarded publication remain required.',sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,publicationApproved=False)
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 out=module('aqua_junction_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-exact-original-side-junction-role-review-v1',refs,dict(uids=[T],sourceRoleInterpretationAccepted=True,sourceFaces=[32,1836],fullAcceptance=False,nextStep='Bind this exact-source interpretation to all original/runtime coordinate modes and complete current physical/browser evidence before qualification.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
