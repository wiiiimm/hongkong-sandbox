"""Review the source-specific global-bottom warning without waiving foundation checks."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-source-relationship-review-v2-20261019';DOC=BASE/BATCH
UID='landsd/210032:0';SHA='a8635ec84493ea64fa8b803bc5ea6e90f1dcd46979674e9d6d24445067491de7'
def folder(name):return BASE/('government-xl-star-ferry-'+name+'-20261019')
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    for name in ['contact-faces-v2','all-contact-ground-attribution-v2','four-mode-foundations-v2','identity-review-v1','complete-neighbours-v3','ordinary-validation-v3']:
        q=folder(name)/'result.json';r=read(q)
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.append(q)
        for e in r['evidenceRefs']:
            assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
face=read(folder('contact-faces-v2')/'faces.json');attribution=read(folder('all-contact-ground-attribution-v2')/'attribution.json')
identity=read(folder('identity-review-v1')/'210032:0-review.json')
assert face['sourceSHA256']==attribution['summary']['sourceSHA256']==identity['sourceSHA256']==SHA
assert identity['identityOnlyApproved']
rim=set(face['lowRimFaceIds']);matched=[r for r in attribution['faces'] if r['faceId'] in rim]
assert len(matched)==len(rim)==4332 and all(r['maximumTerrainDifferenceMetres']==0 for r in matched)
assert max(abs(r['normalYRatio']) for r in matched)<.012
assert not face['fullyBuriedFaceIds'] and not attribution['summary']['originalTerrainFullyBuriedIds']
modes=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
    f=read(folder('four-mode-foundations-v2')/('210032:0-'+mode+'.json'))
    assert f['sourceSHA256']==SHA and f['foundation']['completeTerrainTriangles']==42334 and f['strictFoundationAccepted']
    assert f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
    modes.append(dict(mode=mode,wholeWorldSHA256=f['wholeWorldSHA256'],strictFoundationAccepted=True))
n=read(folder('complete-neighbours-v3')/'summary.json');v=read(folder('ordinary-validation-v3')/'summary.json')
assert len(n['requiredNativeUids'])==5 and not n['basicReasons'] and not n['unresolvedNatives']
assert v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0
assert v['ordinaryConcerns']==[dict(uid=UID,concerns=['sampled-terrain-above-model-bottom'])]
images=[folder('contact-faces-v2')/'contact-faces.png']+[folder('extent-views-v1')/(name+'.png') for name in ['whole','extent-front','extent-reverse']]
decision=dict(uid=UID,sourceSHA256=SHA,reviewer='Codex ROOT',sourceTerrainRelationshipReviewed=True,originalSurveyedRelationshipAccepted=True,geometryOrPoseChanges=0,aiGeometryModelling=False,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=True,checks=modes,lowRimFaceIds=sorted(rim),buriedFaceIds=[],changedTerrainFaces=[r['faceId'] for r in attribution['faces'] if r['maximumTerrainDifferenceMetres']>.004],imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in images],basis=[
    'All 4332 global-low-rim faces reproduce exactly the original government terrain offsets. Inspected source and terrain overlays locate them on the near-vertical twin-pier perimeter and connecting edge.',
    'This accepts the supplied global-bottom relationship, not an assertion that every lowest vertex touches terrain. The complete foundation independently passes in all four geometry modes with no wholly buried faces.',
    '256 other near-vertical faces differ from original TIN by up to1.243558m; this review does not describe those offsets as unchanged. Their whole-source foundation checks pass, as do all38 BASIC and five installed-neighbour regressions.',
    'The1306 terrain contact-candidate vertices are contextual evidence only, not structural certification or a replacement for complete checks.',
    'Keep raw warning and all original source facets, pose and scale. No neighbour suppression or global tolerance change. Staged/live visual, collision and publication acceptance remain mandatory.'
],installationApproved=False,publicationApproved=False,stagedAndLiveReviewRequired=True)
save(DOC/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json',decision);refs.extend(images)
module('star_relationship_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-original-low-rim-relationship-review',list(dict.fromkeys(refs)),dict(uids=[UID],originalSurveyedRelationshipAccepted=True,rawStrictGroundContactPassed=False,rawStrictFoundationPassed=True,installationApproved=False))
