"""UNEXECUTED source-only freezer of complete3actor runtime capture, no acceptance."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from upton_three_original_complete_current_runtime_capture_draft_v1_20261012 import BATCH,DOC,LOCAL,UIDS,MANIFEST_SHA,PLAN,INPUTS,ATTR,CLOSURE,PROTECTED,state,native,module,ref

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);a=p.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists()
 scope=read(DOC/'capture-scope.json');expected={r['uid']:r for r in read(PLAN)['actors']};rows=read(DOC/'selection.json.gz')['rows'];rt=read(LOCAL/'runtime-geometry.json.gz')['rows'];actual=read(DOC/'actual-render-geometry.json.gz');original=read(DOC/'original-full-source-root-context.json.gz')['rows'];before=read(DOC/'protected-state-before.json');native_before=read(DOC/'native-source-state-before.json')['rows']
 assert scope['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json') and scope['currentManifest']['sha256']==MANIFEST_SHA and scope['expectedNativeCount']==6649
 assert scope['startEndAllInputsVerified']and scope['allCurrentTerrainPatchesPreserved']and scope['terrainCandidates']==[] and scope['completeFaces']==13704 and not scope['physicalAccepted']and not scope['installationApproved']
 assert[r['uid']for r in rows]==[r['uid']for r in rt]==[r['uid']for r in actual['rows']]==[r['uid']for r in original]==UIDS
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];assert json.loads(json.dumps(native(rows),default=str))==native_before
 for r,t,a,o,g in zip(rows,rt,actual['rows'],original,scope['completeGroundByActor']):
  uid=r['uid'];e=expected[uid];raw=(ROOT/r['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);assert digest(raw)==e['sourceSHA256']and tri.shape==(e['completeFaces'],3,3)and digest(tri.astype('<f8').tobytes())==e['wholeWorldSHA256'];assert np.array_equal(tri,np.asarray(o['completeOriginalBinary64WorldTriangles']))
  assert t['index']==a['completeOriginalIndex']and t['position']==a['completeLiteralWorldPosition']and len(t['index'])//3==e['completeFaces'];assert a['loadedGroupScale']==[1,1,1];assert len(a['actualObjectGraph'])>0
  for mesh in a['actualRenderMeshes']:
   assert set(mesh['allActualAttributes'])>={'position','normal','color'} and mesh['allActualAttributes']['position']['array']==mesh['completeOriginalVertexAttribute'];assert mesh['allActualAttributes']['position']['count']*3==len(mesh['completeOriginalVertexAttribute']);assert len(mesh['modelMatrixUniformFloat32'])==16 and len(mesh['matrixWorldFloat64'])==16
  ground=np.asarray(t['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)==g['completeActualGroundFaces'] and digest(ground.astype('<f8').tobytes())==g['completeActualGroundSHA256']
 assert PROTECTED in before['uids'];forms=read(DOC/'complete-current-forms.json.gz')['rows'];native_ids={r['uid']for r in actual['nativeContextRows']};assert native_ids=={r['uid']for r in read(DOC/'native-nomination-inventory.json')['nominees']};basic_ids={r['uid']for r in actual['basicContextRows']};assert basic_ids=={r['building']['uid']for r in forms if not r['installedNative'] and r['building']['uid']not in UIDS}
 for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 subprocess.run(['node',str(CLOSURE),str(DOC.relative_to(ROOT))+'/','--verify'],cwd=ROOT,check=True)
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','reviewed_closed_source_capture_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(HERE/'upton_three_original_complete_current_runtime_capture_draft_v1_20261012.py',paths)
 for folder in [DOC,LOCAL]:
  for p in folder.rglob('*'):
   if p.is_file():
    paths.add(p)
    if p.name.endswith('.json')or p.name.endswith('.json.gz'):walker.declared_refs(read(p),paths)
 paths.update([ATTR,CLOSURE,HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'acceptance-metrics.mjs',HERE/'xl-final-script-pass.py',PLAN]+INPUTS)
 note='All13704 unchanged originalfaces across338946/12728/12662, all actual unused vertex attributes, source roots/object/model matrices and original/literal/left/balanced world arrays; complete relevant actual makeTerrain facets and foreignBASIC/native constructor/model contexts. All terrain patches preserved, current2dde/native6649 exact input/source/native/form/module/review fences. Source-specific identity interpretation is not physical approval;all23proper interior sourcecrossings and749body/17zero obligations remain. Installed-native nomination is catalogue-bound context only, not an exhaustive6649actual-position physical census or whole-native reapproval. No source pose/scale/geometry or terrain edit, sharededge/root/solid/engineering/legal/installation claim.'
 save(DOC/'review.json',dict(uids=UIDS,protectedReviewUIDs=before['uids'],sourceOnly=True,completeOriginalFaces=13704,genuineSourceBodyObligations=749,sourceZeroFaceObligations=17,currentManifest=scope['currentManifest'],nativeCount=6649,preservedProperInteriorCrossings=23,currentAcceptance=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,nativeReapproval=False,allCurrentNativeActualPhysicalAuditCompleted=False,finding=note,evidenceRefs=[ref(p)for p in sorted(paths)]));(DOC/'REVIEW.md').write_text('# Upton3actor complete current runtime capture\n\n'+note+'\n');paths.update([DOC/'review.json',DOC/'REVIEW.md'])
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'] and reservations.owns(lease)
 result=walker.F.freeze(BATCH,'three-original-upton-actual-attributes-ground-context-no-physical-approval',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=13704,preservedProperInteriorCrossings=23,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];assert json.loads(json.dumps(native(rows),default=str))==native_before;assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
 print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),sourceOnly=True,physicalAccepted=False,reviewRowsUnchanged=True)))
if __name__=='__main__':main()
