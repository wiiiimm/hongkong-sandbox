"""DRAFT exact Heya rollback recovery; historical proof is not current credit.
No generic signature aliases; only ROOT's three named actual byte archives.
All other completed refs remain literal raw-file SHA checks. No review writes.
"""
import json
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from government_owned_identity import verify_files
from heya_aqua_complete_current_role_fixture_20261011 import FOLDERS,load
from heya_aqua_complete_current_role_policy_v2_20261011 import compose,CURRENT,T,P
BASE=ROOT/'docs/astra-city/government-import'
ROLE=BASE/'government-xl-heya-aqua-whole-current-role-acceptance-v2-20261011'
OLD=BASE/'government-xl-heya-aqua-184286-unchanged-installed-v1-20261011'
HISTORY=BASE/'government-xl-heya-before-installation-current-history-v1-20261011/root-actual-historical-input-contract.json'
HISTORY_SHA='27e12065a1de099b3d9d6530dc05d5e73462655d16622a309bb050292dae2589'
SOURCE_CERT=BASE/'government-xl-heya-aqua-current-complete-source-root-closure-v1-20261011/root-closed-scope.json'
ENTRY_APPROVAL=BASE/'government-xl-heya-aqua-recovery-factual-entry-root-approval-v2-20261011/root-approved-entry-metadata.json'
ORPHAN='fdab0ed5aee2a9cc';PREVIOUS='87728085a588c731'
SHA='f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155'
CHANGE={'sourceIdentityReviewed':True,'publicationApproved':True,'priority':'approved-unchanged-original-root-reviewed'}
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def historical_refs():
 assert digest(HISTORY.read_bytes())==HISTORY_SHA
 h=read(HISTORY);assert h['historicalOnly']and not h['currentAcceptanceAfterSceneChange']and not h['hashAliasesOrSignatureOverrides']and h['manifestBeforeSHA256']==CURRENT
 expected={'3d-viewer/city/data/manifest.json':CURRENT,'docs/astra-city/model-integration-20260909/current-source-review.json':'16bac8df5edc4bf370340bc9444c09c730445e86022a53b2b340751ba8faef57','3d-viewer/city/data/building-progress.json':'ce6631c4035120fc2ae83fd3aba79ffaa3e103c11440aa2946151dda0a7838bd'}
 aliases={}
 assert len(h['actualHistoricalBytes'])==3
 for a in h['actualHistoricalBytes']:
  old=a['actualPreInstallationInput'];archive=a['unmodifiedHistoricalBytes']
  assert expected[old['path']]==old['sha256']==archive['sha256']
  assert archive['path']=='docs/astra-city/government-import/government-xl-heya-before-installation-current-history-v1-20261011/actual-bytes/'+old['path']
  assert ref(ROOT/archive['path'])==archive and old['path']not in aliases
  aliases[old['path']]=(old,archive)
 assert set(aliases)==set(expected);return aliases

def verify_historical_completed_receipt():
 receipt=read(ROLE/'result.json');aliases=historical_refs();resolved=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert receipt['jobId']=='c10465ffe57139f01eeb4dfa17a3ed8ff2c519e1d702f11e27676f6a80c95729'and len(receipt['evidenceRefs'])==7603
 for p in receipt['evidenceRefs']:
  if p['path']in aliases:
   old,archive=aliases[p['path']];assert p==old;resolved.append(dict(historicalInput=p,actualArchivedBytes=archive))
  else:assert ref(ROOT/p['path'])==p
 return dict(completedReceipt=ref(ROLE/'result.json'),historicalOnly=True,currentInstallationCredit=False,exactArchivedInputResolutions=resolved,ordinaryRawRefsVerified=7603-len(resolved))

