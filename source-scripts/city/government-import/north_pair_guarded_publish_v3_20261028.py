"""Lease-fenced entry point for the exact qualified North original pair.

No geometry edits, generic guard changes, old support reapproval or optimisation.
--prepare-only validates immutable evidence without claiming or publishing.
"""
import argparse,json,sys
from pathlib import Path
from contextlib import contextmanager
import north_pair_qualified_stage_v1_20261027 as stage
from run import ROOT,HERE,read,save,connect,reservations,dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_independent_atomic_contract_v1_20261027 import verify_existing_atomic_group
from north_pair_publisher_hooks_v1_20261027 import install
P=stage.P;SOURCES=stage.SOURCES;BASE=stage.BASE
BATCH=P+'original-installed-v3-20261028'

def exact_plan(plan,surface):
 assert set(plan)=={'areas','topLevelTerrainPatches'}and len(plan['areas'])==1
 area=plan['areas'][0];assert set(area)=={'area','catalogue','destination'}
 assert area['catalogue']==str((stage.STAGE/'catalogue.json').relative_to(ROOT))
 assert area['destination']=='city/data/official-models/'+stage.BATCH+'/catalogue.json'
 entries=plan['topLevelTerrainPatches'];assert len(entries)==3
 assert len({e['source']for e in entries})==3
 assert len({e['destination']for e in entries})==3
 for m in surface['members']:
  e=next(e for e in entries if e['source']==m['candidate']['path'])
  assert set(e)=={'source','sha256','destination','resolution','area','replaces','nativeReview'}
  assert e['sha256']==m['candidate']['sha256']and e['replaces']==m['replaces']
  assert e['destination']=='city/data/government-native-north-pair-'+m['member']+'-v1-20261027.json'
 return True

def evidence():
 refs={}
 for suffix in ['qualified-stage-v2','retained-terrain-review-v2','visual-qualification-v1','physical-source-review-v1','identity-revalidated-v1','three-member-surface-v2']:
  _,pins=authenticate(BASE/(P+suffix+'-20261027'))
  for path,sha in pins.items():
   assert path not in refs or refs[path]==sha;refs[path]=sha
 for path,sha in refs.items():assert stage.ref(ROOT/path)['sha256']==sha,path
 q=read(stage.DOC/'qualification.json');assert q['uids']==sorted(SOURCES)and q['sourceSHA256ByUid']==SOURCES
 assert all(q[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','visualAcceptance','privateStageQualified'])
 assert q['existingNativeReaccepted']is False and not q['publication']and q['sourceGeometryChanges']==q['sourcePoseChanges']==0
 surface=read(BASE/(P+'three-member-surface-v2-20261027')/'summary.json')
 assert stage.ref(ROOT/'3d-viewer/city/data/manifest.json')==surface['currentManifest']
 plan=read(stage.STAGE/'plan.json');exact_plan(plan,surface)
 originals={r['uid']:r['candidate']['entry']for r in read(BASE/(P+'three-member-runtime-v2-20261027')/'selection.json.gz')['rows']}
 cfg=read(stage.STAGE/'live-browser-config.json');assert len(cfg['availabilityOverlays'])==1;overlay=cfg['availabilityOverlays'][0]
 before=read(ROOT/'3d-viewer'/overlay['url']);after=read(ROOT/overlay['source']);uid=overlay['uid']
 old=next(m for m in before['models']if m['uid']==uid);new=next(m for m in after['models']if m['uid']==uid)
 models=read(stage.STAGE/'catalogue.json')['models']
 assert verify_existing_atomic_group(models,SOURCES,originals,dict.fromkeys(SOURCES),{uid:old},{uid:new})
 for m in models:
  assert all(m[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
  assert m['sourceFunctionalApplicability']==stage.ref(stage.DOC/'qualification.json')
  assert stage.ref(stage.STAGE/m['asset'])['sha256']==SOURCES[m['uid']]
 retained=read(BASE/(P+'three-member-neighbours-v2-20261027')/'summary.json')['requiredNativeUids'];assert len(retained)==len(set(retained))==67
 keys={'building:'+u for u in [*retained,*SOURCES]}
 keys.update('terrain:'+m['replaces']['url']for m in surface['members']);keys.add('terrain:city/data/terrain.json')
 assert len(keys)==73 and {'building:'+u for u in [*SOURCES,uid]}<=keys
 return keys,surface,overlay,originals

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--receipt');ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 assert not(a.prepare_only and a.apply)
 keys,surface,overlay,originals=evidence()
 if a.prepare_only:
  assert not a.receipt
  save(BASE/(P+'guarded-publisher-preflight-v2-20261027')/'summary.json',dict(uids=sorted(SOURCES),passed=True,resources=sorted(keys),stageReceipt=stage.ref(stage.DOC/'result.json'),publisher=stage.ref(Path(__file__)),publication=False))
  print(dict(preflightPassed=True,canonicalResources=len(keys),publication=False),flush=True);return
 assert a.receipt and not (BASE/BATCH/'installed-acceptance.json').exists()
 lease=read(Path(a.receipt))
 @contextmanager
 def fence():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
   live=reservations._current(db,lease);assert live and keys<=set(live['resources'])
   assert stage.ref(ROOT/'3d-viewer/city/data/manifest.json')==surface['currentManifest'];yield
 with fence():pass
 pub=module('north_exact_live_publisher',HERE.parent/'island-detail-integration/publish.py');install(pub,ROOT,surface,overlay,originals)
 pub.PUBLICATION_GUARD=fence;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/BATCH
 sys.argv=['publish.py',str((stage.STAGE/'plan.json').relative_to(ROOT))]+(['--apply']if a.apply else[]);pub.main()
if __name__=='__main__':main()
