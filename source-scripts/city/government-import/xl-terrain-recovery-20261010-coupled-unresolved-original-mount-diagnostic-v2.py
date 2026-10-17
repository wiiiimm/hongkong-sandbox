"""Diagnose complete original unresolved details against strictly rooted source hosts.

No visual/structural acceptance. All original component and host faces retained.
"""
import argparse,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_local_perpendicular_boundary_diagnostic_20261010 import prepare_hosts,diagnose
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as facet_band

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--support',required=True);p.add_argument('--component',required=True,type=int,action='append');p.add_argument('--batch',required=True);a=p.parse_args()
 physical=ROOT/a.physical;support=ROOT/a.support;doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists()
 graph=read(support/'diagnostic.json.gz');receipt=read(support/'result.json')
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 selection=read(physical/'selection.json.gz');tri=[];assets=[]
 for row,actor in zip(selection['rows'],graph['actors']):
  assert row['uid']==actor['uid'] and row['sourceSHA256']==actor['sourceSHA256']
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];piece=decode_original_world_triangles(raw);assert len(piece)==actor['completeOriginalFaceCount'] and digest(piece.tobytes())==actor['originalWorldTrianglesSHA256'];tri.append(piece);assets.append(asset)
 tri=np.concatenate(tri);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 unresolved=set(range(len(graph['components'])))-set(graph['resolvedOriginalComponents']);assert set(a.component)<=unresolved
 hosts=sorted(i for k in graph['resolvedOriginalComponents'] for i in graph['components'][k]['globalOriginalFaces']);prepared=prepare_hosts(tri,hosts);results=[]
 for k in a.component:
  ids=graph['components'][k]['globalOriginalFaces'];print(json.dumps(dict(component=k,faces=len(ids),phase='complete-boundary-and-facet-diagnosis')),flush=True)
  boundary=diagnose(prepared,ids);facets=[dict(globalSourceFace=i,proof=facet_band(tri[i],tri[hosts])) for i in ids]
  results.append(dict(component=k,completeComponent=graph['components'][k],completeSourceTriangles=tri[ids].tolist(),completeOriginalBoundaryDiagnostic=boundary,everyCompleteOriginalFacetFiniteHostDiagnostic=facets))
 refs=[ref(p) for p in [Path(__file__),physical/'selection.json.gz',support/'diagnostic.json.gz',support/'result.json',*assets,HERE/'original_local_perpendicular_boundary_diagnostic_20261010.py',HERE/'test_exact_original_perpendicular_edge_facet_band_20261010.py',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'test_exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'exact_original_perpendicular_edge_facet_band_20261010.py']]
 result=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeOriginalFaces=len(tri),completeRootedHostFaces=hosts,rows=results,sourceOnlyDiagnostic=True,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,fullAcceptance=False,sourceGeometryChanges=0,evidenceRefs=refs);save(doc/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 summary=dict(uids=[r['uid'] for r in selection['rows']],completeOriginalFaces=len(tri),components=[dict(component=r['component'],completeBoundaryBandPassed=r['completeOriginalBoundaryDiagnostic']['sourceOnlyBoundaryBandPassed'],boundaryReasons=r['completeOriginalBoundaryDiagnostic']['reasons'],wholeFacetBandPassedFaces=[r['globalSourceFace'] for r in r['everyCompleteOriginalFacetFiniteHostDiagnostic'] if r['proof']['verifiedWholeOriginalFacetFiniteFacadeBand']]) for r in results],fullAcceptance=False,sourceGeometryChanges=0)
 m.freeze(a.batch,'complete-original-unresolved-detail-finite-mount-diagnostic-v1',[ROOT/r['path'] for r in refs],json.loads(json.dumps(summary,allow_nan=False)));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
