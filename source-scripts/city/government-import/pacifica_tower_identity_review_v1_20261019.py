"""ROOT identity-only review for exact Pacifica tower sources; no installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-tower-identity-review-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PAIR=BASE/'government-xl-pacifica-original-assembly-v1-20261019';TOWERS=BASE/'government-xl-pacifica-original-towers-v2-20261019';EXTENT=BASE/'government-xl-pacifica-tower-identity-extent-v1-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];folders=[PAIR,TOWERS,EXTENT]+[BASE/f'government-xl-pacifica-{uid}-identity-views-v1-20261019'for uid in ['79250','77278']]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows={r['uid']:r for r in read(PAIR/'selection.json.gz')['rows']};summaries=[]
 for key in ['79250:0','77278:0']:
  uid='landsd/'+key;r=rows[uid];old=read(PAIR/(key+'-identity.json'));proof=verify_files(r,read(TOWERS/(key+'-context.json')),LOCAL/key)
  for k in ['sourceSHA256','sourceFormSHA256','worldTrianglesSHA256','freshCurrentIdentity','reasons']:assert proof[k]==old[k]
  assert proof['originalOwnership']['sourceGraphVerified'] and proof['exactCurrentComponentRoute']['qualified'] and proof['exactWholeCellCoverage']['covered'] and proof['geographicCell']['targetCoversWholeCell']
  projection=proof['originalOwnership']['fullProjection'];assert projection['exactObjectAndCSUID'];view=BASE/f'government-xl-pacifica-{key.split(":")[0]}-identity-views-v1-20261019';images=[view/(n+'.png')for n in ['whole','lower-front','lower-reverse']]+[EXTENT/(key+'.png')]
  if key=='79250:0':
   assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
   assert projection['targetCoveredBySourceProjection']>.99999 and projection['unrelatedIntersectingForms']==0 and projection['sourceExcessCoveredByUnrelatedFormsM2']<.003
   assert 14.3987<projection['sourceExcessMaximumDistanceFromTargetM']<14.3988
   basis=['Exact original model root, ObjectID79250 and CSUID route identify this tower uniquely; whole source and footprint georef-cell checks remain valid.','Full source views align the tall cross-shaped tower with its recorded footprint. The additional curved lower component is authored within the same immutable source graph and lies over the same-parent podium; it is not a translation or another tower.','The full source covers99.9999947percent of the footprint. The14.398708m extension comes from the lower curved component; this review resolves only the generic maximum-extent reasons for this exact source/form/world revision.']
  else:
   assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
   others=[f for f in projection['intersectingForms']if f['uid']!=uid and not f['sameParent'] and not f['sharedOsmReference']];assert len(others)==1 and others[0]['uid']=='landsd/283036:0' and others[0]['structureType']=='Podium'
   assert projection['targetCoveredBySourceProjection']>.986 and projection['sourceExcessMaximumDistanceFromTargetM']<3.173
   basis=['Exact original model root, ObjectID77278 and CSUID route identify this tower uniquely; whole source and footprint georef-cell checks remain valid.','The complete tower aligns with the cross-shaped recorded Tower5 footprint. Its sole non-shared-reference intersecting form is the exact Pacifica podium283036 in this source assembly; the other podium265478 already shares an OSM reference.','The56.623161m2 unrelated-excess label reflects separate podium/tower footprint metadata, not evidence of a different building identity. The original low facade projections and the podium occupy the same intended assembly in the inspected source views. This resolves only these two identity-overlap reasons, not physical support, source-source collision or publication.']
  review=dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-original-tower-identity',sourceSHA256=r['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],modelId=r['modelId'],sourceFaces=r['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=proof,rawReasonsRetained=proof['reasons'],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],reviewBasis=basis,qualification='Exact hashes and source form only. No geometry, pose, footprint or generic threshold changed. Physical, collision, viewer and publication acceptance remain independent.',sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
  save(DOC/(key+'-review.json'),review);summaries.append(dict(uid=uid,identityAccepted=True,installationApproved=False));print(summaries[-1],flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(HERE/n for n in ['exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','component_type_resolution.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());module('pacifica_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-exact-original-tower-identity-reviews',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in summaries],rows=summaries,installationApproved=False))
if __name__=='__main__':main()