def current_scene_and_history():
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==PREVIOUS
 rollback=read(OLD/'post-browser-failure-recovery.json');assert rollback['manifestRestoredSHA256']==CURRENT and rollback['rollbackErrors']==[]and rollback['pendingAndInstalledLedgerHistoryPreserved']and rollback['rootRecoveryAuditRequired']
 installed=read(OLD/'installed-acceptance.json');assert installed['snapshotId']==ORPHAN and installed['sourceSHA256s']=={T:SHA}
 entries=[m for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 assert len(entries)==len({m['uid']for m in entries})==6648 and not any(m['uid']==T for m in entries)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(PREVIOUS,T)).fetchall()==[]
  reviews=c.execute('SELECT snapshot_id,uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(ORPHAN,T)).fetchall()
  events=c.execute('SELECT id,snapshot_id,uid,review_state,result,request_id FROM astra_modelling.model_review_events WHERE snapshot_id=%s AND uid=%s ORDER BY id',(ORPHAN,T)).fetchall()
 assert len(reviews)==1 and reviews[0][:4]==(ORPHAN,T,'installed-verified',SHA)
 assert [(e[0],e[3])for e in events]==[(11942,'approved-for-integration'),(11943,'installed-verified')]
 for e in events:
  assert e[1]==ORPHAN and e[2]==T and e[4]['source_sha256']==SHA
  assert ref(ROOT/e[4]['evidence'])['sha256']==e[4]['sha256']
 assert reviews[0][4]==events[-1][4]
 return dict(currentManifestSHA256=CURRENT,currentSnapshotId=PREVIOUS,currentNativeActors=6648,orphanSnapshot=ORPHAN,orphanReviews=json.loads(json.dumps(reviews)),orphanEvents=json.loads(json.dumps(events)),currentInstallationCredit=False,historyPreserved=True,rollback=ref(OLD/'post-browser-failure-recovery.json'))

def augmented_entry(original,approval):
 assert approval['reviewer']=='ROOT'and approval['independentlyVerified']and approval['approvedMetadataChanges']==CHANGE
 assert approval['uid']==T and approval['sourceSHA256']==SHA and approval['manifestSHA256']==CURRENT and approval['snapshotId']==PREVIOUS
 assert approval['originalEntry']==ref(ROLE/'private-stage-entry.json')and approval['sourceRootCertificate']==ref(SOURCE_CERT)and approval['historicalContract']==ref(HISTORY)
 assert approval['geometryChanges']==approval['terrainChanges']==0 and not approval['currentInstallationCredit']
 assert original==read(ROLE/'private-stage-entry.json')and original['sha256']==SHA and original['uid']==T and original['placementReviewed']is True and original['publicationApproved']is False and 'sourceIdentityReviewed'not in original
 result={**deepcopy(original),**CHANGE};assert {k:v for k,v in result.items()if k not in CHANGE}=={k:v for k,v in original.items()if k not in CHANGE}
 return result

def recheck(local,*,require_entry_approval=True):
 historical=verify_historical_completed_receipt();current=current_scene_and_history()
 data=load();row=read(BASE/FOLDERS['identity']/'selection.json.gz')['rows'][0];context=read(BASE/FOLDERS['identity']/'context.json.gz')['rows'][0]
 fresh=verify_files(row,context,Path(local)/'unmocked-current-owned-identity');assert fresh==data['identity']and fresh['passed']
 role=json.loads(json.dumps(compose(**data)));assert role==read(ROLE/'complete-current-role.json.gz')and role['stagingReady']and role['scriptChecksPassed']and role['reasons']==[]and not role['installationApproved']
 support=read(BASE/FOLDERS['identity']/'installed-support-entry.json')
 assert ref(ROOT/support['catalogue']['path'])==support['catalogue']and ref(ROOT/support['asset']['path'])==support['asset']
 assert [m for m in read(ROOT/support['catalogue']['path'])['models']if m['uid']==P]==[support['entry']]
 cert=read(SOURCE_CERT);assert cert['reviewer']=='ROOT'and cert['independentlyVerified']and cert['candidateUid']==T and cert['sourceSHA256']==SHA and cert['completedReceipt']==ref(ROLE/'result.json')and cert['currentManifestSHA256']==CURRENT
 original=read(ROLE/'private-stage-entry.json')
 entry=augmented_entry(original,read(ENTRY_APPROVAL))if require_entry_approval else original
 save(Path(local)/'exact-recovery-recheck.json',dict(historicalProof=historical,currentScene=current,freshIdentity=fresh,roleSHA256=digest(json.dumps(role,sort_keys=True,separators=(',',':')).encode()),entryMetadataChanges=CHANGE if require_entry_approval else {},currentCredit=False))
 assert current_scene_and_history()==current
 verify_historical_completed_receipt()
 return role,entry,row
