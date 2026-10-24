"""Source-specific identity interpretation; no physical or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-source-identity-review-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name):
  folder=BASE/batch;_,pins=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return p
 identity=read(take('government-xl-grand-aquarium-repaired-boundary-identity-v1-20261022','93424:0/identity.json'));assert identity['sourceSHA256']=='359aa68b0df2051cc81cc5a8c79189b08715d07e6163307231d20127be1d6b30'
 assert identity['originalOwnership']['sourceGraphVerified']and identity['exactCurrentComponentRoute']['qualified']and identity['exactWholeCellCoverage']['covered']
 c=identity['freshCurrentIdentity'];assert c['exactObjectAndCSUID']and c['target']['objectId']==93424 and c['target']['buildingCSUID']=='3603211884T20101011'
 raw={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'};assert set(identity['reasons'])==raw
 assert abs(c['targetCoveredBySourceProjection']-.9976274245403548)<1e-12
 other=[f for f in c['intersectingForms']if f['uid']!='landsd/93424:0'];assert len(other)==1 and other[0]['uid']=='landsd/295518:0'and other[0]['structureType']=='Podium'
 image=take('government-xl-grand-aquarium-identity-imagery-v1-20261022','93424:0.png');provenance=read(take('government-xl-grand-aquarium-identity-imagery-v1-20261022','provenance.json'))
 for tile in provenance['tiles']:
  p=ROOT/tile['path'];assert digest(p.read_bytes())==tile['sha256'];refs.append(p)
 for tile,sha in identity['exactRouteTileHashes'].items():
  p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==sha;refs.append(p)
 mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==identity['exactRouteManifestSHA256'];refs.append(mp)
 review=dict(uids=['landsd/93424:0'],uid='landsd/93424:0',reviewer='Codex ROOT',sourceSHA256=identity['sourceSHA256'],sourceFormSHA256=identity['sourceFormSHA256'],worldTrianglesSHA256=identity['worldTrianglesSHA256'],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,imagesActuallyInspected=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],identityReviewApproved=True,identityOnlyApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawReasonsRetained=identity['reasons'],rawSpatialContext=c,observations=[
 'Exact original graph ownership, unique current ObjectID/CSUID route and complete geographic cell bind this unchanged government asset to Grand Aquarium.',
 'ROOT inspected the official Lands Department aerial and unfitted complete-source overlay. The main rectangular roof envelope, circular skylight area and long curved eastern roof edge correspond to the photographed structure. This is not a displaced whole building.',
 'The complete source covers 99.76274245403548 percent of the current footprint. The source extends beyond that footprint, with a maximum distance of 15.889090712346635 metres and 689.7318649369201 square metres excess; these facts and the source outline remain unchanged. Aerial pixels do not prove ownership or ground support for every small northern extension.',
 'The only recorded different-parent intersection is 11.231685859390623 square metres over Ocean Square podium 295518. That intersection does not make this asset a different building. It remains an explicit physical overlap/terrain obligation, not cleared by this identity decision.'
 ],decision='Accept identity only for the exact complete original revision. Preserve automatic spatial failures. No placement, support, collision, terrain or publication approval is granted.',remainingRequirements=['Original source contact and partial terrain-intersection review','Physical Ocean Square overlap and all retained neighbour obligations','Current desktop/mobile browser and guarded publication checks'],installationApproved=False,placementReviewed=False,publicationApproved=False,sourceGeometryChanges=0)
 save(doc/'ROOT-IDENTITY-REVIEW.json',review);module('aquarium_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-identity-only-interpretation',refs,review)
if __name__=='__main__':main()
