"""UNEXECUTED diagnostic freezer; preserves legacy runtime and missing physical acceptance."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from west_wing26195_complete_current_runtime_capture_draft_v2_20261012 import BATCH,DOC,LOCAL,UID,SOURCE_SHA,FACES,MANIFEST_SHA,PLAN,ATTR,CLOSURE,FREEZER,ref,module,state,preflight

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);args=parser.parse_args();lease=read(Path(args.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists();p=preflight();scope=read(DOC/'capture-scope.json');before=read(DOC/'protected-state-before.json');assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']
 assert scope['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')and scope['currentManifest']['sha256']==MANIFEST_SHA and scope['completeFaces']==FACES and scope['nativeCount']==6649 and scope['startEndAllInputsVerified']and scope['existingInstalledEntryPreserved']and not scope['physicalAccepted']and not scope['installationApproved']and scope['terrainCandidates']==[]
 raw=p['asset'].read_bytes();tri=decode_original_world_triangles(raw);assert digest(raw)==SOURCE_SHA and tri.shape==(FACES,3,3)and digest(tri.astype('<f8').tobytes())==scope['completeOriginalWorldSHA256'];original=read(DOC/'original-full-source-root-context.json.gz');assert np.array_equal(tri,np.asarray(original['completeOriginalBinary64WorldTriangles']))
 rt=read(LOCAL/'runtime-geometry.json.gz')['rows'];a=read(DOC/'actual-render-geometry.json.gz');assert len(rt)==len(a['rows'])==1;t=rt[0];attrs=a['rows'][0];assert t['uid']==attrs['uid']==UID and t['index']==attrs['completeOriginalIndex']and t['position']==attrs['completeLiteralWorldPosition']and len(t['index'])//3==FACES and attrs['loadedGroupScale']==[1,1,1]
 for mesh in attrs['actualRenderMeshes']:
  assert set(mesh['allActualAttributes'])>={'position','normal','color'}and mesh['allActualAttributes']['position']['array']==mesh['completeOriginalVertexAttribute']and mesh['allActualAttributes']['position']['count']*3==len(mesh['completeOriginalVertexAttribute'])and len(mesh['matrixWorldFloat64'])==len(mesh['modelMatrixUniformFloat32'])==16
 ground=np.asarray(t['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)==scope['completeActualGroundFaces']and digest(ground.astype('<f8').tobytes())==scope['completeActualGroundSHA256']
 assert {r['uid']for r in a['nativeContextRows']}=={r['uid']for r in read(DOC/'native-nomination-inventory.json')['nominees']};assert {r['uid']for r in a['basicContextRows']}=={u for u in p['forms']if u not in p['installed']}
 for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 subprocess.run(['node',str(CLOSURE),str(DOC.relative_to(ROOT))+'/','--verify'],cwd=ROOT,check=True);walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_freeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(HERE/'west_wing26195_complete_current_runtime_capture_draft_v2_20261012.py',paths)
 for folder in [DOC,LOCAL]:
  for path in folder.rglob('*'):
   if path.is_file():
    paths.add(path)
    if path.name.endswith('.json')or path.name.endswith('.json.gz'):walker.declared_refs(read(path),paths)
 paths.update(ROOT/path for path in scope['inputHashes']);paths.update([ATTR,CLOSURE,PLAN]);paths.update(ROOT/e['path']for e in p['plan']['sourceProvenanceRefs']);assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and reservations.owns(lease)
 result=walker.F.freeze(BATCH,'existing-west-wing-original-current-runtime-ground-context-no-physical-approval',sorted(paths),dict(uids=[UID],sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=FACES,legacyRuntimeDeliveryPreserved=True,legacyPhysicalAcceptanceGapRetained=True,sourceBodyCensusDeferred=True,currentAllNativePhysicalProved=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest'];print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)))
if __name__=='__main__':main()
