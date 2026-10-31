"""Fresh atomic failure checks plus full source/retained views for physical originals.

No publication: the old sequential per-model failure loop cannot test an atomic
family. Its visual/pick/collision captures are composed with a REQUIRED fresh
five-case atomic lifecycle run on exactly the same stage/assets/terrain/code.
"""
from pathlib import Path
import argparse,copy,json,os,shutil,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-ocean-coordinated-full-browser-v1-20261027';PHYSICAL='government-xl-ocean-four-original-physical-review-v2-20261027';ATOMIC='government-xl-ocean-four-atomic-lifecycle-browser-v1-20261027';OLD='government-xl-after-waterfront-ocean-four-corrected-private-diagnostic-v4-20261027'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def verify_atomic(report,models):
 ids=sorted(m['uid']for m in models);sources={m['uid']:(m['sha256'],m['triangles'])for m in models}
 assert report['passed']and not report['pageErrors']and len(report['cases'])==5
 assert report['cases'][0]['width']==1280 and report['cases'][0]['failedUid']is None
 assert sorted(c['failedUid']for c in report['cases'][1:])==ids
 for case in report['cases']:
  assert case['baseOnlyRestoredCompleteGroup']and case['completeGroupEvicted']and not case['audit']['violations']
  assert {s['uid']:(s['sha256'],s['triangles'])for s in case['sources']}==sources and all(s['active']for s in case['sources'])
  assert all(t['active']in[[],ids]for t in case['audit']['transitions'])and any(t['active']==ids for t in case['audit']['transitions'])
  if case['failedUid']:assert case['width']==390 and case['failureKeptAllBasics']
 return True

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');a=parser.parse_args();refs=[Path(__file__)];pins={}
 def take(name,path):
  if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 review=take(PHYSICAL,BASE/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json');assert review['identityAccepted']and review['sourceSpecificPhysicalInterpretationAccepted']and review['completeNeighbourInterpretationAccepted']and review['companionRootsApproved']and not review['visualAcceptance']and not review['installationApproved']and not review['publication']
 sources=review['sourceSHA256ByUid'];ids=sorted(sources);assert len(ids)==4 and review['activationGroup']==ids and len(review['retainedNativeUids'])==len(review['retainedNativeEntries'])==27
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==review['currentManifestSHA256'];refs.append(manifest)
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),review['leaseResources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
  finally:
   if reservations.owns(lease):assert reservations.release(lease)['ok']
  return
 lease=read(LEASE);assert reservations.owns(lease)and set(review['leaseResources'])<=set(lease['resources'])and not DOC.exists()
 prior=HERE/'local/government-xl-ocean-four-atomic-lifecycle-stage-v1-20261027';catalogue=take(ATOMIC,prior/'catalogue.json');atomic_config=take(ATOMIC,prior/'config.json');forms=take(ATOMIC,prior/'source-forms.json')
 assert {m['uid']:m['sha256']for m in catalogue['models']}==sources and all(m['activationGroup']==ids and m['proceduralWindows']is False for m in catalogue['models'])
 for m in catalogue['models']:
  source=prior/m['asset'];assert digest(source.read_bytes())==m['sha256'];refs.append(source);target=LOCAL/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'source-forms.json',forms)
 old=HERE/'local'/OLD;config=take(OLD,old/'browser-config-1280.json');assert config['terrain']==atomic_config['terrain'];assert config['nativeSupportUidsByModel']=={u:[p]for u,p in review['supportByUid'].items()}
 assert set(config['additionalRetainedUids'])==set(review['retainedNativeUids'])and config['catalogueReplacements']==[]
 for t in config['terrain']:
  source=ROOT/t['source'];assert digest(source.read_bytes())==t['sha256'];refs.append(source)
 # Authenticate current code independently; historical numeric runtime output
 # does not transfer its old official-models.js provenance to this new run.
 for name in ['app.js','official-models.js','streaming.js','model-group-lifecycle.js','model-activation-groups.js','model-support.js','official-model-assets.js','tile-cache.js','model-variants.js','model-byte-cache.js']:
  path=ROOT/'3d-viewer/city'/name;refs.append(path)
 for entry in review['retainedNativeEntries'].values():assert entry.get('publicationApproved')is True
 destination='city/data/official-models/'+BATCH+'/catalogue.json';config.update(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL=destination,viewerURL='http://127.0.0.1:4177/city.html',additionalRetainedUids=review['retainedNativeUids'])
 atomic_config.update(stage=config['stage'],catalogueURL=destination,viewerURL=config['viewerURL']);save(LOCAL/'atomic-config.json',atomic_config)
 tool=HERE/'ronsdale_three_live_browser_v15_20261026.mjs';atomic_tool=HERE/'model_atomic_lifecycle_browser_v1_20261027.mjs';refs.extend([tool,atomic_tool])
 expected={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};DOC.mkdir()
 def call(label,command,timeout):
  assert reservations.owns(lease);print(label,'starting',flush=True)
  with (DOC/(label+'.log')).open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=timeout)
  save(DOC/(label+'-command.json'),dict(command=command,exitCode=r.returncode));assert r.returncode==0,label
  assert reservations.owns(lease);print(label,'passed',flush=True)
 preflight=LOCAL/'preflight-config.json';save(preflight,dict(**config,doc=str(DOC.relative_to(ROOT))+'/'))
 call('preflight',['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],120)
 call('atomic-lifecycle',['node',str(atomic_tool),str((LOCAL/'atomic-config.json').relative_to(ROOT)),str((DOC/'atomic-lifecycle').relative_to(ROOT))],1800)
 atomic=read(DOC/'atomic-lifecycle/report.json');assert verify_atomic(atomic,catalogue['models'])
 for width in [1280,390]:
  path=LOCAL/('browser-config-'+str(width)+'.json');save(path,dict(**config,viewportWidths=[width],failureTestUids=[],doc=str((DOC/str(width)).relative_to(ROOT))+'/'))
  call('browser-'+str(width),['node',str(tool),'staged',str(path.relative_to(ROOT))],1800)
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
  own=report['retainedNativeOwnViews'];assert len(own)==54 and {(r['uid'],r['time'])for r in own}=={(u,t)for u in review['retainedNativeUids']for t in ['15:00','22:00']}
  assert all(r['active']and r['visible']and r['fallbackFaces']==0 for r in own)
 assert verify_atomic(read(DOC/'atomic-lifecycle/report.json'),read(LOCAL/'catalogue.json')['models'])
 for path,sha in expected.items():assert digest((ROOT/path).read_bytes())==sha,path
 assert digest(manifest.read_bytes())==review['currentManifestSHA256']and reservations.owns(lease)
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 save(DOC/'browser-composition.json',dict(sameStageAssetTerrainAndCodeAcrossChecks=True,mandatoryFreshAtomicCases=5,failedPeerCases=ids,fullSourceAndRetainedViewportWidths=[1280,390],retainedNativeViews=108,sequentialFailureLoopNotApplicableToAtomicGroups=True,allFailureCasesExecuted=True,installationApproved=False,performanceAcceptance=False))
 result=dict(uids=ids,sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,allBrowserDiagnosticsPassed=True,downloadFailureTestsSkipped=False,atomicFailureCases=5,retainedNativeUids=review['retainedNativeUids'],visualAcceptance=False,qualifiedForLiveVerification=False,installationApproved=False,publication=False,sourceGeometryChanges=0,nativeMetadataChanges=0,performanceAcceptance=False)
 module('ocean_coordinated_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'physical-original-atomic-failure-and-full-retained-browser-composition-v1',refs,result)
if __name__=='__main__':main()
