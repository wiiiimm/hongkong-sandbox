"""DRAFT nonaccepting freezer for root-approved two-actor complete current ground capture.
Executes only after completed capture and root stable SHA; no review/publication writes.
"""
import argparse,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;METHOD=B/'government-xl-beverly-elm-complete-current-support-ground-capture-method-v1-20261011'
UIDS=['landsd/255939:0','landsd/258892:0'];STATE_UIDS=UIDS+['landsd/255543:0','landsd/253874:0']
BODYDOCS=[B/'government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011',B/'government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid',(STATE_UIDS,)).fetchall()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest-sha256',required=True);args=parser.parse_args();assert len(args.manifest_sha256)==64;assert DOC.exists()and not(DOC/'result.json').exists();before=state();scope=read(DOC/'capture-scope.json');preflight=read(DOC/'support-source-preflight.json');assert scope['currentManifest']==preflight['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')and scope['currentManifest']['sha256']==args.manifest_sha256
 assert scope['startEndInputsVerified']and scope['allCurrentTerrainPatchesPreserved']and scope['terrainCandidates']==[]and not scope['currentAcceptance']and not scope['nativeReapproval'];runtime=read(LOCAL/'runtime-geometry.json.gz');actual=read(DOC/'actual-render-geometry.json.gz');selection=read(DOC/'selection.json.gz');assert len(runtime['rows'])==len(actual['rows'])==len(selection['rows'])==2
 actorrows=[]
 for i,uid in enumerate(UIDS):
  r=next(r for r in runtime['rows']if r['uid']==uid);a=next(r for r in actual['rows']if r['uid']==uid);s=next(r for r in selection['rows']if r['uid']==uid);binding=next(r for r in preflight['bodySourceBindings']if r['uid']==uid);raw=(ROOT/s['candidate']['path']).read_bytes();original=decode_original_world_triangles(raw);assert digest(raw)==r['sourceSHA256']==a['sourceSHA256']==s['sourceSHA256'];assert digest(original.tobytes())==binding['completeOriginalWorldSHA256'];ground=np.asarray(r['drawnGroundGeometry'],dtype=float).reshape(-1,3,3);gr=next(g for g in scope['completeGroundRows']if g['uid']==uid);assert len(ground)==gr['faces']and digest(ground.tobytes())==gr['worldSHA256'];assert a['completeOriginalIndex']==r['index']and a['completeLiteralWorldPosition']==r['position']
  old=read(BODYDOCS[i]/'diagnostic.json.gz')
  if i==0:
   assert old['completeOriginalCarrierFaces']==len(original)==12640 and old['completeOriginalCarrierWorldSHA256']==digest(original.tobytes());census=old['completeOriginalCarrierBodyCensus'];bodycount=273;role='Installed original carrier; cap2122 genuine674-face body. Prior owned350facet historical cap coverage failure is preserved; no current cap/grade/root or whole native reapproval.'
  else:
   assert old['wholeOriginalPodiumFaces']==len(original)==764 and old['completePodiumWorldSHA256']==digest(original.tobytes());census=old['completePodiumNonzeroBodyCensus'];bodycount=1;role='Held original podium;99 exact original line contacts to1112-face towerbody269. Podium grounding/burial and305 other tower bodies unresolved; no installation/source acceptance.'
  assert len(census['sharedEdgeConnectedComponents'])==bodycount;assert sorted(f for body in census['sharedEdgeConnectedComponents']for f in body)==sorted(census['completeRenderableFaceIds']);assert census['completeOriginalFaceIds']==list(range(len(original)))and census['completeWorldTrianglesSHA256']==digest(original.tobytes())
  actorrows.append(dict(uid=uid,sourceSHA256=digest(raw),completeOriginalFacets=len(original),completeOriginalWorldSHA256=digest(original.tobytes()),exactCompleteBodyCensusRef=ref(BODYDOCS[i]/'diagnostic.json.gz'),bodySourceReceiptRef=ref(BODYDOCS[i]/'result.json'),genuineOriginalBodies=bodycount,completeActualRelevantGroundFaces=len(ground),completeActualRelevantGroundSHA256=digest(ground.tobytes()),literalWorldSHA256=digest(np.asarray(r['position'],dtype=float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)].tobytes()),actualFourStreamAttributesRef=ref(DOC/'actual-render-geometry.json.gz'),roleLimits=role,gradeRootCredit=False,currentAcceptance=False,nativeReapproval=False))
 spec=importlib.util.spec_from_file_location('reviewed_twoactor_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);paths=set();m.local_imports(Path(__file__),paths);m.local_imports(HERE/'beverly_elm_complete_current_support_ground_capture_v2_20261011.py',paths)
 for folder in [DOC,LOCAL,METHOD]:
  for p in folder.rglob('*'):
   if p.is_file():
    paths.add(p)
    if p.name.endswith('.json')or p.name.endswith('.json.gz'):m.declared_refs(read(p),paths)
 for folder in BODYDOCS:
  paths.update([folder/'diagnostic.json.gz',folder/'result.json'])
 paths.update(HERE/n for n in ['beverly_elm_current_support_actual_render_attributes_v2_20261011.mjs','beverly_elm_capture_module_closures_v2_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs'])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in BODYDOCS:
   oldreceipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(oldreceipt['jobId'],)).fetchone()==('complete',oldreceipt)
 note='Complete exact original support actors and complete relevant actual current makeTerrain Float32 facets, all installed terrain retained with empty candidates; full current catalogue/form/source/body/module input fences and original/literal/explicit left/balanced source attributes. This is byte-bound diagnostic context only, not whole finite clearance, qualified cap/grade/root, architecture intent, protective regression discharge, whole-native reapproval or current acceptance. Original16 BeverlyK details and305 other Elm tower bodies remain unresolved. Every saved historical owned/native/BASIC/foreign failure and all raw rows are retained separately; proposed historical scopes are not current acceptance. Sampling metrics check every loaded vertex/triangle centroid and low-rim edge interiors <=1m; complete drawn facets are captured separately for subsequent exact finite proof. Explicit F32 arithmetic is not universal GPU/camera proof.'
 save(DOC/'review.json',dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,actors=actorrows,currentManifest=scope['currentManifest'],finding=note,allHistoricalObligations=preflight['historicalObligations'],completeCurrentRelevantForeignBasicNativeInventory=preflight['fullCurrentRelevantForeignBasicAndNativeFormInventory'],noHistoricalFailureWaiver=True,reviewRowsSnapshotBefore=before,modelReviewWrites=0,evidenceRefs=[ref(p)for p in sorted(paths)]));(DOC/'REVIEW.md').write_text('# Exact current support-ground source context\n\n'+note+'\n\nComplete ground/source hashes and original body receipts are recorded in review.json. Next numerical obligation: exact full finite cap coverage/strict clearance followed by genuine exposed grade-wall/whole exposed-edge route; neither is implied by capture.\n');paths.update([DOC/'review.json',DOC/'REVIEW.md']);save(DOC/'evidence-scope.json',dict(sourceOnly=True,closedEvidenceRefs=[ref(p)for p in sorted(paths)]))
 assert state()==before;save(DOC/'review-state-fence.json',dict(affectedUIDs=STATE_UIDS,before=before,after=state(),exactRowsUnchanged=True,modelReviewWrites=0,scope='Exact rows checked after diagnostic processing and again after freeze; no review writes.'));paths.add(DOC/'review-state-fence.json');result=m.F.freeze(BATCH,'two-original-support-actors-complete-actual-current-ground-source-only',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,actors=actorrows,currentManifest=scope['currentManifest'],noHistoricalFailureWaiver=True,noForeignRegressionDischarge=True,noNativeReapproval=True,modelReviewWrites=0));assert state()==before;assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest'];print(json.dumps(dict(jobId=result['jobId'],reviewRowsUnchanged=True,currentAcceptance=False)))
if __name__=='__main__':main()
