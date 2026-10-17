"""Historical source-only CITIC finite-host union diagnostic, never acceptance.

Unlike the earlier single vertical coplanar host test, this accounts for all
independently rooted original host facets, including corners and horizontal
surfaces. The exact fixed .1 m band, every original face and all old failures
remain intact. This does not refresh or relabel historical physical evidence.
"""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-citic-eight-details-complete-orthogonal-host-union-diagnostic-v1-20261011'
DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-citic-current-original-complete-support-v1'
PROBE=BASE/'government-xl-terrain-recovery-citic-complete-original-current-probe-v1-20261010'
PRIOR=BASE/'xl-terrain-recovery-20261010-citic-complete-original-literal-back-facets-v1'
PARTS=[29,33,34,35,36,39,40,70]

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
 assert not DOC.exists()
 g=read(GRAPH/'diagnostic.json.gz');selection=read(PROBE/'selection.json.gz')
 assets=[ROOT/next(r for r in selection['rows']if r['uid']==a['uid'])['candidate']['path']for a in g['actors']]
 for a,p in zip(g['actors'],assets):
  row=next(r for r in selection['rows']if r['uid']==a['uid'])
  assert digest(p.read_bytes())==row['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets])
 assert original.shape==(14036,3,3) and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath)
 literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index'],np.uint32).reshape(-1,3)]for a in g['actors']])
 assert literal.shape==original.shape and np.isfinite(original).all() and np.isfinite(literal).all()
 for folder in [GRAPH,PROBE,PRIOR]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 prior=read(PRIOR/'diagnostic.json.gz')
 assert prior['originalWorldSHA256']==digest(original.tobytes()) and prior['literalWorldSHA256']==digest(literal.tobytes())
 rootids=np.array(sorted(i for k in g['resolvedOriginalComponents']for i in g['components'][k]['globalOriginalFaces']),int)
 assert len(rootids)==len(set(rootids)) and not set(rootids)&{i for k in PARTS for i in g['components'][k]['globalOriginalFaces']}
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',PROBE/'result.json',PRIOR/'diagnostic.json.gz',PRIOR/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'exact_original_surface_coordinate_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py']]
 rows=[]
 for mode,tri in [('untouched-provider-original',original),('captured-historical-runtime-literal',literal)]:
  for k in PARTS:
   ids=g['components'][k]['globalOriginalFaces'];proofs=[]
   # The helper performs its conservative broadphase against the full scope.
   # No manually selected nearest plane or host removes other valid surfaces.
   for i in ids:
    proof=verify(tri[i],tri[rootids])
    proofs.append(dict(globalOriginalFace=i,proof=proof))
   passing=[p['globalOriginalFace']for p in proofs if p['proof']['wholeFacetAssociated']]
   zero=[p['globalOriginalFace']for p in proofs if p['proof'].get('sourcePrimitiveDimensionLessThan2')]
   old=next(r for r in prior['rows']if r['component']==k and r['mode']==('untouched-provider-original'if mode.startswith('untouched')else'captured-actual-runtime-literal'))
   rows.append(dict(component=k,mode=mode,completeFaces=ids,allFacetProofs=proofs,passingFacetIds=passing,zeroAreaFacesRetainedWithoutCredit=zero,previousSingleVerticalCoplanarPassingFacets=old['passingFacetIds'],completeComponentAssociated=len(passing)==len(ids),roleAccepted=False,structuralRootCredit=False))
   print(dict(component=k,mode=mode,completeFaces=len(ids),newPassingFacets=len(passing),oldPassingFacets=len(old['passingFacetIds']),zeroAreaFaces=len(zero)),flush=True)
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(rows=rows,evidenceRefs=refs,completeSourceFaces=len(original),completeIndependentHostScope=rootids.tolist(),originalWorldSHA256=digest(original.tobytes()),literalWorldSHA256=digest(literal.tobytes()),historicalBaselineManifestSHA256=selection['manifestSHA256'],sourceOnlyHistoricalDiagnostic=True,allPriorNegativeEvidencePreserved=True,strictEuclideanBandM=.1,sourceGeometryChanges=0,aiGeometryModelling=False,visualRoleAccepted=False,nativeReacceptance=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('citic_union_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'eight-complete-original-detail-general-finite-host-union-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[a['uid']for a in g['actors']],sourceOnlyHistoricalDiagnostic=True,sourceGeometryChanges=0,aiGeometryModelling=False,visualRoleAccepted=False,nativeReacceptance=False,installationApproved=False,qualification='Distinct general finite-host union measure, preserving single vertical coplanar failures, all original faces and the unchanged .1m band. No current physical rebind, visual role, grounding or installation acceptance.'))

if __name__=='__main__':main()
