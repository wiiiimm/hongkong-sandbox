"""Every original/literal detail facet against complete finite rooted facades.

Source-only diagnosis: a back mounting sheet may be part of a closed sign solid.
Every failed front/free facet remains recorded; no structural/visual approval.
"""
import importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-cullinan-west-complete-original-literal-detail-facets-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');selection=read(PROBE/'selection.json.gz');assets=[ROOT/next(r for r in selection['rows']if r['uid']==a['uid'])['candidate']['path']for a in g['actors']];original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath);literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index'],np.uint32).reshape(-1,3)]for a in g['actors']]);assert literal.shape==original.shape==(154603,3,3)
 receipt=read(GRAPH/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']];rows=[];rootids=np.array(sorted(i for k in g['resolvedOriginalComponents']for i in g['components'][k]['globalOriginalFaces']),int)
 for mode,tri in [('untouched-provider-original',original),('captured-actual-runtime-literal',literal)]:
  for k in [270,294,295]:
   ids=g['components'][k]['globalOriginalFaces'];piece=tri[ids];lo=np.nextafter(piece.min(axis=(0,1))-.1,-np.inf);hi=np.nextafter(piece.max(axis=(0,1))+.1,np.inf);near=rootids[np.all(tri[rootids].max(axis=1)>=lo,axis=1)&np.all(tri[rootids].min(axis=1)<=hi,axis=1)];proofs=[]
   for i in ids:
    normal=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);proof=verify(tri[i],tri[near])if len(near)and np.any(normal)else None;proofs.append(dict(face=i,normal=normal.tolist(),band=proof,fullFiniteFacetBandPassed=bool(proof and proof['verifiedWholeOriginalFacetFiniteFacadeBand'])))
   passing=[p['face']for p in proofs if p['fullFiniteFacetBandPassed']];rows.append(dict(component=k,mode=mode,completeFaces=ids,allFacetProofs=proofs,passingFacetIds=passing,completeRootedFiniteHostFaceScope=near.tolist(),visualRoleAccepted=False,groundRootCredit=False,structuralBridgeCredit=False));print(dict(mode=mode,component=k,allFaces=len(ids),passingFacets=len(passing),candidateRootedHosts=len(near)),flush=True)
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[a['uid']for a in g['actors']],sourceOnlyFrozenBaseline=True,manifestSHA256=selection['manifestSHA256'],originalWorldSHA256=digest(original.tobytes()),literalWorldSHA256=digest(literal.tobytes()),rows=rows,evidenceRefs=refs,sourceGeometryChanges=0,visualRoleAccepted=False,nativeReacceptance=False,installationApproved=False);save(DOC/'diagnostic.json.gz',result);sp=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f);f.freeze(BATCH,'complete-original-literal-three-source-detail-finite-back-facet-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnlyDiagnostic=True,sourceGeometryChanges=0,visualRoleAccepted=False,nativeReacceptance=False))
if __name__=='__main__':main()
