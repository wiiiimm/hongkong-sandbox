"""Bind exact original floor-role review, current witnesses and inspected exports."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ying_hoi_native_wall_admission_v1_20261026 import UID, PARENT, WALLS, replay

BASE = ROOT / 'docs/astra-city/government-import'
CONFIG = BASE / 'government-xl-ying-hoi-native-floor-original-install-config-v1-20261026.json'


def main():
    cfg = read(CONFIG)
    out = BASE / cfg['review']
    assert not out.exists()
    refs = [Path(__file__), CONFIG]
    pins = {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    identity = take(cfg['identity'], '207957:0/identity.json')
    support = take(cfg['supportBinding'], 'summary.json')
    reviewed = take('government-xl-after-ferry-tuen-mun-ying-hoi-progress-v2-20261026', 'ROOT-EXPORT-OBSERVATIONS.json')
    assert len(reviewed['imagesActuallyViewed']) == 8
    inspected = {q['path']: q['sha256'] for q in reviewed['imagesActuallyViewed']}
    reports, images, retained = [], [], []
    for width in [390, 1280]:
        report = take(cfg['browser'], str(width) + '/staged-browser.json')
        p = BASE / cfg['browser'] / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
        for v in [v for v in report['views'] if 'time' in v] + report['retainedNativeOwnViews']:
            image = p.parent / v['file']
            rel = str(image.relative_to(ROOT))
            sha = digest(image.read_bytes())
            assert inspected[rel] == sha == pins[cfg['browser']][rel]
            refs.append(image)
            item = dict(path=rel, sha256=sha, uid=v['uid'], width=width, time=v['time'])
            (images if v['uid'] == UID else retained).append(item)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    wall_image = BASE / cfg['wallViews'] / 'negative-wall-native-floor-roots.png'
    _, wall_pins = authenticate(BASE / cfg['wallViews'])
    assert digest(wall_image.read_bytes()) == wall_pins[str(wall_image.relative_to(ROOT))]
    refs.extend([manifest, wall_image, BASE / cfg['wallViews'] / 'result.json'])
    review = dict(uids=[UID], sourceSHA256ByUid=cfg['sources'], identityAccepted=True,
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  completeFourWorldSourceClearance=True, completeCurrentNeighbourChecks=2,
                  rawCanonicalSupportPassed=False, rawCompoundCapPassed=False,
                  acceptedOwnedNativeInteriorWallFaces=WALLS, retainedBasicSupportDependencies=[],
                  runtimeAvailabilityDependenciesByUid={UID: PARENT}, retainedNativeEntries={PARENT: support['installedNativeEntry']},
                  identityProof=identity['proof'], identityProofByUid={UID: identity['proof']},
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  leaseResources=['building:' + UID, 'building:' + PARENT], terrainEdits=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False,
                  visualAcceptance=True, originalSourceReviewAccepted=True, imagesActuallyViewed=images,
                  retainedImagesActuallyViewed=retained, browserReports=reports,
                  wallFloorImageActuallyViewed=dict(path=str(wall_image.relative_to(ROOT)), sha256=digest(wall_image.read_bytes())),
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
                  qualification=cfg['placementReview'] + ' ROOT directly opened the15wall/floor panels: ten small lower wall facets, four full-height vertical walls and one short lower wall have paths to authentic original floor facets. The upper envelope is not the sole occupied floor level of this original podium. The exact same-name T/P source relationship and retained native availability bound this source-specific wall/floor interpretation. All581transverse contacts ineachworld remain recorded as authored same-building wall/floor interfaces; no claim of zero interpenetration or engineering certification. No unrelated actor, horizontal buried floor or newly affected face is admitted. Separate leased guarded publication/live verification and complete retention readback remain mandatory.')
    refs.extend(replay(cfg, review))
    refs.append(HERE / 'test_ying_hoi_native_wall_admission_v1_20261026.py')
    save(out / 'ROOT-SOURCE-REVIEW.json', review)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    module('ying_hoi_floor_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        cfg['review'], 'exact-original-same-building-native-floor-role-review', list(dict.fromkeys(refs)), review)


if __name__ == '__main__':
    main()
