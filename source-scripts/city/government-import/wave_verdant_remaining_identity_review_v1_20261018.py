"""Exact source-specific remaining assembly identities; physical gates remain separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-remaining-reviewed-identities-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=['government-xl-wave-verdant-identity-routes-v1-20261018','government-xl-wave301562-primary-plan-context-v1-20261018']
EXPECTED={
 'landsd/304885:0':dict(sha='448a02ec87fa8e83212a654f9734de7e2681b5ab90747fc1d0129664c411eed1',modelId='B161672662302062G0',reasons={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'},basis=[
 'ROOT inspected the complete source/footprint projection and staged production day render. The original is the same podium under the two Verdant blocks, following the curved site perimeter with boundary recesses. Exact IDs, source root, unique current whole-map route and whole one-metre GeoRef cell independently agree.',
 'Full source projection is3038.343752m2 with2993.286179m2 inside the3198.126591m2 recorded form. The204.840412m2 target deficit is almost entirely boundary recesses, not an omitted internal courtyard or evidence of a differently located object.98.5170percent of the original projection lies inside the target. These complete measurements explain the failure; no generic coverage limit is changed.',
 'Cached centroid distance0.118080m is not used to clear identity: complete original geometry gives1.426959m. The complete root-owned podium geometry and outline correspondence identify this exact source despite that basic-form difference. All deficit/excess polygons and both centroid values remain recorded.']),
 'landsd/301562:0':dict(sha='8326b663b61047b8728c2fa49550b0ab26b48868a05b8b2588db33004acf1959',modelId='B161752669001062G0',reasons={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'},basis=[
 'All144 original faces belong to the exact named root B161752669001062G0, with unchanged pose, exact government IDs and unique fresh whole-map route. Both original and recorded form contain the whole one-metre GeoRef cell. The original covers99.5361percent of the recorded main block; the discrepancy is an attached tapered extension, not a shifted main block.',
 'ROOT inspected complete source/form projection and complete rotated assembly source plan against developer brochure PDFpage20/printed18. The plan places the ground-floor service/refuse/filtration strip at the end of Tower2 beside the carpark ramp, corresponding qualitatively to this source. The diagram rotation is not surveyed registration, and the original remains unnamed; no invented precise room identity is assigned.',
 'All44.663451m2 of extension beyond the basic footprint is covered in projection by other original assembly geometry; the only footprint classified unrelated is podium301560. That classification comes from absent parent/OSM association, not a conflicting government ObjectID. Source ownership and the service-strip context identify the authored extension. This does not prove legal/common ownership, support or clearance.',
 'The14.733880m extension and4.691395m fresh centroid offset remain raw evidence. This exact-source identity decision changes no universal extent threshold and does not resolve any of the17 original support failures.'])}

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 sources={}
 for name in ['government-xl-wave-all-original-support-distance-v1-20261017','government-xl-wave-verdant-podium-support-v1-20261017']:
  p=BASE/name/'support-inputs.json';refs.append(p);sources.update({x['uid']:x for x in read(p)['sources']})
 contexts=read(BASE/'government-xl-wave-verdant-current-identity-runtime-v1-20261018/identity-context.json');routes=read(BASE/NAMES[0]/'summary.json')['rows'];decisions=[]
 for uid,spec in EXPECTED.items():
  row=sources[uid];assert row['sourceSHA256']==spec['sha'] and row['native']['model']['modelId']==spec['modelId'];row.update(modelId=spec['modelId'],triangles=row['native']['model']['triangles']);identity=next(x['identity']for x in contexts['rows']if x['uid']==uid);context=dict(sourceSHA256=row['sourceSHA256'],identity=identity,neighbourTileHashes=contexts['neighbourTileHashes']);raw=verify_files(row,context,LOCAL/uid.replace('/','-').replace(':','-'));old=read(BASE/'government-xl-wave-verdant-authoritative-identity-v1-20261018'/(uid.replace('/','-').replace(':','-')+'-identity.json'))
  for key in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','freshCurrentIdentity']:assert raw[key]==old[key]
  assert set(raw['reasons'])==spec['reasons'];assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid']==uid
  assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==row['triangles'] and raw['geographicCell']['targetCoversWholeCell'];metrics=next(x for x in routes if x['uid']==uid);assert metrics['exactUniqueIdentifiers'] and not metrics['graphReasons']
  decision=dict(uid=uid,sourceSHA256=row['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],modelId=row['modelId'],sourceFaces=row['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=raw,rawReasonsRetained=raw['reasons'],reviewBasis=spec['basis']+['Identity only for these exact source/form/world tuples. Changed evidence requires a fresh review. No geometry edits, coordinate fitting, neighbour suppression or support/terrain/foundation/collision/runtime/publication exemption.'],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False,fullAcceptance=False)
  save(DOC/(uid.replace('/','-').replace(':','-')+'-review.json'),decision);decisions.append(decision);print(dict(uid=uid,identityOnlyApproved=True,faces=row['triangles']),flush=True)
 save(DOC/'summary.json',dict(rows=decisions,fullAcceptance=False,newlyInstalled=0));refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'component_type_resolution.py',*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('assembly_remaining_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-two-original-assembly-identities-v1',list(set(refs)),dict(uids=list(EXPECTED),identityAccepted=True,sourceIdentityReviewUsedAI=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
