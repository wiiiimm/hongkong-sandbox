"""Exact-source identity interpretation for five Park Avenue towers; no placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-park-tower-identity-review-v1-20261018';DOC=BASE/BATCH
IDENTITY=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018';PROJECTION=BASE/'government-xl-olympian-two-park-projection-context-v1-20261018';LAYERS=BASE/'government-xl-olympian-two-park-all-source-layers-v1-20261018'
UIDS=['landsd/79627:0','landsd/83600:0','landsd/79657:0','landsd/80122:0','landsd/83837:0']
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [IDENTITY,PROJECTION,LAYERS]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection={x['uid']:x for x in read(IDENTITY/'selection.json.gz')['rows']};reviews=[]
 for uid in UIDS:
  row=selection[uid];proof=read(IDENTITY/(uid.split('/')[1]+'-identity.json'))['proof'];f=proof['freshCurrentIdentity'];geo=read(PROJECTION/(uid.split('/')[1]+'-geometry.json.gz'))
  assert proof['originalOwnership']['sourceGraphVerified']and proof['exactCurrentComponentRoute']['qualified']and proof['exactCurrentComponentRoute']['uid']==uid
  assert proof['exactWholeCellCoverage']['covered']and proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==row['triangles']and f['exactObjectAndCSUID']
  assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
  assert f['targetCoveredBySourceProjection']>.997 and f['sourceExcessCoveredByUnrelatedFormsM2']<9 and f['sourceExcessMaximumDistanceFromTargetM']<5
  assert row['source']['building']in read(ROOT/'3d-viewer'/row['source']['tile'])['buildings'];assert digest((ROOT/row['candidate']['path']).read_bytes())==proof['sourceSHA256']
  for key in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:assert geo[key]==proof[key]
  review=dict(uid=uid,sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,identityReviewApproved=True,sourceIdentityReviewUsedAI=True,rawReasonsRetained=proof['reasons'],reviewBasis=['ROOT inspected the complete seven-panel original projection figure, including all five tower outlines. Each original matches its unique tower footprint orientation and distinctive repeated plan; recess-filling wings and eastern facade projections are preserved.', 'Exact government source graph, CSUID/ObjectID component route and whole georeference cell match this tower. Measured original coverage of its target exceeds 99.7%; foreign-form excess is individually below 9 square metres. These figures describe these five exact sources and are not general acceptance thresholds.', 'The recorded podium-form overlaps and all original extension faces remain in evidence. Other-original projection coverage is contextual only; no blanket overlap permission, engineering claim, tower-to-tower support credit or geometry alteration.', 'Source identity only. Complete support, buried-face treatment, terrain, neighbour, device/browser and publication checks remain required.'],placementReviewed=False,publicationApproved=False,installationApproved=False,modelGeometryChanges=0)
  save(DOC/(uid.split('/')[1]+'-review.json'),review);reviews.append(review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'summary.json',dict(rows=reviews,fullAcceptance=False,newlyInstalled=0));refs.extend(ROOT/p for p in pins)
 out=module('park_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-five-park-tower-identity-only-review-v1',list(set(refs)),dict(uids=UIDS,identityOnlyApproved=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
