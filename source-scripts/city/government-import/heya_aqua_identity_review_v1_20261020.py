"""Source-specific identity review; all placement/publication gates remain separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-identity-review-v1-20261020';DOC=BASE/BATCH;IDENT=BASE/'government-xl-heya-aqua-identity-v1-20261020';CONTEXT=BASE/'government-xl-heya-aqua-source-context-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [IDENT,CONTEXT]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 proof=take(IDENT,IDENT/'identity.json');context=take(CONTEXT,CONTEXT/'summary.json');images=[]
 for name in ['identity-context.png','wall-context--55.png','wall-context-125.png']:
  p=CONTEXT/name;assert digest(p.read_bytes())==pins[CONTEXT][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 assert proof['reasons']==['current-target-does-not-cover-whole-georef-cell'];assert proof['originalOwnership']['sourceGraphVerified'];assert proof['originalOwnership']['originalRootName']=='B339412218501063C0';assert proof['exactCurrentComponentRoute']['qualified'];assert proof['geographicCell']['originalProjectionCoversWholeCell'] and proof['exactWholeCellCoverage']['covered']
 identity=proof['freshCurrentIdentity'];assert identity['exactObjectAndCSUID'] and identity['unrelatedIntersectingForms']==0;assert identity['targetCoveredBySourceProjection']>.99;assert identity['sourceExcessMaximumDistanceFromTargetM']<3.75;assert identity['sourceExcessCoveredByUnrelatedFormsM2']==0
 review=dict(uids=[proof['uid']],reviewer='Codex ROOT',reviewType='source-specific-footprint-notch-identity',sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawReasonsRetained=proof['reasons'],rawProof=proof,imagesActuallyInspected=images,sourceGeometryChanges=0,sourcePoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False,basis=[
 'The exact original graph B339412218501063C0 and encoded tower CSUID3394122185T20151008 route to current ObjectID184287. The original model covers the complete encoded one-metre cell. Its 19777 unchanged faces cover99.0047844percent of the recorded tower footprint; no unrelated form is overlapped.',
 'ROOT inspected the complete projection and enlarged cell diagram. The single failed target-cell rule is the one-metre box crossing the concave notch of the recorded footprint. It does not indicate a displaced tower: the long orientation, end outlines and successive recesses align throughout the source. Maximum source extension is3.749547975m, with187.4607 of190.5414m2excess covered by the same-parent installed podium.',
 'This accepts identity for these exact source/form bytes only. It does not change the whole-cell rule globally, alter the footprint, infer engineering support, or approve the remaining local wall seam. Full runtime/placement/browser/publication evidence remains necessary.' ])
 save(DOC/'review.json',review);module('heya_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-source-footprint-notch-identity-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
