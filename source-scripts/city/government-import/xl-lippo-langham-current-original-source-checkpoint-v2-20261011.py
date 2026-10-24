"""Freeze complete byte-identical Langham acquisition; no identity/physical credit."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-lippo-langham-current-original-source-checkpoint-v2-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-langham-current-original-recovery-v1-20261011'
def main():
 assert not DOC.exists()
 data=read(INPUT/'selection.json.gz');assert data['sourceGeometryChanges']==0 and data['missing']==[] and len(data['rows'])==1
 r=data['rows'][0];assert r['uid']=='landsd/237843:0' and r['modelId']=='B355201752601063C0'
 path=ROOT/r['candidate']['path'];raw=path.read_bytes();assert digest(raw)==r['sourceSHA256']
 tri=decode_original_world_triangles(raw);assert len(tri)==r['native']['model']['triangles']==9522
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==data['manifestSHA256']
 for ref in data['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 proof=dict(uid=r['uid'],modelID=r['modelId'],sourceSHA256=r['sourceSHA256'],completeOriginalFaces=len(tri),worldSHA256=digest(tri.tobytes()),sourceStreams=source_stream_binding(raw),sourceLookupBasis=r['sourceLookupBasis'],nativeCacheKey=r['native']['cacheKey'],nativeResultSHA256=r['native']['resultSha'],currentSource=r['source'],recovery=r['recovery'],sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False)
 save(DOC/'proof.json.gz',proof)
 derived=json.loads(json.dumps(data));derived['rows'][0]['triangles']=len(tri);assert derived['rows'][0]['triangles']==derived['rows'][0]['native']['model']['triangles'];save(DOC/'check-selection.json.gz',derived)
 save(DOC/'prior-schema-failures.json',dict(sourceCheckpointError="KeyError: 'uids' before job enqueue; proof/source refs unchanged and reservation released",identityInputError="KeyError: 'triangles' before any identity evaluation",priorIdentityAccepted=False,priorPhysicalAccepted=False))
 old_runner=HERE/'xl-lippo-langham-current-original-source-checkpoint-v1-20261011.py'
 refs=[Path(__file__),INPUT/'selection.json.gz',INPUT/'check-selection.json.gz',DOC.parent/'government-xl-lippo-langham-current-original-source-checkpoint-v1-20261011/proof.json.gz',old_runner, DOC.parent/'government-xl-lippo-langham-current-complete-original-identity-diagnostic-v1-20261011/NONACCEPTING_FAILURE.json',HERE/'xl-lippo-langham-current-original-recovery-v1-20261011.py',HERE/'xl-next-support-recovery-20261005.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',path,manifest,*[ROOT/q['path'] for q in data['evidenceRefs']]]
 sp=importlib.util.spec_from_file_location('langham_source_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-byte-identical-current-native-langham-source-v1',refs,dict(uids=[r['uid']],completeOriginalFaces=len(tri),sourceSHA256=r['sourceSHA256'],sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],uid=r['uid'],sourceSHA256=r['sourceSHA256'],faces=len(tri))),flush=True)
if __name__=='__main__':main()
