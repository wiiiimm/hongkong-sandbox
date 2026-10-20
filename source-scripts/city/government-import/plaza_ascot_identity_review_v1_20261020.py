"""Exact-source identity interpretation only; collision and placement remain separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-identity-review-v1-20261020';DOC=BASE/BATCH
NAMES=['identity','identity-imagery','extent-context','component-census','adjacent-original-recovery']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   d=BASE/f'government-xl-plaza-ascot-{n}-v1-20261020';r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[n]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(n,name):
  p=BASE/f'government-xl-plaza-ascot-{n}-v1-20261020'/name;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 proof=take('identity','identity.json');assert proof['originalOwnership']['sourceGraphVerified']and proof['exactCurrentComponentRoute']['qualified']and proof['exactWholeCellCoverage']['covered']and proof['geographicCell']['targetCoversWholeCell']
 f=proof['freshCurrentIdentity'];assert f['exactObjectAndCSUID']and f['targetCoveredBySourceProjection']>.9969
 raw={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'};assert set(proof['reasons'])==raw
 extent=take('extent-context','summary.json')['rows'][0];assert extent['facesWithVertexBeyond10m']==149 and extent['maximumDistanceM']<17.225
 census=take('component-census','census.json');recovery=take('adjacent-original-recovery','recovery.json');assert {r['uid']for r in recovery['rows']}=={'landsd/258411:0','landsd/228446:0','landsd/127447:0'}
 for r in recovery['rows']:
  p=ROOT/r['assetPath'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
 images=[]
 for n,name in [('identity-imagery','258411:0.png'),('extent-context','258411:0-extent.png')]:
  p=BASE/f'government-xl-plaza-ascot-{n}-v1-20261020'/name;h=digest(p.read_bytes());assert h==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=h))
 provenance=take('identity-imagery','provenance.json')
 for tile in provenance['tiles']:
  p=ROOT/tile['path'];assert digest(p.read_bytes())==tile['sha256'];refs.append(p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==proof['exactRouteManifestSHA256'];refs.append(manifest)
 for t,h in proof['exactRouteTileHashes'].items():
  p=ROOT/'3d-viewer'/t;assert digest(p.read_bytes())==h;refs.append(p)
 review=dict(uids=['landsd/258411:0'],uid='landsd/258411:0',reviewer='Codex ROOT',sourceSHA256=proof['sourceSHA256'],sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],identityReviewApproved=True,identityOnlyApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawReasonsRetained=proof['reasons'],rawIdentity=proof,imagesActuallyInspected=images,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReviewed=False,publicationApproved=False,installationApproved=False,basis=[
 'Exact original source graph and qualified ObjectID/CSUID/georef-cell route identify this unchanged complete source as Plaza Ascot. Full original projection covers 99.6901 percent of the recorded podium footprint.',
 'ROOT inspected the official aerial overlay and full-source extent plot. Without fitting, shifting or scaling, the long podium envelope and small southwestern perimeter extension align with the built complex. The raw footprint extent warning concerns a local perimeter extension, not a displaced whole building. Aerial capture date is unknown and pixels do not prove all small surfaces.',
 'The four different-parent footprint overlaps remain fully recorded. Two are adjoining Plaza Ascot sources recovered with exact original hashes; a small 336368 overlap lies above its recorded roof. The 251951 component is inside the source projection. These intersections do not change the exact source identity. Neither same-name grouping nor this identity approval clears their physical overlap or suppresses any neighbour.',
 'This approves identity only for the pinned complete source. Full source contact, compound foundation where applicable, affected neighbours, terrain boundaries, runtime and publication gates remain required. No raw failure or acceptance threshold is erased.' ])
 save(DOC/'review.json',review);module('ascot_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-identity-only-interpretation',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
