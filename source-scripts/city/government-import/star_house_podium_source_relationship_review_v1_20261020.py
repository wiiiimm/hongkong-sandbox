"""Exact original podium ground relationship review; no numerical or publication waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-house-podium-source-relationship-review-v1-20261020';DOC=BASE/BATCH;UID='landsd/231484:0';SHA='2d2b63f0aedd4e57971f295e6aecc51f1c23e7c4e7c739b5a1085d4a0712761a'
folders={k:BASE/('government-xl-star-house-podium-'+k+'-20261020') for k in ['contact-faces-v1','ground-attribution-v1','identity-review-v1','neighbours-v1','loader-v1','source-views-v1','overlap-views-v1']};folders['foundations']=BASE/'government-xl-star-parkview-four-mode-foundations-v1-20261020';assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in folders.values():
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
identity=read(folders['identity-review-v1']/'231484:0-review.json');assert identity['identityOnlyApproved'] and identity['sourceSHA256']==SHA
face=read(folders['contact-faces-v1']/'faces.json');at=read(folders['ground-attribution-v1']/'attribution.json');assert face['sourceSHA256']==at['summary']['sourceSHA256']==SHA
ids=set(face['intersectingFaceIds']);matched=[r for r in at['faces'] if r['faceId'] in ids];assert len(matched)==len(ids)==70;assert all(min(r['originalGovernmentTerrainGaps'])<-.5 for r in matched);assert max(abs(r['normalYRatio']) for r in matched)<.019;assert not face['fullyBuriedFaceIds'];assert set(at['summary']['originalTerrainFullyBuriedIds'])=={2719,2720,3096}
bindings=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 f=read(folders['foundations']/('231484:0-'+mode+'.json'));assert f['uid']==UID and f['sourceSHA256']==SHA and f['strictFoundationAccepted'];assert f['foundation']['completeTerrainTriangles']==f['foundation']['triangles']==3260;assert f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0;bindings.append(dict(mode=mode,wholeWorldSHA256=f['worldSHA256'],strictFoundationAccepted=True))
n=read(folders['neighbours-v1']/'summary.json');assert not n['terrainChanged'] and n['maxGroundChange']==0 and not n['flagged'];v=read(folders['loader-v1']/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0
images=[folders['contact-faces-v1']/'contact-faces.png',folders['source-views-v1']/'complete-source-four-views.png',folders['overlap-views-v1']/'overlap-context.png']
decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',sourceTerrainRelationshipReviewed=True,originalSurveyedRelationshipAccepted=True,rawStrictTerrainIntersectionPassed=False,rawStrictFoundationPassed=True,checks=bindings,reviewedIntersectingFaceIds=sorted(ids),buriedFaceIds=[],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in images],basis=[
 'All70 current penetration faces already penetrate authenticated original government ground; every one is nearly vertical (maximum absolute normalY0.0186648332). ROOT inspected complete original and ground-overlay exports; flagged facets are lower perimeter walls rather than fully submerged roofs or an entire displaced source.',
 'Current ground is not identical to originalTIN: the173 flagged/rim comparisons differ by up to2.7436028m. Preserve this difference explicitly. OriginalTIN wholly buries three near-vertical faces2719/2720/3096; current ground buries none. Restoring originalTIN would not fix the numerical intersection warning.',
 'All3260 unchanged source faces pass complete foundation coverage in original/literal/left-F32/balanced-F32 modes with zero wholly buried faces. Current global lowrim remains within ordinary contact limits. No source vertices, source pose, thresholds or terrain were changed.',
 'The existing numerical penetration warning remains failed and recorded. This review accepts only the exact source-specific surveyed wall/ground relationship. It does not alter generic acceptance rules, resolve tower33396 support, approve neighbouring identity/suppression, or grant publication.',
 'Terrain regression is zero because no terrain is replaced. Neighbour geometry is retained. Staged and live browser visibility, picking, collision and recovery evidence remain mandatory; no cross-building collision clearance is inferred from unchanged terrain alone.'
],geometryOrPoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,installationApproved=False,publicationApproved=False,stagedAndLiveReviewRequired=True)
save(DOC/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json',decision)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('star_podium_relationship_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-ground-relationship-review',list(dict.fromkeys(refs)),dict(uids=[UID],originalSurveyedRelationshipAccepted=True,rawStrictTerrainIntersectionPassed=False,rawStrictFoundationPassed=True,installationApproved=False))
