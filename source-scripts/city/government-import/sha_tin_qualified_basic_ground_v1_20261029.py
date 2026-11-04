"""Qualify the four BASIC-only updates and exercise their real publisher stagers."""
import copy
import sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-sha-tin-';BATCH=P+'qualified-basic-ground-v1-20261029'
TERRAIN_URL='city/data/government-native-sha-tin-seven-original-v1-20261029.json'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def summary(suffix):return take(P+suffix,BASE/(P+suffix)/'summary.json')
    proposal=summary('three-basic-ground-proposals-v2-20261029');geometry=summary('production-geometry-equivalence-v1-20261029');collision=summary('production-basic-collision-v1-20261029');life=summary('source-bound-production-atomic-lifecycle-v1-20261029');grade=summary('seven-final-grade-composition-v1-20261029')
    assert geometry['unchangedLegacyForms']==70 and geometry['unchangedOriginalModels']==7 and geometry['equivalentBasicContinuations']==3
    assert collision['exactCellMapUnchanged']and collision['allRoofMaximaUnchanged']and collision['probes']==435204 and collision['newlyBlockedProbes']>0
    assert life['browserPassed']and life['cases']==life['expectedCases']==8 and life['actualProductionGeometryHTTP']and life['moduleSubstitution']is False
    assert grade['sourceGradeEvidenceComposed']
    images=take(P+'source-bound-fallback-root-observations-v1-20261029',BASE/(P+'source-bound-fallback-root-observations-v1-20261029')/'ROOT-FALLBACK-IMAGE-OBSERVATIONS.json');assert images['allEightFallbackCanvasesActuallyInspected']and images['boundedFallbackAppearanceReviewed']
    # Reuse exact source/prototype equivalence and actual-production lifecycle;
    # do not recollect unchanged PNGs or re-run exact source geometry.
    for row in images['images']:
        path=ROOT/row['path'];assert digest(path.read_bytes())==row['sha256'];refs.append(path)
    raw=summary('three-basic-continuation-foreign-volume-v1-20261029');pair=summary('three-basic-continuation-pair-context-v1-20261029');assert len(raw['rows'])==291 and len(pair['allSixNewNewPairs'])==6 and len(pair['footprintRows'])==3
    fixture=P+'source-bound-production-fixture-v1-20261029';cfgpath=HERE/'local'/fixture/'config.json';cfg=take(fixture,cfgpath);catpath=ROOT/cfg['stage']/'catalogue.json';cat=take(fixture,catpath);models={m['uid']:m for m in cat['models']};assert len(models)==7
    terrain=summary('seven-upward-floor-terrain-return-v1-20261029');asset=ROOT/terrain['candidate']['path'];assert digest(asset.read_bytes())==terrain['candidate']['sha256'];refs.append(asset)
    sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
    contract=module('qualified_native_basic_stager',HERE.parent/'island-detail-integration/native_basic_fallback_ground.py');canonical=module('qualified_native_basic_canonical',HERE.parent/'island-detail-integration/basic_podium_footings.py');illustrative=module('qualified_basic_canopy_stager',HERE.parent/'island-detail-integration/illustrative_foundations.py')
    refs.extend([HERE.parent/'island-detail-integration/native_basic_fallback_ground.py',HERE.parent/'island-detail-integration/basic_podium_footings.py',HERE.parent/'island-detail-integration/illustrative_foundations.py'])
    out.mkdir();updates=[];reviews=[]
    for row in proposal['rows']:
        uid=row['uid'];b=row['originalBuilding'];hint=row['hint'];tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(x for x in read(tile)['buildings']if x['uid']==uid)==b;refs.append(tile)
        g=next(r for r in geometry['hinted']if r['uid']==uid);assert g['allProductionAttributesEqualBrowserTestedPrototype']and g['originalCoreAttributesUnchanged']and g['visualAndCollisionDescriptionsEqual']
        volume=next(r for r in collision['volumeRows']if r['uid']==uid);assert volume['oldRoofAndBodyVolumesPreserved']and volume['exactCellMembershipUnchanged']and volume['roofMaximumUnchanged']
        assert row['fullHeightFieldCoverage']and hint['terrainSHA256']==terrain['candidate']['sha256']
        review=dict(status='approved-for-integration',policy=contract.POLICY,uid=uid,buildingCSUID=b['buildingCSUID'],sourceFormSHA256=canonical.value_sha(b),tileSHA256=digest(tile.read_bytes()),hint=hint,terrainURL=TERRAIN_URL,ownerPlacementAndAvailabilitySHA256=contract.owner_contract_sha(models[uid]),groundRangeHKPD=row['groundRangeHKPD'],rawMissingNativeAreaM2=row['rawMissingNativeAreaM2'],rawNativeProjectionCoverageComplete=row['nativeMeshProjectionCoverageComplete'],sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,reviewer='ROOT',**{k:True for k in contract.REQUIRED},rawContactFlagsRetained=True,rawForeignSurfaceContextBatch=P+'three-basic-continuation-foreign-volume-v1-20261029',rawNewNewPairContextBatch=P+'three-basic-continuation-pair-context-v1-20261029',collisionSoftwareBatch=P+'production-basic-collision-v1-20261029',actualProductionLifecycleBatch=P+'source-bound-production-atomic-lifecycle-v1-20261029',basis='Existing closed BASIC Tower footprint semantics continue down only to authenticated drawn-source ground. Every original body/roof attribute remains exact; native source detail bypasses continuation entirely. Actual cell membership and roof maxima stay equal; collision changes are confined to same-footprint lower intervals. Existing opaque junction and Float32 boundary contacts remain explicit, not treated as geometric clearance or cadastral ownership. Actual source and fallback exports inspected. No government geometry is generated or changed.')
        path=out/(uid.split('/')[1]+'-qualified-review.json');save(path,review);binding=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()));updates.append(dict(uid=uid,tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()),before=b,hint=hint,terrainURL=TERRAIN_URL,evidence=binding));reviews.append(binding)
    canopy_batch=P+'canopy-post-foundation-v1-20261029';canopy=take(canopy_batch,BASE/canopy_batch/'summary.json');canopy_input=take(canopy_batch,BASE/canopy_batch/'input.json');canopy_proposal=take(canopy_batch,BASE/canopy_batch/'proposal.json');render=take(canopy_batch,BASE/canopy_batch/'render-proof.json');b=canopy_input['building'];assert b['uid']=='landsd/92340:0'and canopy['fullPostFootprintsMeetGround']and canopy['wholeRoofClear']and render['roofPartsExactlyUnchanged']and render['allXZExactlyUnchanged']and render['onlyIllustrativePostBottomVerticesChanged']
    tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(x for x in read(tile)['buildings']if x['uid']==b['uid'])==b;refs.append(tile)
    canopy_review=dict(uid=b['uid'],status='approved-for-integration',fullPostFootprintsMeetGround=True,wholeRoofClear=True,roofAndRecordedElevationsUnchanged=True,collisionReviewApproved=True,visualReviewApproved=True,actualAtomicLifecyclePassed=True,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,foundationBase=canopy_proposal['foundationBase'],sourceFormSHA256=canonical.value_sha(b),tileSHA256=digest(tile.read_bytes()),reviewer='ROOT',evidenceInterpretationUsedAI=True,basis='Only the seven existing illustrative post bottoms extend downward over their unchanged small footprints. Exact roof, post top/XZ and source heights stay unchanged; actual production collision cell map/roof maxima and all eight native-activation/failure/Base-only/retry/eviction restoration checks pass. The BASIC roof/posts are visible again on native-owner failure or Base-only. No government mesh edits or structural certification.')
    path=out/'92340-0-qualified-canopy-review.json';save(path,canopy_review);canopy_update=dict(uid=b['uid'],tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()),before=b,foundationBase=canopy_proposal['foundationBase'],proposal=dict(path=str((BASE/canopy_batch/'proposal.json').relative_to(ROOT)),sha256=digest((BASE/canopy_batch/'proposal.json').read_bytes())),evidence=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    plan=dict(nativeBasicFallbackGrounds=updates,illustrativeFoundations=[canopy_update]);save(out/'plan-fragment.json',plan)
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=copy.deepcopy(read(manifest_path));refs.append(manifest_path)
    dest=ROOT/'3d-viewer/city/data/official-models'/BATCH/'catalogue.json';assert not dest.exists();tpath=ROOT/'3d-viewer'/TERRAIN_URL;assert not tpath.exists()
    edits={dest:canonical.canonical(cat),tpath:asset.read_bytes()};manifest['officialModelCatalogues'].append(str(dest.relative_to(ROOT/'3d-viewer')));manifest['terrainPatches'].append(dict(url=TERRAIN_URL,resolution=5,area='Sha Tin unchanged government originals'));report={}
    illustrative.stage_illustrative_foundations(ROOT,plan,manifest,edits,report,read,lambda p:digest(p.read_bytes()),canonical.canonical)
    contract.stage_native_basic_fallback_ground(ROOT,plan,manifest,edits,report,read,lambda p:digest(p.read_bytes()),canonical.canonical)
    assert len(report['nativeBasicFallbackGrounds'])==3 and len(report['illustrativeFoundations'])==1 and len(report['retainedNativeBasicFallbackGroundChecks'])==3
    changes={u['uid']:dict(u['before'],nativeFallbackGround=u['hint'])for u in updates};changes[b['uid']]=dict(b,foundationBase=canopy_proposal['foundationBase'],foundationPolicy='terrain-derived-illustrative-posts')
    for uid,expected in changes.items():
        path=ROOT/'3d-viewer/city/data/tiles'/(expected['tile']+'.json');actual=next(x for x in __import__('json').loads(edits[path])['buildings']if x['uid']==uid);assert actual==expected
    result=dict(uids=list(models),qualifiedBasicContinuationUids=[u['uid']for u in updates],qualifiedCanopyUid=b['uid'],realPublisherStagersPassed=True,sourceAndSurveyFieldsUnchanged=True,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,actualProductionLifecyclePassed=True,stagerReport=report,publicFilesWritten=0,inMemoryOnly=True,fullPublisherPassed=False,completeOriginalModelAcceptance=False,installationApproved=False,publication=False,qualification='Qualified source-bound BASIC-only plan fragment, exercised in memory through the actual two publisher stagers using all current catalogues and seven new source owners. Exact original source, field, source/terrain revision, owner placement/availability, body/roof/height, existing grid fallback, collision, visual and actual-production lifecycle evidence is bound. The three hints and canopy post metadata alone are staged; no model, tile, terrain, manifest or acceptance row has been published. Full source assembly/publication remains separate.')
    save(out/'summary.json',result)
    module('sha_tin_qualified_basic_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-basic-continuation-and-canopy-real-stager-plan-fragment',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
