"""Supervised complete unchanged current King source-role replay; no installation."""
import json,uuid,subprocess,sys,importlib.util
from run import ROOT,HERE,read,save,reservations
from king_cheung_whole_current_role_bound_v2_20261011 import verify_files,DOCS,UID,ref
BATCH='government-xl-king-cheung-95691-whole-current-role-acceptance-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 role,entry=verify_files();assert reservations.owns(lease)
 save(DOC/'acceptance.json',role);save(DOC/'staged-original-entry.json',entry)
 paths=[__file__,HERE/'king_cheung_whole_current_role_bound_v2_20261011.py',HERE/'king_cheung_whole_current_role_policy_v2_20261011.py',HERE/'king_cheung_named14_intrinsic_visual_placement_20261011.py',HERE/'test_king_cheung_whole_current_role_v2_20261011.py',DOC/'acceptance.json',DOC/'staged-original-entry.json']
 for folder in DOCS.values():
  r=read(folder/'result.json');paths.append(folder/'result.json');paths.extend(ROOT/p['path']for p in r['evidenceRefs'])
 s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert reservations.owns(lease)
 result=m.freeze(BATCH,'king-complete18742-908-four-stream-current-typed-role-acceptance-v2',paths,dict(uids=[UID],completeOriginalFaces=18742,completeOriginalRealComponents=908,currentTypedPhysicalAccepted=True,acceptanceReadyForStaging=True,installationApproved=False,newlyInstalled=0));print(json.dumps(dict(jobId=result['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-full-role-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
