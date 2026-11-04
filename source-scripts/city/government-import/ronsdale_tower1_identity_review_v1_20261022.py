"""Scope Block 1 identity to the two unchanged original government components."""
from pathlib import Path
import copy,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-tower1-identity-review-v1-20261022';DOC=BASE/BATCH
UID='landsd/256898:0';POD='landsd/233771:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-ronsdale-tower1-assembly-coverage-v1-20261022';coverage=take(n,BASE/n/'coverage.json');old=take('government-xl-remaining-forty-original-identity-v2-20261021',BASE/'government-xl-remaining-forty-original-identity-v2-20261021/256898:0/identity.json');podium=take('government-xl-remaining-forty-podium-identity-v1-20261021',BASE/'government-xl-remaining-forty-podium-identity-v1-20261021/233771:0/identity.json')
 assert old['sourceSHA256']==coverage['towerSourceSHA256'] and podium['sourceSHA256']==coverage['podiumSourceSHA256'];assert podium['passed'] and not podium['reasons']
 assert old['reasons']==['fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'] and old['originalOwnership']['sourceGraphVerified']
 route=old['exactCurrentComponentRoute'];target=old['freshCurrentIdentity']['target'];assert route['qualified'] and not route['reasons']
 assert route['official']['objectId']==target['objectId']==256898 and route['official']['buildingCSUID']==target['buildingCSUID']=='3818515100T20050430'
 assert route['official']['sourceBaseHeight']==target['base']==107.1 and route['official']['sourceTopHeight']==target['base']+target['height']==202.7
 assert old['geographicCell']['originalProjectionCoversWholeCell'] and old['geographicCell']['targetCoversWholeCell']
 assert old['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2']==0
 for record in [old,podium]:
  for path,h in record['exactRouteTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==h;refs.append(ROOT/'3d-viewer'/path)
 n='government-xl-ronsdale-regional-scope-v1-20261022';forms=take(n,BASE/n/'form-obligations.json.gz');towerform=next(r for r in forms if r['uid']==UID);podform=next(r for r in forms if r['uid']==POD);assert towerform['parent']==podform['parent'] and set(towerform['osmRefs'])&set(podform['osmRefs'])
 targetpoly=shapely.from_wkt(coverage['targetWKT']);missing=shapely.from_wkt(coverage['missingWKT']);towerpoly=shapely.from_wkt(coverage['towerProjectionWKT'])
 assert missing.difference(targetpoly.boundary.buffer(1.5)).area<1e-8
 assert missing.difference(towerpoly.buffer(1.5)).area<1e-8
 assert coverage['compoundCoveredFraction']>=.98 and coverage['remainingMissingAreaM2']<8
 image=BASE/'government-xl-ronsdale-tower1-assembly-coverage-v1-20261022/coverage.png';assert digest(image.read_bytes())==cache['government-xl-ronsdale-tower1-assembly-coverage-v1-20261022'][str(image.relative_to(ROOT))];refs.append(image)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 identity=copy.deepcopy(old);identity.update(passed=True,reasons=[],proof=dict(exactBuildingCSUID=True,exactObjectId=True,uniqueViewerMatch=True,identityAccepted=True,detailedProjectionAccepted=True),policy='source-specific-original-two-component-identity-review-v1',rawIndividualIdentityReasons=old['reasons'],sourceSpecificCompoundIdentityAccepted=True,requiredSourceSHA256ByUid={UID:old['sourceSHA256'],POD:podium['sourceSHA256']},standalonePublicationApproved=False,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,currentManifestSHA256=digest(manifest.read_bytes()),imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],compoundCoveredFraction=coverage['compoundCoveredFraction'],boundaryDiscrepancyLimitMetres=1.5,qualification='Identity acceptance requires BOTH exact original government components in one accepted assembly. Exact official ObjectID/CSUID/type/base/top route and complete geographic cell match. Inspected distinctive footprint agrees in position/orientation; all individual-tower missing projection lies within1.5m of its own source and recorded boundary, with no missing interior wing. The original podium covers35.8568m2 of43.3011m2 missing tower projection; the unchanged compound covers98.7724% of the recorded target. Raw individual92.8593%coverage failures remain recorded. No generic identity threshold, geometry, pose or scale change. All physical/support/neighbour/runtime/browser/publication gates remain required.')
 save(DOC/'identity.json',identity);module('ronsdale_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'scoped-original-two-component-identity-review',refs,dict(uids=[UID,POD],identity=identity,installationApproved=False));print(dict(uid=UID,identityAcceptedWithOriginalPodium=True,compoundCoveredFraction=coverage['compoundCoveredFraction']),flush=True)
if __name__=='__main__':main()
