"""Draft orchestration only; exact reviewed source/native finite caller unchanged."""
import argparse,json,subprocess,sys,uuid,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import citywalk134332_surviving_native_finite_interface_draft_v1_20261013 as Q
BATCH=Q.D.name;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PROPOSAL=Q.B/'government-xl-citywalk134332-supervisor-freezer-wiring-proposal-v1-20261013';FREEZER=HERE/'citywalk134332_freeze_surviving_native_interfaces_draft_v1_20261013.py';GROUP=Q.B/'government-xl-fourteen-retained-component-identity-20261008/134332-0.json';CLOSURE=HERE/'citywalk134332_complete_exporter_module_closure_draft_v1_20261013.mjs';CLOSURE_OUTPUT=LOCAL/'complete-exporter-module-closure.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(uids,)).fetchall()
def verified_plan():
 plan=read(PROPOSAL/'wiring-plan.json')
 for e in plan['codeAndHistoricalPins']:assert ref(ROOT/e['path'])==e
 validation=read(ROOT/plan['completedPreparationValidation']['path']);assert ref(ROOT/plan['completedPreparationValidation']['path'])==plan['completedPreparationValidation'];assert validation['testsPassed']==validation['executedTests']==7 and validation['testExitCode']==validation['preflightExitCode']==0
 return plan

def inputs(a):
 plan=verified_plan();assert a.expected_manifest==plan['expectedManifestSHA256'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==a.expected_manifest
 catalogue_refs=[ref(ROOT/'3d-viewer'/url)for url in read(manifest)['officialModelCatalogues']];entries=[e for c in catalogue_refs for e in read(ROOT/c['path'])['models']];assert len(entries)==6650;lookup,suppressed=Q.current_actor_partition(entries)
 global_suppressors={}
 for e in entries:
  for u in e.get('suppressesBuildingUids',[]):global_suppressors.setdefault(u,[]).append(e['uid'])
 global_suppressors={u:sorted(v)for u,v in sorted(global_suppressors.items())}
 survival=[dict(uid=e['uid'],modelId=e['modelId'],sourceSHA256=e['sha256'],suppressedBy=global_suppressors.get(e['uid'],[]),survives=not global_suppressors.get(e['uid'],[]),rawEntry=e)for e in sorted(entries,key=lambda e:e['uid'])];assert len({e['uid']for e in survival})==6650
 family=[f['uid']for f in read(GROUP)['completeGroupForms']];assert len(family)==len(set(family))==13 and Q.UID in family
 impacted=sorted({u for e in entries if e['uid']in Q.ACTORS for u in e.get('suppressesBuildingUids',[])})
 uids=sorted(set(family)|set(Q.ACTORS)|set(impacted));assert uids==plan['protectedUIDs'] and len(uids)==plan['canonicalActorCount']
 # Every declared native support is actual installed and within this exact set.
 dependencies=[]
 for u in Q.ACTORS:
  for d in lookup[u].get('supportDependencies',[]):assert d['uid']in lookup and d['uid']in uids;assert lookup[d['uid']]['buildingCSUID']==d['csuid'];dependencies.append(dict(owner=u,dependency=d))
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']=='5cb980a97466802b';assert ref(pointer)==plan['currentSourceReviewPointer']
 source_row=read(Q.SEL)['rows'][0];source_key=source_row['native']['cacheKey']+'/'+source_row['candidate']['entry']['modelId'];assert source_key==plan['canonicalSourceKey']
 resources=sorted(['building:'+u for u in uids]+['native-model:'+source_key,'source-context:'+BATCH+'-capture']);assert resources==plan['supervisedResources'];assert 'source-context:'+BATCH not in resources
 rows=json.loads(json.dumps(state(uids),allow_nan=False));return dict(uids=uids,rows=rows,observedProtectedReviewRecords=len(rows),reviewCountNotInventedOrTransferred=True,currentManifest=ref(manifest),sourcePointer=ref(pointer),dependencies=dependencies,suppressed=suppressed,completeCurrentCatalogueRefs=catalogue_refs,completeNativeSurvivalInventory=survival,globalSuppressionInventory=global_suppressors,sourceAcquisitionSelection=ref(Q.SEL),sourceKey=source_key,resources=resources,plan=ref(PROPOSAL/'wiring-plan.json'))

def fence(a,before):
 now=inputs(a);assert now==before and reservations.owns(read(LEASE))
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();before=inputs(a)
 if a.preflight_only:print(json.dumps(dict(readOnlyCurrentStatePreflightPassed=True,canonicalActorCount=len(before['uids']),observedProtectedReviewRecords=len(before['rows']),uids=before['uids'],noWorker=True)));return
 if not a.owned:
  assert not LOCAL.exists()and not Q.D.exists();claim=reservations.claim('citywalk-native-interfaces-'+str(uuid.uuid4()),before['resources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
 assert reservations.owns(read(LEASE));save(LOCAL/'protected-state-before.json',before);save(LOCAL/'immutable-lease-at-start.json',read(LEASE));fence(a,before);assert reservations.heartbeat(read(LEASE))['ok']
 subprocess.run(['node',str(CLOSURE),str(CLOSURE_OUTPUT.relative_to(ROOT))],cwd=ROOT,check=True);fence(a,before)
 subprocess.run([sys.executable,str(Path(Q.__file__)),'--expected-manifest',a.expected_manifest],cwd=ROOT,check=True);fence(a,before)
 subprocess.run(['node',str(CLOSURE),str(CLOSURE_OUTPUT.relative_to(ROOT)),'--verify'],cwd=ROOT,check=True);fence(a,before)
 subprocess.run([sys.executable,str(FREEZER),'--expected-manifest',a.expected_manifest],cwd=ROOT,check=True);fence(a,before);print(json.dumps(dict(frozenDiagnosticComplete=True,noAcceptance=True)),flush=True)
if __name__=='__main__':main()
