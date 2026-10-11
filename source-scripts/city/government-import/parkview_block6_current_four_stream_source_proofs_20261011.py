"""All11041current source facets,81original contact paths and4complete openings.
No acceptance/geometry edits; every stream and complete actual ground is bound.
"""
from pathlib import Path
from fractions import Fraction as F
import json,numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure
from complete_original_lower_opening_mounts_v2_20261011 import verify as opening_verify,binding
B=ROOT/'docs/astra-city/government-import';PHYSICAL=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';GRAPH=B/'government-xl-parkview-block6-complete-original-support-paths-v1-20261011';BATCH='government-xl-parkview-block6-current-four-stream-source-proofs-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];runtimepath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';rt=read(runtimepath)['rows'][0];ap=PHYSICAL/'actual-render-geometry.json.gz';a=read(ap)['row'];assert a['uid']==r['uid']=='landsd/255438:0'and a['sourceSHA256']==r['sourceSHA256'];index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);assert a['completeOriginalIndex']==rt['index']and np.array_equal(np.asarray(a['completeLiteralWorldPosition']),np.asarray(rt['position']));ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
 worlds=[decode_original_world_triangles(asset.read_bytes()),np.asarray(a['completeLiteralWorldPosition']).reshape(-1,3)[index],np.asarray(a['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[index],np.asarray(a['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[index]];names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];graph=read(GRAPH/'diagnostic.json.gz');cs=graph['completeSourceEdgeBodyFaces'];parents={int(k):v for k,v in graph['completeConditionalParents'].items()};assert len(parents)==81;orphans=graph['unreachedBodies'];hostfaces=sorted(f for i in parents for f in cs[i]);rows=[]
 for mode,world in zip(names,worlds):
  assert world.shape==(11041,3,3)and np.isfinite(world).all();worldsha=digest(world.tobytes());same=next((x for x in rows if x['completeWorldSHA256']==worldsha),None)
  if same is not None:row={**same,'mode':mode,'identicalImmutableWorldAndGroundProofsReusedFrom':same['mode']};rows.append(row);continue
  pin=dict(completeWorldSHA256=worldsha,completeGroundSHA256=digest(ground.tobytes()),sourceSHA256=r['sourceSHA256'],actualAttributes=ref(ap),kernel=ref(HERE/'exact_original_face_conservative_clearance_v5_20261010.py'));checkpoint=LOCAL/(mode+'-finite-partial.json.gz');partial=read(checkpoint)if checkpoint.exists()else None;assert partial is None or partial['binding']==pin;faces=[]if partial is None else partial['allFaces']
  for i in range(len(faces),11041):
   faces.append(dict(sourceFace=i,proof=finite(world[i],ground)))
   if i%500==0:save(checkpoint,dict(binding=pin,allFaces=faces,complete=False));print(json.dumps(dict(mode=mode,faces=i)),flush=True)
  save(checkpoint,dict(binding=pin,allFaces=faces,complete=True));edgecensus=[]
  for i,fs in enumerate(cs):
   p=census(world,fs);edgecensus.append(dict(originalBody=i,proof=p))
  contacts=[]
  for child,parent in sorted(parents.items()):
   if parent is None:continue
   witness=next(p for p in graph['allExactCrossBodyContacts']if p['dimension']>0 and set(p['bodies'])=={child,parent});f,h=witness['originalFaces'];points=finite_intersection_points(rational_face(world[f]),rational_face(world[h]));contacts.append(dict(bodies=[child,parent],originalFaces=[f,h],**contact_measure(points)))
  openings=[dict(originalBody=i,proof=opening_verify(world,cs[i],hostfaces,expected_binding=binding(world,cs[i],hostfaces)))for i in orphans]
  row=dict(mode=mode,completeWorldSHA256=worldsha,completeGroundSHA256=digest(ground.tobytes()),all11041WholeFacetFiniteProofs=faces,unprovedWholeFacetIDs=[x['sourceFace']for x in faces if not x['proof']['existingOrdinaryClearanceBoundProved']],complete85OriginalBodyEdgeCensuses=edgecensus,original81BodyPositiveContactPaths=contacts,all80ContactPathsRemainPositive=all(x['dimension']>0 for x in contacts),all85OriginalBodiesRemainSingleNonzeroSharedEdgeBodies=all(len(x['proof']['sharedEdgeConnectedComponents'])==1 and not x['proof']['exactNonrenderingOriginalFaces']for x in edgecensus),completeFourOpeningProofs=openings,allFourCompleteLowerOpeningsAssociate=all(x['proof']['completeLowerOpeningAssociated']for x in openings),bodyAndHostAndFullSourceBindingsIndependent=True,sourceGeometryChanges=0,currentAcceptance=False,structuralRootCredit=False,architecturalFunctionInferred=False);rows.append(row);print(json.dumps(dict(mode=mode,unproved=row['unprovedWholeFacetIDs'],contacts=row['all80ContactPathsRemainPositive'],openings=row['allFourCompleteLowerOpeningsAssociate'],bodies=row['all85OriginalBodiesRemainSingleNonzeroSharedEdgeBodies'])),flush=True)
 refs=[ref(p)for p in [Path(__file__),asset,runtimepath,ap,PHYSICAL/'selection.json.gz',PHYSICAL/'current-raw-outcome.json',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',HERE/'complete_original_lower_opening_mounts_v2_20261011.py',HERE/'test_complete_original_lower_opening_mounts_v2_20261011.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'parkview_block6_four_original_roof_opening_mounts_20261011.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/255438:0','landsd/254491:0'],sourceSHA256=r['sourceSHA256'],completeSourceFaces=11041,completeCurrentGroundFaces=len(ground),rows=rows,explicitArithmeticNotUniversalGPUCameraGuarantee=True,mandatoryCurrentNativeGradeCarrierPathStillRequired=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=refs))
if __name__=='__main__':main()
