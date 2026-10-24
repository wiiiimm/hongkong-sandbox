"""Stage six unchanged independent Market originals and reviewed dual native ground.

This only prepares assets, dry-runs publication and runs staged browser acceptance.
Root performs separately guarded live publication after reviewing every receipt.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from dependency_preflight import from_catalogues
UIDS={'landsd/'+u+':0' for u in ['313033','313034','313116','313118','313119','313121']}
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
ROLE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-current-role-v10'
BATCH='government-xl-terrain-recovery-market-six-typed-stage-v3-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/'government-xl-terrain-recovery-market-six-typed-stage-v2-20261009'
BROWSER_CONFIG=DOC/'browser-config.json'
LEASE=HERE/'local'/BATCH/'install-reservation.json'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def recheck(local):
 physical=read(PHYSICAL/'result.json');role_result=read(ROLE/'result.json')
 for doc,result in [(PHYSICAL,physical),(ROLE,role_result)]:
  assert read(doc/'neon-sync.json')==dict(jobId=result['jobId'],resultVerified=True)
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 assert physical['publication'] is False and physical['newlyInstalled']==physical['modelGeometryChanges']==physical['scriptExternalAICalls']==0
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid'] for r in rows}==UIDS
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for row in rows:assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 kernel=module('market_fresh_original_roles',HERE/'xl-terrain-recovery-20261009-market-six-current-role-v10.py');role=kernel.recheck();assert json.loads(json.dumps(role))==read(ROLE/'typed-role.json.gz')
 assert role['independentPhysicalChecksPassed'] and not role['unresolvedIndependentPhysicalReasons'] and role['verifiedPodiumWallRole']['verifiedWallRole']
 assert role['completeOriginalFaces']==40100 and role['completeOriginalComponents']==84 and role['currentNeighbourFormsAccounted']==42
 assert {r['uid'] for r in role['completeFreshCurrentIdentities']}==UIDS and all(r['passed'] for r in role['completeFreshCurrentIdentities'])
 for r in role_result['evidenceRefs']:assert ref(ROOT/r['path'])==r
 return rows,role['completeFreshCurrentIdentities'],role
def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();rows,identities,role=recheck(HERE/'local'/BATCH/'identity-recheck')
 original=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-typed-stage-v2-20261009'
 prior=read(original/'stage.json');assert set(prior['uids'])==UIDS and prior['checksPassed'] and not prior['publication']
 for item in prior['evidenceRefs']:assert ref(ROOT/item['path'])==item
 save(DOC/'identity-publication-recheck.json',identities);save(DOC/'typed-role-publication-recheck.json.gz',role)
 config=read(STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';save(BROWSER_CONFIG,config)
 evidence=prior['evidenceRefs']+[ref(original/'stage.json'),ref(Path(__file__)),ref(BROWSER_CONFIG),ref(DOC/'identity-publication-recheck.json'),ref(DOC/'typed-role-publication-recheck.json.gz'),ref(HERE/'xl-terrain-recovery-20261009-multi-native-assembly-browser-v2.mjs')]
 decision=dict(batch=BATCH,uids=sorted(UIDS),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},manifestSHA256=role['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence,priorFailedBrowserPreserved=ref(original/'staged-browser.json'),qualification='Unchanged staged source/assets/two-parent terrain plan. Retained actors are independent foreign originals, not support dependencies; every selected candidate view records actual renderer wanted/pixel/distance eligibility and requires active+visible retained detail whenever wanted. Both retained sources also require own-camera desktop/mobile day/night full-source framing and active+visible presence. No runtime priority/cache residency change.')
 save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE/'xl-terrain-recovery-20261009-publish-reviewed-multi-native.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
 call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-assembly-browser-v2.mjs'),'staged',ref(BROWSER_CONFIG)['path']])
 report=module('market_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',UIDS)
 expected={(u,w,t) for u in ['landsd/313032:0','landsd/99395:0'] for w in [1280,390] for t in ['15:00','22:00']}
 assert {(v['uid'],v['width'],v['time']) for v in report['retainedNativeOwnViews']}==expected
 assert all(v['active'] and v['visible'] and v['fullyFramed'] for v in report['retainedNativeOwnViews'])
 for v in report['views']:
  if 'time' in v:assert all(not r['wanted'] or r['active'] and r['visible'] for r in v['nativeSupports'].values())
 for r in evidence:assert ref(ROOT/r['path'])==r
 recheck(HERE/'local'/BATCH/'identity-recheck-final')
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(DOC/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=sorted(UIDS),retainedNativeOwnViews=8,publication=False,newlyInstalled=0)),flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args()
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned()
  return
 assert not DOC.exists() and STAGE.exists()
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];resources={'building:'+r['building']['uid'] for r in forms}|{'terrain-patch:'+u for u in UIDS}
 resources|={'terrain-surface:'+r['url'] for r in read(PHYSICAL/'terrain-candidates.json')[0]['replacesMany']}
 claim=reservations.claim('codex-market-stage-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
