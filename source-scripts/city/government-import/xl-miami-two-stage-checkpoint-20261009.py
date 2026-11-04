"""Replay complete source/physical/browser evidence and fence a non-publishing handoff."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from miami_two_related_podium_identity_20261009 import verify_collection,UIDS
BATCH='government-xl-miami-two-original-staged-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
BASE=ROOT/'docs/astra-city/government-import'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return digest(Path(p).read_bytes())
def receipt(batch,job):
 p=BASE/batch/'result.json';x=read(p);assert x['jobId']==job
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',x)
 for r in x['evidenceRefs']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
 return x
def recheck():
 physical=receipt('government-xl-miami-two-complete-original-physical-20261009','d75a4c0ec6d0bf7641f963d41e4a761cc32eded1eab84b99dca37a76b0ec67bb');assert physical['scriptFullAcceptancePassed'] and physical['reasons']==[]
 identity_receipt=receipt('government-xl-miami-two-related-podium-identity-20261009','328fbc173f56b5cd0626a231e4e287708f3f5d9b510c8896b7cd4657903cd711');assert identity_receipt['identityAccepted']
 stage=read(DOC/'stage-inputs.json');manifest=sha(ROOT/'3d-viewer/city/data/manifest.json');assert manifest==stage['currentManifestSHA256']
 assert sha(STAGE/'catalogue.json')==stage['catalogueSHA256'] and sha(STAGE/'plan.json')==stage['planSHA256']
 catalogue=read(STAGE/'catalogue.json');assert {m['uid'] for m in catalogue['models']}==UIDS
 for m in catalogue['models']:
  assert sha(STAGE/m['asset'])==m['sha256']==stage['sourceSHA256s'][m['uid']]
  assert m['proceduralWindows'] is False and not m.get('suppressesBuildingUids') and m['publicationApproved'] is False
 proof=verify_collection();assert proof==stage['identityProof']
 contact=read(DOC/'basic-podium-exact-original-contacts.json.gz');assert {r['uid'] for r in contact['rows']}==UIDS
 for p,h in contact['inputHashes'].items():assert sha(ROOT/p)==h,p
 for r in contact['rows']:assert r['result']['allPairsExamined'] and r['sourceSHA256']==stage['sourceSHA256s'][r['uid']] and r['currentPodiumUID']=='landsd/232089:0'
 report=module('miami_two_browser_receipt_validator',HERE/'integrate.py').browser_verified(DOC/'browser-v2/staged-browser.json',UIDS)
 for v in report['views']:
  if 'time' in v:
   assert v['fullyFramed'] and abs(v['ground']-v['groundSampler'])<=.004
   assert v['retained']['landsd/232089:0']=={'loaded':True,'detailedActive':False,'hidden':False}
   assert (DOC/'browser-v2'/v['file']).is_file()
 assert read(DOC/'publication-dry-run.json')['passed'] and read(DOC/'publication-dry-run.json')['manifestUnchanged']
 return {'uids':sorted(UIDS),'physicalJobId':physical['jobId'],'identityJobId':identity_receipt['jobId'],'currentManifestSHA256':manifest,'sourceSHA256s':stage['sourceSHA256s'],'stagedBrowserPassed':True,'desktopMobileDayNightViews':8,'intentional503FallbackRetryCases':2,'wholeOriginalBoundsFramed':True,'currentBasicPodiumRetained':True,'currentPodiumExactLineContacts':{r['uid']:r['countsByDimension']['1'] for r in contact['rows']},'allOriginalFacesAndCurrentPodiumFacesAccounted':True,'publicationDryRunPassed':True,'scriptFullAcceptancePassed':True,'identityAccepted':True,'physicalAccepted':True,'sourceIdentityInterpretationUsedAI':True,'remainingReason':'root-independent-export-review-serial-live-installation','nextStep':'Root independently inspects exact contacts/exports, copies only review flags in final installation stage, replays fresh source/physical inputs under publication lease, performs guarded apply and both live browser checks. No model is installed by this checkpoint.'}
def main():
 result=recheck();save(DOC/'acceptance-ready-handoff.json',result)
 paths=[Path(__file__),HERE/'xl-miami-two-stage-preparation-20261009.py',HERE/'xl-miami-two-basic-podium-contact-inputs-20261009.mjs',HERE/'xl-miami-two-basic-podium-exact-contacts-20261009.py',HERE/'xl-miami-two-staged-browser-20261009.mjs',HERE/'resolution-assembly-browser.mjs',HERE/'resolution-recovery-browser.mjs',HERE/'integrate.py',HERE/'test_miami_two_related_podium_identity_20261009.py',HERE/'miami_two_related_podium_identity_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE.parent/'model-integration-20260909/publish.py',HERE.parent/'island-detail-integration/publish.py',ROOT/'3d-viewer/city.html',ROOT/'3d-viewer/city/app.js',ROOT/'3d-viewer/city/building-geometry.js']
 for b in ['government-xl-miami-two-complete-original-physical-20261009','government-xl-miami-two-related-podium-identity-20261009']:
  paths.append(BASE/b/'result.json');paths.extend(ROOT/r['path'] for r in read(BASE/b/'result.json')['evidenceRefs'])
 paths.extend(p for p in STAGE.rglob('*') if p.is_file());integration=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;paths.extend(p for p in integration.rglob('*') if p.is_file())
 module('miami_two_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-unchanged-original-towers-complete-current-staged-browser-publication-dry-run-v1',paths,result)
if __name__=='__main__':main()
