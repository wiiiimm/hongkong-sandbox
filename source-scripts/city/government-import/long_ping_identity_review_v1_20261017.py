"""Exact-source Long Ping identity review; all physical/publication gates remain independent."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';UID='landsd/107382:0';SHA='f462a97834afe39e5f66932c562eaa1daa4fa9f6958d5879663d1878b4251add';MODEL='B207143425301063C0';CSUID='2071434253T20050430'
PHYSICAL=BASE/'government-xl-long-ping-current-physical-v1-20261017';EXTENT=BASE/'government-xl-long-ping-extent-account-v1-20261017';PRIMARY=BASE/'government-xl-long-ping-primary-review-v1-20261017';BATCH='government-xl-long-ping-reviewed-identity-v1-20261017';DOC=BASE/BATCH
EXPECTED={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYSICAL,EXTENT,PRIMARY]:
   p=folder/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PHYSICAL/'selection.json.gz')['rows'][0];proof=read(PHYSICAL/'identity-proof.json');b=row['source']['building'];native=row['native'];account=read(EXTENT/'account.json')
 assert row['uid']==UID and row['sourceSHA256']==SHA and row['modelId']==MODEL and b['objectId']==107382 and b['buildingCSUID']==CSUID
 assert proof['sourceSHA256']==SHA and proof['originalOwnership']['sourceGraphVerified'] and proof['originalOwnership']['originalRootName']==MODEL
 assert proof['exactCurrentComponentRoute']['qualified'] and proof['exactCurrentComponentRoute']['uid']==UID and proof['exactCurrentComponentRoute']['official']['objectId']==107382 and proof['exactCurrentComponentRoute']['official']['buildingCSUID']==CSUID
 assert set(proof['reasons'])==EXPECTED and proof['freshCurrentIdentity']['exactObjectAndCSUID']
 assert b in read(ROOT/'3d-viewer'/row['source']['tile'])['buildings']
 assert digest((ROOT/row['candidate']['path']).read_bytes())==SHA
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,native['cacheKey'])).fetchone()==(native['resultSha'],)
 foreign=[f for f in proof['freshCurrentIdentity']['intersectingForms']if f['uid']!=UID];assert len(foreign)==1 and foreign[0]['uid']=='way/227090446:0'
 assert account['allSourceFaces']==15538 and account['nominatedFaces']==408 and account['remainingFaces']==15130 and account['maximumRemainingVertexDistanceM']<=10
 north=[];west=[]
 for component in account['components']:
  bounds=np.asarray(component['wholeFaceBounds'])
  if bounds[1,2]<-17765:north.append(component)
  elif bounds[0,0]<-14020 and bounds[0,2]>-17744:west.append(component)
  else:raise AssertionError('Unreviewed extent component')
 assert sum(x['faceCount']for x in north)==370 and sum(x['faceCount']for x in west)==38 and len(north)+len(west)==len(account['components'])
 decision=dict(uid=UID,modelId=MODEL,sourceSHA256=SHA,governmentBuildingCSUID=CSUID,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawIdentityProof=proof,rawWarningsRetained=True,scopedResolvedReasons=sorted(EXPECTED),reviewScope='Exact complete unchanged government Long Ping station source identity only',componentAccount=dict(northAccessFaces=370,westernAccessFaces=38,remainingOriginalFaces=15130),reviewBasis=['Verified original FME root B207143425301063C0 and exact dated government Tower CSUID 2071434253T20050430 route uniquely to current station ObjectID 107382. All 15,538 original faces and source bytes are retained.','The complete source covers 99.97926572386363% of the recorded station footprint. That footprint is a narrow platform rectangle, while official MTR station layout and street map explicitly include projecting concourse/access circulation.','Root inspected the unchanged source in plan and two oblique views. All 370 nominated north-side faces belong to the stair/access structure, its roof and supports. The sole overlapping OSM structure occupies this same north-side station-access position, consistent with the Exit A side on the official MTR street map; it does not establish a different identity for the original station.','All 38 other nominated faces are in the original elevated south-west station access corridor. Its outer corner reaches 11.15033016673245 m from the platform footprint. Root inspected this complete nominated component and its connection to the station; MTR layout corroborates extended station access circulation. No exact exit label is needed for this source identity decision.','All other 15,130 original faces are within 8.936235083524206 m of the unchanged footprint. This is a bounded whole-source architectural identification, not an increased global distance threshold or deletion of excess geometry.','Railway protection-area inclusion is not used as ownership proof. No OSM actor is suppressed or reparented, and current physical/terrain/foreign-model collision checks remain mandatory.'],placementReviewed=False,publicationApproved=False,foreignActorSuppressionApproved=False,aiGeometryModelling=False)
 save(DOC/'identity-review.json',decision);(DOC/'ROOT-REVIEW.md').write_text('# Long Ping exact original source identity\n\n'+'\n\n'.join(decision['reviewBasis'])+'\n\nIdentity only. Current terrain fails 42 buried source faces; authenticated government terrain is a repair candidate, not an installed solution. All original contact, complete affected-neighbour, runtime and browser requirements remain.\n')
 refs.extend([EXTENT/'account.json',EXTENT/'complete-extent-account.png',PHYSICAL/'north-extension-original.png',PHYSICAL/'identity-proof.json'])
 out=module('long_ping_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-exact-original-long-ping-identity-v1',list(dict.fromkeys(refs)),dict(uids=[UID],sourceSHA256=SHA,identityAccepted=True,sourceIdentityReviewUsedAI=True,identityProof=decision['identityProof'],fullAcceptance=False,nextStep='Construct bounded authenticated source-terrain candidate; test complete changed extent and all neighbours, contacts, foundation, runtime and browser before any publication.'))
 print(dict(jobId=out['jobId'],identityAccepted=True),flush=True)
if __name__=='__main__':main()
