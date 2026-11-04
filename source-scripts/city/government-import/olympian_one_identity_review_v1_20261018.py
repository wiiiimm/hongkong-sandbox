"""Exact original podium identity review, not physical or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-identity-review-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-next-twenty-original-identity-v1-20261018';UID='landsd/72354:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 folders=[SRC,BASE/'government-xl-olympian-one-original-views-v1-20261018',BASE/'government-xl-olympian-one-pacifica-extent-v1-20261018']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=next(r for r in read(SRC/'selection.json.gz')['rows']if r['uid']==UID);old=read(SRC/'72354:0/identity.json');proof=verify_files(row,read(SRC/'72354:0/context.json'),LOCAL/'identity')
 for k in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','freshCurrentIdentity','reasons']:assert proof[k]==old[k]
 assert proof['originalOwnership']['sourceGraphVerified'] and proof['exactCurrentComponentRoute']['qualified'] and proof['exactWholeCellCoverage']['covered'] and proof['geographicCell']['targetCoversWholeCell']
 assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
 scope=proof['originalOwnership']['fullProjection'];assert scope['unrelatedIntersectingForms']==0 and scope['sourceExcessCoveredByUnrelatedFormsM2']==0 and scope['targetCoveredBySourceProjection']>.997
 viewfolder=folders[1];images=[viewfolder/(n+'.png')for n in ['whole','whole-reverse','lower-front','lower-reverse']]+[folders[2]/'72354:0.png']
 review=dict(uid=UID,reviewer='Codex ROOT',reviewType='exact-original-podium-extent-identity',sourceSHA256=row['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],modelId=row['modelId'],sourceFaces=row['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],reviewBasis=['Exact original root B344151985202063C0 routes uniquely to government podium ObjectID72354 and CSUID3441519852P20060804; both original projection and recorded target contain its complete georef cell.','The complete31,046face projection covers99.7679139percent of the recorded footprint. Its long main outline, rounded ends and adjoining original Bank of China Centre align in complete solid source views. The14.1320556m maximum extension is a local north-end authored appendage outside the simpler footprint, not a shifted main building. Its exact faces and669.396018m2 total source excess remain retained.','No source excess overlaps an unrelated recorded form. The only overlying separate form is the same-parent Bank of China Centre, whose original source was independently recovered and passed identity. This establishes source assignment, not architectural function of each small appendage, legal ownership, physical support or collision acceptance.','This accepts only the exact-source maximum-extent identity reasons. No10m threshold, source geometry, source pose or footprint was changed. Changed source/form/world bytes require a fresh review.'],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
 save(DOC/'72354:0-review.json',review)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(HERE/n for n in ['exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','component_type_resolution.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 module('olympian_one_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-extent-identity-review',list(dict.fromkeys(refs)),dict(uids=[UID],identityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
