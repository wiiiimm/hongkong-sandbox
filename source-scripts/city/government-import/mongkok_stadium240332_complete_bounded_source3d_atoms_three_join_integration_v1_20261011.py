"""DRAFT source3D atoms + three generated nominations; no terrain mesh/current credit."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import importlib.util,json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,decoded,encoded
from exact_original_3d_directed_edge_atom_census_v1_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,cross,sub
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points,dimension
from exact_original_component_contacts_20261009 import contact_measure
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-complete-bounded-source3d-atoms-three-join-integration-v1-20261011';DOC=B/NAME;LOCAL=HERE/'local'/NAME;METHOD=B/(NAME+'-method')/'METHOD.md';PREFIX='government-xl-mongkok-stadium240332-';OLD=B/(PREFIX+'actual-native-union-authentic-core-inventory-v2-20261011');FRINGE=B/(PREFIX+'adjacent15c-complete-fringe-coverage-crosssheet-seams-v1-20261011');GRAPH=B/(PREFIX+'original14d-whole3d494-component-context-v1-20261011');JOIN=B/(PREFIX+'three-original-crosssheet-3d-join-feasibility-v1-20261011')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(folder):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 return r
def embedded(face):return tuple((p[0],F(0),p[2])for p in face)
def main():
 assert not DOC.exists();folders=[OLD,FRINGE,GRAPH,JOIN];receipts=[verify(p)for p in folders];o_file=HERE/'local'/OLD.name/'actual-union-authentic-whole-source-facets.json.gz';n_file=HERE/'local'/FRINGE.name/'complete-original15c-sheet-world.json.gz';o,n=read(o_file),read(n_file);fr=decoded(read(FRINGE/'diagnostic.json.gz'));gr=decoded(read(GRAPH/'diagnostic.json.gz'));jr=decoded(read(JOIN/'diagnostic.json.gz'));tin=next(ROOT/r['path']for r in o['sourceFiles']if r['path'].endswith('.gltf'));spec=importlib.util.spec_from_file_location('source3d_unchanged14d',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=LOCAL;old=decoder.terrain_triangles(tin);new=np.asarray(n['allWholeOriginalSheetFacets'],dtype='<f8');assert old.shape==(109339,3,3)and new.shape==(48930,3,3)and np.isfinite(old).all()and np.isfinite(new).all();assert digest(old.tobytes())==o['completeOriginalSheetSHA256']==gr['completeOriginalWorldSHA256']and digest(new.tobytes())==n['completeOriginalSheetWorldSHA256'];ids=[('14D',i)for i in o['completeSelectedOriginalSheetFacetIds']]+[('15C',i)for i in fr['allSelectedWholeOriginal15cFacetIds']];assert len(ids)==14554+244;worlds={'14D':old,'15C':new};base=np.asarray([worlds[s][i]for s,i in ids],dtype='<f8');source_faces=[rational_face(t)for t in base];projections=[embedded(f)for f in source_faces];core=CompleteGround(np.asarray(projections,dtype='<f8'));closure=[];zero_ids=[];rf={}
 # Reuse complete exact original14D plane-category census to avoid retesting
 # its100322-piece component proven to have ZERO vertical primitives.
 old_candidates=sorted({i for r in gr['completeWholeNonzeroExactEdgeComponents']if r['exactPlaneOrientations'].get('vertical',0)for i in r['allOriginalFacetIds']}|{r['originalFacet']for r in gr['allExactZeroOriginalPrimitives']});candidate_ids={'14D':old_candidates,'15C':list(range(48930))}
 for sheet,targets in candidate_ids.items():
  for i in targets:
   face=rational_face(worlds[sheet][i]);normal=cross(sub(face[1],face[0]),sub(face[2],face[0]))
   if normal[1]!=0:continue
   zero_ids.append((sheet,i));projected=embedded(face);selected,proof=core.select(projected);hits=[]
   for j0 in selected:
    j=int(j0);pts=finite_intersection_points(projected,projections[j])
    if pts:hits.append(dict(coreOriginalFace=list(ids[j]),exactClosedProjectedIntersectionPoints=sorted(pts)))
   closure.append(dict(originalSourceFacet=[sheet,i],exact3DPrimitiveDimension=dimension(face),exactProjectedPrimitiveDimension=dimension(projected),selection=proof,allClosedFiniteCoreContactProofs=hits,retainCompleteOriginalFacet=bool(hits)))
   if hits and(sheet,i)not in ids:ids.append((sheet,i));source_faces.append(face)
  print(json.dumps(dict(completedZeroProjectionInventorySheet=sheet,sourceFacesRetained=len(source_faces))),flush=True)
 original_count=len(source_faces);originals=np.asarray([[list(map(float,p))for p in f]for f in source_faces],dtype='<f8');assert all(rational_face(t)==f for t,f in zip(originals,source_faces));nominees=[];join_binding=[]
 for k,r in enumerate(jr['allThreeExactSourceBoundaryJoinNominations']):
  for tri in r['allPositiveGeneratedJoinFaces']:nominees.append(tuple(tuple(p)for p in tri));join_binding.append(k)
 assert len(nominees)==3 and all(dimension(f)==2 for f in nominees);code=['exact_original_3d_directed_edge_atom_census_v1_20261011.py','test_exact_original_3d_directed_edge_atom_census_v1_20261011.py','exact_resumable_projected_inventory_v1_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_closed_ground_aabb_pruning_v1_20261011.py','test_exact_closed_ground_aabb_pruning_v1_20261011.py','science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py','test_science_museum_contact_relative_interior_v1_20261011.py','xl-second-pass.py'];refs=[ref(p)for p in[Path(__file__),METHOD,o_file,n_file]+[HERE/x for x in code]]+[ref(p/f)for p in folders for f in['result.json','diagnostic.json.gz']]+o['sourceFiles']+n['sourceFiles'];bindings=list({(r['path'],r['sha256']):r for r in refs}.values())
 def fence():assert all(ref(ROOT/r['path'])==r for r in bindings)
 cp=Checkpoints(LOCAL/'original-source-3d-atomic-checkpoints',source_faces,bindings,fence);original_atoms=census(source_faces,cp);cp=Checkpoints(LOCAL/'nominee-source-3d-integration-checkpoints',source_faces+nominees,bindings,fence);raw=census(source_faces+nominees,cp);orientation=[];oriented=list(nominees)
 for strip in range(3):
  faces_for_strip={original_count+i for i,k in enumerate(join_binding)if k==strip};mixed=[r for r in raw['allExact3DAtomicEdges']if any(e['face']in faces_for_strip for e in r['allDirectedIncidences'])and any(e['face']<original_count for e in r['allDirectedIncidences'])];proper=all(r['incidenceCount']==2 and sum(e['face']in faces_for_strip for e in r['allDirectedIncidences'])==1 for r in mixed);directions=[r['exactOpposedTwoIncidences']for r in mixed];reverse=bool(mixed and proper and not any(directions));consistent=bool(mixed and proper and(all(directions)or not any(directions)));orientation.append(dict(joinStrip=strip,allMixedSourceGeneratedAtoms=mixed,wholeGeneratedStripCanHaveOpposedSourceWinding=consistent,reverseGeneratedFacesOnly=reverse,sourceNormalOrWindingChanges=0))
  if reverse:
   for i,k in enumerate(join_binding):
    if k==strip:oriented[i]=tuple(reversed(oriented[i]))
 cp=Checkpoints(LOCAL/'oriented-source-3d-integration-checkpoints',source_faces+oriented,bindings,fence);integrated=census(source_faces+oriented,cp);ground=CompleteGround(originals);contacts=[];selections=[]
 for i,face in enumerate(oriented):
  selected,proof=ground.select(face);selections.append(proof);allowed_originals={('14D',jr['allThreeExactSourceBoundaryJoinNominations'][join_binding[i]]['originalBoundaryProof']['original14dFacetId']),('15C',jr['allThreeExactSourceBoundaryJoinNominations'][join_binding[i]]['originalBoundaryProof']['original15cFacetId'])}
  for j0 in selected:
   j=int(j0);pts=sorted(finite_intersection_points(face,source_faces[j]))
   if not pts:continue
   measure=contact_measure(pts);mid=tuple(sum(p[k]for p in pts)/len(pts)for k in range(3));contacts.append(dict(generatedNominee=i,originalSourceFacet=list(ids[j]),exactFiniteIntersectionPoints=pts,properBothRelativeInteriorCrossing=measure['dimension']>0 and relative_interior(face,mid)and dimension(source_faces[j])==2 and relative_interior(source_faces[j],mid),explicitNominatedSourceFacet=ids[j]in allowed_originals,positiveContactWithUnnominatedOriginal=measure['dimension']>0 and ids[j]not in allowed_originals,**measure))
 generated_atoms=[r for r in integrated['allExact3DAtomicEdges']if any(e['face']>=original_count for e in r['allDirectedIncidences'])];summary=dict(completeSelectedPositiveOriginalFaces=14798,completeRetainedSourceFaces=original_count,completeAllZeroProjectedOriginalPrimitives=len(zero_ids),zeroProjectedOriginalsRetained=sum(r['retainCompleteOriginalFacet']for r in closure),generatedNominations=3,source3DNonmanifoldAtoms=len(original_atoms['allNonmanifoldAtomIds']),source3DSameDirectionAtoms=len(original_atoms['allTwoSameDirectionAtomIds']),generatedMixedWindingIncompatibleStrips=sum(not r['wholeGeneratedStripCanHaveOpposedSourceWinding']for r in orientation),generatedNonmanifoldAtoms=sum(r['incidenceCount']>2 for r in generated_atoms),generatedSameDirectionAtoms=sum(r['incidenceCount']==2 and not r['exactOpposedTwoIncidences']for r in generated_atoms),generatedOpenBoundaryAtoms=sum(r['incidenceCount']==1 for r in generated_atoms),generatedProperOriginalSurfaceCrossings=sum(r['properBothRelativeInteriorCrossing']for r in contacts),generatedPositiveUnnominatedSourceContacts=sum(r['positiveContactWithUnnominatedOriginal']for r in contacts));fence();assert all(verify(p)==r for p,r in zip(folders,receipts));refs=bindings+[ref(p)for p in LOCAL.rglob('*')if p.is_file()and not p.name.endswith('.tmp')];save(DOC/'diagnostic.json.gz',encoded(dict(uids=['landsd/240332:0','landsd/240527:0'],sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,meshFilesCreated=False,sourcePositionOrWindingChanges=0,liveTerrainChanges=0,completeOriginalSourceFacetBindings=[list(x)for x in ids],completeRetainedOriginal3DSourceSHA256=digest(originals.tobytes()),allProjectedZeroOriginalPrimitiveClosureProofs=closure,completeOriginalSource3DAtomCensus=original_atoms,allThreeNomineeSourceDirectionalWindingProofs=orientation,allOrientedGeneratedNominations=oriented,completeIntegrated3DAtomCensus=integrated,allGeneratedSourceExactFiniteContacts=contacts,allClosedSourceContactSubsetSelections=selections,summary=summary,evidenceRefs=refs,qualification='Complete bounded selected-original and projected-zero finite-closure3D directed atomic edge context; source positions/planes/winding unchanged. Source-only three generated nominations may reverse ONLY generated winding when globally compatible with both source boundaries. Every incompatible winding/nonmanifold/open generated boundary and proper/unnominated finite source contact is retained as an unqualified negative. Existing91 original crossings/494+37projected overlaps/6+4projected failures remain unqualified. No whole terrain/candidate/F32/current actor/support/water/runtime approval, no actual mesh or live/state writes.')));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
