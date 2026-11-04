"""Bounded source-association identity review; retain every spatial/physical hold.

This review identifies five exact government source units, not ownership of all
boundary projections or permission to install/suppress any neighbouring form.
"""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_source_assembly_diagnostic import COVERAGE_REASONS
BASE=ROOT/'docs/astra-city/government-import'
ASSEMBLY='government-xl-elegant-garden-complete-two-permit-assemblies-v1-20261028'
BOUNDARY='government-xl-elegant-garden-two-permit-boundary-allocation-v1-20261028'
PRIMARY='government-xl-elegant-garden-current-primary-records-v1-20261028'
CENSUS='government-xl-elegant-garden-complete-two-permit-records-v1-20261028'
CAP='government-xl-elegant-garden-seventeen-original-current-selection-v1-20261028'
EXPECTED={'H123/87':{'landsd/173532:0','landsd/173768:0','landsd/236170:0'},'H16/90':{'landsd/173764:0','landsd/228592:0'}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('exact-permit-source-identity-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 groups=take(ASSEMBLY,'summary.json')['rows'];boundaries={r['permit']:r for r in take(BOUNDARY,'summary.json')['rows']};members={r['permit']:r for r in take(CENSUS,'summary.json')['rows']}
 primary={r['csuid']:r for r in take(PRIMARY,'summary.json')['rows']};selection=take(CAP,'selection.json.gz');sources={r['uid']:r for r in selection['rows']};reviews=[]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 for group in groups:
  permit=group['permit'];assert set(group['uids'])==EXPECTED[permit]
  membership=members[permit];assert membership['allMembersHaveSelectedOriginals']and not membership['membersWithoutSelectedOriginals']and set(membership['selectedSourceUIDs'])==EXPECTED[permit]
  measures=group['measures'];assert measures['coverage']>.997 and measures['maximumExtentM']<5.27
  assert group['reasons']==['complete-permit-unrelated-excess-above-1m2'] and not group['assemblyLimitsPassed']
  allocation=boundaries[permit];assert allocation['totalUnrelatedUnionM2']==measures['unrelatedExcessM2']or abs(allocation['totalUnrelatedUnionM2']-measures['unrelatedExcessM2'])<1e-7
  image=ROOT/group['export']['path'];assert digest(image.read_bytes())==group['export']['sha256'];refs.append(image)
  for uid in group['uids']:
   raw=group['rawIndividualIdentity'][uid];source=sources[uid];b=source['source']['building'];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==raw['sourceSHA256'];refs.append(asset)
   assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']and raw['geographicCell']['targetCoversWholeCell']
   assert not set(raw['reasons'])-COVERAGE_REASONS and raw['freshCurrentIdentity']['exactObjectAndCSUID']
   official=primary[b['buildingCSUID']];assert official['uniqueOfficialRecord'];record=official['officialRecords'][0]
   assert record['Status']=='Active'and record['BuildingCSUID']==b['buildingCSUID']and record['BuildingBlockType']==b['structureType']
   assert record['BaseHeight']==b['base']and abs(record['TopHeight']-b['base']-b['height'])<1e-8
   review=dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-complete-permit-source-association-only',modelId=source['modelId'],sourceSHA256=raw['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],
    identityOnlyApproved=True,identityReviewApproved=True,sourceIdentityReviewed=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),
    completeOfficialPermit=permit,completeCSUIDs=membership['completeCSUIDs'],rawIdentityVerbatim=raw,rawReasonsRetained=raw['reasons'],rawAssemblyLimitsPassed=False,rawAssemblyReasons=group['reasons'],assemblyMeasures=measures,
    imagesActuallyInspected=[group['export']],boundaryObligations=allocation['actors'],requiresIndependentBoundaryPlacementReview=True,outsideAssemblySuppressionApproved=False,boundaryOwnershipApproved=False,
    sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,placementReviewed=False,physicalAccepted=False,publicationApproved=False,installationApproved=False,
    basis=[
     'The unchanged government root graph and unique typed component route bind this exact asset to its pinned viewer object/CSUID. The original and target cover the encoded full metre cell; no name/proximity substitution or current-OBJECTID rewrite is used.',
     'Fresh official active CSUID/type/base/top records and the complete occupation-permit structure/relation census identify every member, with no absent/unselected permit part. Complete original projections cover more than99.7percent of the verified member footprints. ROOT inspected the complete original assembly from above and two sides; the source units correspond to those member tower/podium arrangements.',
     'This accepts source association of these exact bytes/form only. It deliberately DOES NOT mark the failed1m² unrelated-overlap diagnostic passed, assign ownership of all boundary facets, approve the canopy as redundant, approve neighbour suppression, or clear placement. Every allocated original-facet/other-form overlap remains an explicit mandatory physical boundary obligation.',
     'The raw21.2597104m² Elegant Garden and2.7797416m² Rex projection excesses remain recorded. Identity approval cannot be substituted for complete current original/BASIC neighbour checks, source roles, collision, desktop/mobile or guarded publication evidence. Generic spatial/support limits are unchanged.'
    ])
   save(out/(uid.split('/')[1]+'-review.json'),review);reviews.append(dict(uid=uid,sourceSHA256=raw['sourceSHA256'],identityOnlyApproved=True,requiresIndependentBoundaryPlacementReview=True))
 result=dict(uids=sorted(r['uid']for r in reviews),rows=reviews,identityOnlyApproved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,placementReviewed=False,publicationApproved=False,installationApproved=False,
  qualification='Bounded source-association judgement for exactly the five original roots in the two complete official permits. No general identity/spatial rule changes. Raw failed proxies, other-form facet allocations and all placement/support/collision/visual/publication obligations remain mandatory and unapproved.')
 save(out/'summary.json',result);refs.append(HERE/'original_source_assembly_diagnostic.py');assert reservations.owns(lease)
 module('exact_permit_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-exact-official-permit-source-association-identity-review',list(dict.fromkeys(refs)),result)
 print(dict(sourceIdentitiesReviewed=len(reviews),placementApproved=False,newlyInstalled=0),flush=True)
if __name__=='__main__':main()
