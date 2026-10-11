"""Complete named original262 foundation skin/current four-world proposal replay."""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_named_embedded_foundation_skin_v2_20261011 import verify,UID,SOURCE,ROLE,sha,canonical
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
FINITE=BASE/'government-xl-king-cheung-95691-complete18742-current-finite-diagnostic-v1-20261011'
GRADE=BASE/'government-xl-king-cheung-95691-complete262-part34-current-grade-cause-v1-20261011'
COUNTERPARTS=BASE/'government-xl-king-cheung-95691-complete262-part34-counterparts-context-v1-20261011'
GRAPH=BASE/'government-xl-king-cheung-95691-complete908-source-component-interfaces-v2-20261011'
BATCH='government-xl-king-cheung-95691-current-foundation-skin-role-proposal-v2-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,FINITE,GRADE,COUNTERPARTS,GRAPH]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');cap=read(INPUT/'complete-current-actual-source-and-ground.json.gz');finite=read(FINITE/'diagnostic.json.gz');assert data['uid']==UID and data['sourceSHA256']==SOURCE
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==cap['inputHashes']['3d-viewer/city/data/manifest.json']
 ground=np.asarray(data['completeDrawnGround'],dtype='<f8');rows=[]
 for mode,stream in data['completeWorldStreams'].items():
  w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');records=next(r['complete18742FaceComparisons']for r in finite['rows']if r['arithmetic']==mode)
  binding=dict(uid=UID,sourceSHA256=SOURCE,mode=mode,completeWorldSHA256=sha(w),completeGroundSHA256=sha(ground),completeFiniteRowsSHA256=canonical(records))
  proof=verify(w,ground,records,mode=mode,interpreted_role=ROLE,expected_binding=binding,current_binding=binding)
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha(w),proof=proof))
 save(DOC/'proposal.json.gz',dict(uids=[UID],sourceSHA256=SOURCE,rows=rows,rawWhole75FiniteFailuresRetained=True,namedFoundationRoleProposedOnly=True,
  allOtherOriginalPartsRemainIndependent=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs +=[HERE/'king_cheung_named_embedded_foundation_skin_20261011.py',HERE/'test_king_cheung_named_embedded_foundation_skin_20261011.py',HERE/'local/government-xl-king-cheung-95691-current-foundation-skin-role-proposal-v1-20261011/test-failure.json']
 refs +=[HERE/n for n in ['king_cheung_named_embedded_foundation_skin_v2_20261011.py','test_king_cheung_named_embedded_foundation_skin_v2_20261011.py',
  'exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','original_bound_facet_wall_context_v3_20261010.py',
  'original_bound_facet_wall_context_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py']]
 s=importlib.util.spec_from_file_location('king_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'named-original262-foundation-skin-current-four-world-grade-clear-body23-proposal',refs+[DOC/'proposal.json.gz'],dict(uids=[UID],completeNamedFaces=262,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-cheung-foundation-role-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
