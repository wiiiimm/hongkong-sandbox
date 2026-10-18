"""Source-only review of the Park Avenue podium's separately supplied tower regions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-park-podium-identity-review-v1-20261018';DOC=BASE/BATCH;UID='landsd/72277:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];names=['government-xl-olympian-two-park-podium-coverage-v1-20261018','government-xl-olympian-two-park-tower-identity-review-v1-20261018']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 identity=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018';proof=read(identity/'72277:0-identity.json')['proof'];row=next(x for x in read(identity/'selection.json.gz')['rows']if x['uid']==UID);coverage=read(BASE/names[0]/'coverage.json')
 assert proof['originalOwnership']['sourceGraphVerified']and proof['exactCurrentComponentRoute']['qualified']and proof['exactCurrentComponentRoute']['uid']==UID and proof['exactWholeCellCoverage']['covered']and proof['freshCurrentIdentity']['exactObjectAndCSUID']
 assert proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==row['triangles']==3364
 assert coverage['sourceSHA256']==proof['sourceSHA256']and coverage['assemblyCoverage']>.997 and coverage['remainingUncoveredM2']<10
 assert row['source']['building']in read(ROOT/'3d-viewer'/row['source']['tile'])['buildings'];assert digest((ROOT/row['candidate']['path']).read_bytes())==proof['sourceSHA256']
 review=dict(uid=UID,sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,identityReviewApproved=True,sourceIdentityReviewUsedAI=True,rawReasonsRetained=proof['reasons'],reviewBasis=['ROOT inspected complete original podium projection and five associated tower projections. The podium is a longitudinal strip aligned with the five original tower positions; current basic footprint includes wider tower regions supplied separately by those original assets.', 'Exact government CSUID/ObjectID/type route, source graph and complete geographic cell match this podium. All3364 original faces retained. Podium-only footprint coverage61.04% is not treated as complete assembly coverage: separate five tower originals account for1764.30m2 of1774.18m2 missing footprint, producing99.783% assembly coverage.', 'The five associated tower identities have separate exact-source approvals.100 previously flagged canonical tower contact points independently find lower contact surfaces in this exact podium. This is supporting identity context, not placement approval or permission to omit support checks.', 'Accept only this immutable source identity and metadata binding. Preserve the raw footprint/overlap failures.33 buried faces and all terrain/browser/placement checks remain unresolved; no geometry edits, no generic threshold change, no publication approval.'],placementReviewed=False,publicationApproved=False,installationApproved=False,modelGeometryChanges=0)
 save(DOC/'72277:0-review.json',review);refs.extend(ROOT/p for p in pins)
 out=module('park_podium_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-park-podium-identity-only-review-v1',list(set(refs)),dict(uids=[UID],identityOnlyApproved=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
