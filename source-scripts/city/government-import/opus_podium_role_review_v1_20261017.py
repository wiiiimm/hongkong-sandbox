"""Scoped original podium wall/lower-skin interpretation; no publication approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import exact_coverage
BASE=ROOT/'docs/astra-city/government-import';LOCAL=BASE/'government-xl-opus-podium-local-roles-v1-20261017';EXPOSE=BASE/'government-xl-opus-podium-wall-exposure-v1-20261017';FINITE=BASE/'government-xl-opus-podium-finite-walls-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-podium-role-review-v1-20261017';DOC=BASE/BATCH;UID='landsd/248432:0';SHA='413249980adc12dffbe589ec5db87a66075682c71e134b0e21a74d228d85f72e'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_original_projection_coverage_v2_20261010.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [LOCAL,EXPOSE,FINITE]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 local=consume(LOCAL/'context.json');exposure=consume(EXPOSE/'contexts.json.gz');finite=consume(FINITE/'original.json.gz');worlds=consume(WORLD/'world-triangles.json.gz');tri=np.array(worlds['original'][UID]);assert len(tri)==967 and digest(tri.tobytes())==local['worldSHA256']==finite['worldSHA256'];assert all(np.array_equal(tri,w[UID]) for w in worlds.values())
 source=ROOT/'source-scripts/city/government-import/local/government-xl-seven-new-original-closures-20261008/assets'/ (SHA+'.glb.gz');assert digest(source.read_bytes())==SHA;refs.append(source)
 assert local['wallFaces']==local['wallsWithStrictClearRoofPath']==130 and not local['missingRoofPaths'];assert exposure['nonWallFailedFaces']==[dict(faceIndex=619,normalY=-1.,minimumGapM=exposure['nonWallFailedFaces'][0]['minimumGapM'])]
 walls=[x['sourceFace'] for x in local['wallPaths']];assert len(walls)==len(set(walls))==130
 failed=[r['sourceFace'] for r in finite['faces'] if not r['proof']['existingOrdinaryClearanceBoundProved']];assert sorted(walls+[619])==failed and all(r['proof']['groundProjectionCovered'] for r in finite['faces'])
 assert all(exposure['contexts'][i]['maximumObservedGapM']>0 for i in walls if i!=610)
 continuation=exposure['continuation']['rows'];assert len(continuation)==1 and continuation[0]['sourceFace']==610 and continuation[0]['exactConnectedCoplanarSheetFaces']==[610,611] and continuation[0]['exposedOriginalSheetFaces']==[611] and continuation[0]['hasActualAboveGroundExteriorContinuation']
 higher=[r['faceIndex'] for r in local['downwardFace']['higherOriginalFaces']];cover=exact_coverage(tri[619],tri[higher]);assert cover['exactProjectionCovered']
 assert all(tri[i,:,1].min()>tri[619,:,1].max() for i in higher)
 assert finite['faces'][618]['proof']['existingOrdinaryClearanceBoundProved'] and np.all(tri[618,:,1]==tri[619,0,1]);shared=set(map(tuple,tri[618]))&set(map(tuple,tri[619]));assert len(shared)==2 and len(set(shared))==2
 for p in [LOCAL/'source.png',LOCAL/'ground.png']:assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p)
 review=dict(reviewer='Codex ROOT',uid=UID,sourceSHA256=SHA,sourceRoleInterpretationAccepted=True,wallFaces=walls,lowerSkinFaces=[619],strictOrdinaryFaces=836,worldSHA256=local['worldSHA256'],groundSHA256=local['groundSHA256'],coordinateModes=list(worlds),rawStrictFailuresRetained=failed,rawStrictClearanceAccepted=False,exactHigherOriginalSurfaceCoverage=cover,originalHigherFaces=higher,downwardConnectionToStrictClearCoplanarFace=618,imagesActuallyViewed=[dict(path=str((LOCAL/n).relative_to(ROOT)),sha256=digest((LOCAL/n).read_bytes())) for n in ['source.png','ground.png']],basis='All 130 source-authored walls have exact shared-edge paths to strictly clear upward original surfaces. 129 have exact exposed-vertex witnesses; wall610 continues in the exact same plane through shared-edge wall611 with positive exposure. Original downward face619 connects to strictly clear coplanar face618 and its whole projection is covered exactly by wholly higher upward faces of the same unchanged source. Source-only and prepared-terrain exports were inspected from opposite oblique directions. Face619 is interpreted narrowly as a lower source skin, not an exposed upward deck.',qualification='Only these exact original faces and saved terrain/world hashes. This is source-role interpretation, not engineering certification, complete support, current foreign-neighbour acceptance, browser acceptance or publication permission. Every raw finite failure remains. No general wall or underside exemption.',sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,publicationApproved=False,newlyInstalled=0)
 DOC.mkdir();save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 out=module('opus_role_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-source-specific-wall-and-lower-skin-review-v1',refs,dict(uids=[UID],sourceRoleInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],sourceRoleInterpretationAccepted=True),flush=True)
if __name__=='__main__':main()
