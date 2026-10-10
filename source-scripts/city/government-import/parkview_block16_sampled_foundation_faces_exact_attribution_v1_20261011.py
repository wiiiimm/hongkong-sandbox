"""DRAFT identify sampled-foundation failures then exact finite pair attribution.
All11351 existing vertex+centroid classifications rechecked unchanged; only4
implicated source facets receive complete current finite-column pair census.
No whole-source proof, terrain/removal proposal, support or acceptance credit.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from parkview_blocks7_16_retained_parent_cap_causality_v1_20261011 import matches
B=ROOT/'docs/astra-city/government-import';PHYSICAL=B/'government-xl-parkview-block16-fresh-current-physical-capture-v1-20261011';CARRIER=B/'government-xl-parkview-block16-fresh-current-carrier-capture-v1-20261011';GRAPH=B/'government-xl-parkview-block16-complete-original-support-graph-v1-20261011';ATTR=B/'government-xl-parkview-block16-complete-cap-retained-obligations-v1-20261011';DOC=B/'government-xl-parkview-block16-sampled-foundation-faces-exact-attribution-v1-20261011';PIN='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==PIN
 paths=[Path(__file__),PHYSICAL/'foundation.json',PHYSICAL/'current-raw-outcome.json',PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',CARRIER/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',ATTR/'diagnostic.json.gz',ATTR/'result.json',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'parkview_blocks7_16_retained_parent_cap_causality_v1_20261011.py']
 rtpath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';crpath=HERE/'local'/CARRIER.name/'runtime-geometry.json.gz';paths.extend([rtpath,crpath]);rt=read(rtpath)['rows'][0];tri=np.asarray(rt['position'],dtype='<f8').reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);carrier=np.asarray(read(crpath)['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 row=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];paths.append(asset);original=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(11351,3,3)and np.array_equal(tri,original);raw=read(PHYSICAL/'current-raw-outcome.json');assert raw['currentManifest']['sha256']==PIN and digest(ground.tobytes())==raw['completeCurrentDrawnGroundSHA256'];attr=read(ATTR/'diagnostic.json.gz');assert digest(carrier.tobytes())==attr['completeCurrentDrawnGroundSHA256'];graph=read(GRAPH/'diagnostic.json.gz');assert digest(original.tobytes())==graph['completeOriginalWorldSHA256']
 spec=importlib.util.spec_from_file_location('block16_exact_foundation_source',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final);form=row['source']['building'];rings=form['rings'];recheck=final.foundation_context(tri,ground,Polygon(rings[0],rings[1:]));assert recheck==read(PHYSICAL/'foundation.json')['rows'][0]['foundation']
 lo,hi=tri.min((0,1)),tri.max((0,1));mask=(ground[:,:,0].max(1)>=lo[0]-1)&(ground[:,:,0].min(1)<=hi[0]+1)&(ground[:,:,2].max(1)>=lo[2]-1)&(ground[:,:,2].min(1)<=hi[2]+1);native=ground[mask];polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;native,polys=native[valid],polys[valid];points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(polys)).reshape(-1,4);gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1)).tolist();assert len(ids)==recheck['fullyBuriedTriangles']==4
 rows=[];total=0
 for fid in ids:
  face=tri[fid];xz=ground[:,:,[0,2]];fxz=face[:,[0,2]];candidates=np.flatnonzero(np.all(xz.max(1)>=fxz.min(0),axis=1)&np.all(xz.min(1)<=fxz.max(0),axis=1)).tolist();total+=len(candidates);assert total<=256,'Bounded full pair census; no truncation';pairs=[]
  for gid in candidates:
   proof=verify(face,ground[gid]);carrierids=matches(carrier,ground[gid]);known=[r for r in attr['allCurrentCapPairAttributions']if r['originalGroundFace']in carrierids]
   pairs.append(dict(ownedDrawnGroundFace=gid,exactFiniteColumnPairProof=proof,exactWholeCarrierGroundFacetMatches=carrierids,priorCapGroundAttributionsVerbatim=known))
  bodyids=[i for i,fids in enumerate(graph['completeSourceEdgeBodyFaces'])if fid in fids];assert len(bodyids)==1
  rows.append(dict(originalSourceFace=fid,originalSourceFacetSHA256=digest(face.tobytes()),originalSourceBody=bodyids[0],existingVertexPlusCentroidGapSamples=gaps[fid].tolist(),completeClosedAABBCandidateGroundIDs=candidates,completeFinitePairProofs=pairs,negativeFinitePairs=sum(p['exactFiniteColumnPairProof']['exactClosedHorizontalProjectionsMeet']and F(p['exactFiniteColumnPairProof']['exactMinimumFiniteColumnGapM'])<0 for p in pairs)))
 refs=[ref(p)for p in paths];assert digest(manifest.read_bytes())==PIN
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',stableManifestSHA256=PIN,sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,retentionRemovalApproved=False,nativeReacceptance=False,existingFoundationDiagnosticVerbatim=recheck,completeExistingSampleClassificationFaces=11351,sampledFoundationFailureSourceFaceIDs=ids,completeFinitePairBudget=256,actualCompletePairCount=total,rows=rows,evidenceRefs=refs,qualification='Existing fullyBuried label is3vertices+centroid, not whole finite facet classification. Complete finite-column pairs establish these4 implicated facets only, not allsource clearance/coverage or any safe replacement. Provenance outside priorcap48 inventory remains unresolved.'))
 print(json.dumps(dict(implicatedSourceFaces=ids,finitePairs=total,bodies=[r['originalSourceBody']for r in rows],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
