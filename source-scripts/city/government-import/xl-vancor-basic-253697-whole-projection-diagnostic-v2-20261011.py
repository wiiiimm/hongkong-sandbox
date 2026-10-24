"""Full actual BASIC253697 projection versus complete original Vancor and terrain.

Read-only diagnostic. No footprint proxies, actor suppression, old-gap waiver,
absent original podium support, terrain mutation or acceptance credit.
"""
import importlib.util,subprocess,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from whole_source_disjoint_literal_parent_facets_20261010 import finite_projection,form_polygon
from native_parent_child_flat_composition_20261010 import faces
BATCH='government-xl-vancor-basic-253697-whole-projection-diagnostic-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011'
PHYSICAL=DOC.parent/'government-xl-vancor-authentic-tin-retained-pak-shing-current-physical-v1-20261011'
LOCAL=HERE/'local'/PHYSICAL.name
UID='landsd/147956:0';BASIC='landsd/253697:0';MANIFEST='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def geom(p):return json.loads(shapely.to_geojson(p))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 inputs=read(INPUT/'result.json');prior=read(PHYSICAL/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [inputs,prior]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in [INPUT/'check-selection.json.gz',INPUT/'proposal-input.json',INPUT/'complete-proposed-region-current-forms.json.gz']:assert ref(p)in inputs['evidenceRefs']
 selection=read(INPUT/'check-selection.json.gz');row=selection['rows'][0];assert row['uid']==UID
 proposal=read(INPUT/'proposal-input.json');parentpath=ROOT/proposal['retainedParent']['path'];assert ref(parentpath)==proposal['retainedParent']
 candidatepath=LOCAL/'government-native-147956-0.json';assert ref(candidatepath)in prior['evidenceRefs']
 neighbourpath=PHYSICAL/'neighbour-checks.json';assert ref(neighbourpath)in prior['evidenceRefs'];neighbours=read(neighbourpath);failed=[r for r in neighbours['rows']if r['reasons']];assert len(failed)==1 and failed[0]['uid']==BASIC
 DOC.mkdir(parents=True);subprocess.run(['node',str(HERE/'xl-vancor-current-basic-253697-geometry-v2-20261011.mjs')],cwd=ROOT,check=True)
 capture=read(DOC/'complete-current-basic-geometry.json.gz');actor=capture['actor'];assert actor['uid']==BASIC
 pos=np.asarray(actor['completePosition'],dtype='<f8').reshape(-1,3);idx=np.asarray(actor['completeIndex'],int).reshape(-1,3);basic=pos[idx]
 assert len(basic)==actor['completeFaces']and np.isfinite(basic).all()
 sourcepath=ROOT/row['candidate']['path'];raw=sourcepath.read_bytes();assert digest(raw)==row['sourceSHA256'];source=decode_original_world_triangles(raw);assert len(source)==669
 parent=read(parentpath);candidate=read(candidatepath);old=faces(parent);new=faces(candidate)
 ownprojection=finite_projection(source);basicprojection=finite_projection(basic);rings=form_polygon(actor['currentForm']['rings']);intersection=basicprojection.intersection(ownprojection)
 oldproj=[finite_projection(np.asarray([t]))for t in old];tree=shapely.STRtree(oldproj);selected=sorted(map(int,tree.query(basicprojection,predicate='intersects')));region=shapely.union_all([oldproj[i]for i in selected]);unsafe=[i for i in selected if oldproj[i].intersects(ownprojection)]
 below={'oldCurrentParent':old,'VancorCandidate':new};terrain=[]
 for label,tri in below.items():
  triProjection=[finite_projection(np.asarray([t]))for t in tri];tt=shapely.STRtree(triProjection);ids=sorted(map(int,tt.query(basicprojection,predicate='intersects')))
  terrain.append(dict(label=label,completeFaces=len(tri),completeActualFloat32TriangleSHA256=digest(tri.astype('<f8').tobytes()),allWholeFacetsIntersectingCompleteBasicProjection=ids,allWholeFacetVertices=tri[ids].tolist(),wholeBasicProjectionUncoveredGeoJSON=geom(basicprojection.difference(shapely.union_all([triProjection[i]for i in ids])))))
 out=dict(uid=UID,currentBasicUID=BASIC,currentBasicCSUID=actor['currentForm']['buildingCSUID'],completeOriginalSourceFaces=len(source),completeOriginalSourceWorldSHA256=digest(source.astype('<f8').tobytes()),completeOriginalWorldTriangles=source.tolist(),completeCurrentBasicFaces=len(basic),completeCurrentBasicWorldTriangles=basic.tolist(),completeCurrentBasicWorldSHA256=digest(basic.tobytes()),completeCurrentBasicBounds=[pos.min(0).tolist(),pos.max(0).tolist()],completeSourceBounds=[source.min((0,1)).tolist(),source.max((0,1)).tolist()],completeCurrentBasicProjectionGeoJSON=geom(basicprojection),currentFormFootprintGeoJSON=geom(rings),actualBasicProjectionOutsideCurrentFormM2=basicprojection.difference(rings).area,fullSourceProjectionGeoJSON=geom(ownprojection),fullSourceBasicProjectionIntersectionGeoJSON=geom(intersection),fullSourceBasicProjectionIntersectionM2=intersection.area,completeProjectedMeshesDisjoint=not basicprojection.intersects(ownprojection),minimumProjectedDistanceM=basicprojection.distance(ownprojection),allOriginalParentFacetsMeetingActualBasicProjection=selected,originalParentSelectedRegionGeoJSON=geom(region),originalParentSelectedRegionSourceIntersectionM2=region.intersection(ownprojection).area,selectedOriginalParentFacetsNotSourceDisjoint=unsafe,literalWholeParentDisjointRetentionAdmissible=not unsafe and not basicprojection.intersects(ownprojection),terrain=terrain,rawSoleNeighbourFailure=failed[0],currentManifest=start,evidenceRefs=[ref(sourcepath),ref(parentpath),ref(candidatepath),ref(neighbourpath),ref(INPUT/'result.json'),ref(PHYSICAL/'result.json'),ref(DOC/'complete-current-basic-geometry.json.gz')],sourceGeometryChanges=0,terrainGeometryChanges=0,currentRootOrSupportAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Every actual current BASIC face/full vertex attribute and complete original source face is retained. Whole literal parent-facet retention requires strict complete-projection disjointness; genuine intersections are negative evidence, not footprint proxy or absent-podium support credit.')
 save(DOC/'diagnostic.json.gz',out)
 assert ref(manifest)==start
 refs=[Path(__file__),HERE/'xl-vancor-current-basic-253697-geometry-v2-20261011.mjs',HERE/'exact_packed_world_geometry_20261009.py',HERE/'whole_source_disjoint_literal_parent_facets_20261010.py',HERE/'native_parent_child_flat_composition_20261010.py',*[ROOT/p for p in capture['inputHashes']],*[ROOT/r['path']for r in out['evidenceRefs']]]
 spec=importlib.util.spec_from_file_location('vancor_basic_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'full-current-basic253697-original-vancor-parent-projection-diagnostic-v2',refs,dict(uids=[UID,BASIC],fullSourceBasicProjectionIntersectionM2=intersection.area,wholeLiteralParentDisjointRetentionAdmissible=out['literalWholeParentDisjointRetentionAdmissible'],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(basicFaces=len(basic),sourceBasicOverlapM2=intersection.area,unsafeWholeParentFaces=len(unsafe),retentionAdmissible=out['literalWholeParentDisjointRetentionAdmissible'])))
if __name__=='__main__':main()
