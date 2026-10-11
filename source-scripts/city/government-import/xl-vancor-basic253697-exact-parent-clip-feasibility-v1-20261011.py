"""Source/current-bound exact parent clipping feasibility, never a terrain candidate."""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from native_parent_child_flat_composition_20261010 import faces
from whole_source_disjoint_literal_parent_facets_20261010 import finite_projection
from exact_current_parent_finite_region_clip_feasibility_20261011 import diagnose
BATCH='government-xl-vancor-basic253697-exact-parent-clip-feasibility-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-vancor-basic-253697-whole-projection-diagnostic-v1-20261011'
MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipt=read(INPUT/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for name in ['diagnostic.json.gz','complete-current-basic-geometry.json.gz']:assert ref(INPUT/name)in receipt['evidenceRefs']
 frozen=read(INPUT/'diagnostic.json.gz');assert frozen['completeProjectedMeshesDisjoint']and not frozen['literalWholeParentDisjointRetentionAdmissible'];assert frozen['selectedOriginalParentFacetsNotSourceDisjoint']==[1169,1170,2114,2115,2116,2302,2533]
 capture=read(INPUT/'complete-current-basic-geometry.json.gz')
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 parent=ROOT/'3d-viewer/city/data/government-native-186864-0.json';assert ref(parent)in frozen['evidenceRefs'];terrain=faces(read(parent));source=np.asarray(frozen['completeOriginalWorldTriangles'],dtype='<f8');projection=finite_projection(source);actual=shapely.from_geojson(json.dumps(frozen['completeCurrentBasicProjectionGeoJSON']));form=shapely.from_geojson(json.dumps(frozen['currentFormFootprintGeoJSON']))
 regions=[('complete-actual-basic-projection',actual),('explicit-current-basic-and-guard-footprint-one-centimetre-envelope',actual.union(form).buffer(.01,join_style='mitre'))];rows=[]
 for name,region in regions:
  assert region.geom_type=='Polygon'and region.is_valid and not region.intersects(projection)
  triangulation=[list(t.exterior.coords)[:3]for t in shapely.get_parts(shapely.constrained_delaunay_triangles(region))];rings=[list(region.exterior.coords),*[list(r.coords)for r in region.interiors]]
  proof=diagnose(terrain,rings,triangulation);packed=np.asarray(proof['packedClippedFacets'],dtype=float);coverage=finite_projection(packed);difference=region.difference(coverage)
  rows.append(dict(region=name,completeRegionGeoJSON=json.loads(shapely.to_geojson(region)),wholeSourceProjectionMinimumDistanceM=region.distance(projection),exactClipFeasibility=proof,actualPackedProjectionSourceIntersectionM2=coverage.intersection(projection).area,actualPackedProjectionStrictSourceDisjoint=not coverage.intersects(projection),actualPackedRegionMissingAreaM2=difference.area,actualPackedRegionMissingGeoJSON=json.loads(shapely.to_geojson(difference)),newTerrainCandidateCreated=False,physicalAccepted=False))
 out=dict(rows=rows,currentManifest=start,rawPriorNeighbourFailure=frozen['rawSoleNeighbourFailure'],rawSevenWholeFacetRetentionFailure=frozen['selectedOriginalParentFacetsNotSourceDisjoint'],currentSourceFaces=len(source),parentFacets=len(terrain),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Read-only exact rational parent clipping feasibility with explicit actual Float32 plane and domain failures. The one-centimetre diagnostic envelope is declared and fully source-disjoint; no surface/seam equivalence, numeric tolerance waiver, candidate or support credit is inferred.')
 save(DOC/'diagnostic.json.gz',out);assert ref(manifest)==start
 refs=[Path(__file__),INPUT/'result.json',INPUT/'diagnostic.json.gz',INPUT/'complete-current-basic-geometry.json.gz',parent,*[ROOT/p for p in capture['inputHashes']],HERE/'exact_current_parent_finite_region_clip_feasibility_20261011.py',HERE/'test_exact_current_parent_finite_region_clip_feasibility_20261011.py',HERE/'actual_native_parent_transition_v3_20261010.py',HERE/'exact_original_polygon_triangle_partition_20261010.py',HERE/'native_parent_child_flat_composition_20261010.py',HERE/'whole_source_disjoint_literal_parent_facets_20261010.py']
 spec=importlib.util.spec_from_file_location('vancor_clip_feasibility_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'exact-parent-current-basic-finite-clipping-f32-plane-domain-feasibility-no-candidate-v1',refs,dict(uids=['landsd/147956:0','landsd/253697:0'],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,newlyInstalled=0,actualPackedPlaneFailureCounts={r['region']:len(r['exactClipFeasibility']['actualFloat32PlaneFailures'])for r in rows}))
 print(json.dumps([dict(region=r['region'],facets=len(r['exactClipFeasibility']['packedClippedFacets']),planeFailures=len(r['exactClipFeasibility']['actualFloat32PlaneFailures']),domainGapM2=r['actualPackedRegionMissingAreaM2'],strictSourceDisjoint=r['actualPackedProjectionStrictSourceDisjoint'])for r in rows]))
if __name__=='__main__':main()
