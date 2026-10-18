"""Exact-source identity review for two Central Park towers and adjoining podium."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-remaining-identity-review-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=['government-xl-olympian-two-original-interface-review-v1-20261018','government-xl-olympian-two-fourteen-source-projection-context-v1-20261018']
UIDS=['landsd/269908:0','landsd/269839:0','landsd/239351:0']
BASIS={
UIDS[0]:['Complete original projection covers99.9528percent of the recorded Tower2 form. ROOT inspected the complete boundary plot and lower-original assembly view. The discrepancy follows projecting facade wings and recesses around the same central tower footprint, not a shifted main block.','The only foreign footprint is adjoining original podium239351:1.834220m2 of tower excess. Its original source has been recovered and bound; lack of shared OSM references is not a competing government ObjectID. No legal ownership or physical-clearance claim follows from this identity interpretation.'],
UIDS[1]:['Complete original projection covers99.8889percent of the recorded Tower3 form. ROOT inspected complete extension polygons and original assembly views: broad facade wings extend beyond the simpler recessed footprint. The10.367424m maximum extension remains recorded; no global10m threshold is changed.','The only foreign-footprint excess is1.832958m2 within adjoining original podium239351. All4446 original faces remain accounted for at the exact government root and unchanged pose. This is identity of the whole authored tower, not approval of collision/support or a fabricated smaller building.'],
UIDS[2]:['Complete original podium projection covers96.8138percent of its recorded form, with its principal outline and circular features aligned. ROOT inspected the entire outline and all2625 extension-face records. Repeated eastern extensions occupy the original Park Avenue tower locations; source recovery of five towers and podium72277 confirms this assembly context without modifying the underlying records.','The western strip and small boundary extensions remain explicit original-source polygons. Maximum extension10.385817m and1188.023398m2 classified foreign-footprint excess are preserved. The original source root, exact unique government identifiers, whole georef cell and predominant whole-outline alignment identify this podium; a different OSM parent for an overlying tower does not demonstrate a wrong source.','The architect photograph provides qualitative integrated podium/residential context only. It is not registered surveying, identification of each small facade detail, or evidence that interpenetrations are acceptable. Every source face is retained; podium physical/terrain/collision and neighbour acceptance remain open.']}

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018';oldpath=BASE/'government-xl-olympian-two-exact-identity-routes-v1-20261018';rows={x['uid']:x for x in read(selection/'selection.json.gz')['rows']};reviews=[]
 for uid in UIDS:
  row=rows[uid];old=read(oldpath/(uid.split('/')[1]+'-identity.json'));context=read(selection/(uid.split('/')[1]+'-identity.json'))['context'];proof=verify_files(row,context,LOCAL/uid.split('/')[1])
  for key in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','freshCurrentIdentity','reasons']:assert proof[key]==old[key]
  assert proof['originalOwnership']['sourceGraphVerified']and proof['exactCurrentComponentRoute']['qualified']and proof['exactCurrentComponentRoute']['uid']==uid
  assert proof['exactWholeCellCoverage']['covered']and proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==row['triangles']and proof['geographicCell']['targetCoversWholeCell']
  expected={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
  if uid!=UIDS[0]:expected|={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
  assert set(proof['reasons'])==expected
  review=dict(uid=uid,sourceSHA256=row['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],modelId=row['modelId'],sourceFaces=row['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],reviewBasis=BASIS[uid]+['Exact-source identity only. Changed source/form/world inputs require fresh review. No geometry edits, scaling, coordinate fit, actor suppression, generic threshold change or placement/publication approval.'],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False,fullAcceptance=False)
  save(DOC/(uid.split('/')[1]+'-review.json'),review);reviews.append(review);print(dict(uid=uid,identityOnlyApproved=True),flush=True)
 save(DOC/'summary.json',dict(rows=reviews,fullAcceptance=False,newlyInstalled=0));refs.extend(ROOT/p for p in pins);refs.extend(HERE/n for n in ['exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','component_type_resolution.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('olympian_identity_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-olympian-original-assembly-identity-reviews-v1',list(set(refs)),dict(uids=UIDS,identityAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
