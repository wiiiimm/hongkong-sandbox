"""Review two exact depot canopy correspondences for private visibility tests only."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-depot120104-two-canopies-private-review-v1-20261029'
    out = base / batch
    assert not out.exists()
    refs, pins, reviews = [Path(__file__)], {}, []
    uid, sha = 'landsd/120104:0', '655eb47347eec12814da670830672cf5808a23bbb590e520b22b0d21f6ce360f'
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_ref = dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes()))
    refs.append(manifest)

    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    for number in ['177363', '178180']:
        basic = 'landsd/' + number + ':0'
        packet = 'government-xl-depot120104-canopy' + number + '-primary-v1-20261029'
        feature = take(packet, base / packet / 'summary.json')
        assert (feature['sourceUid'], feature['basicUid'], feature['sourceSHA256']) == (uid, basic, sha)
        f, b = feature['currentForms'][uid], feature['currentForms'][basic]
        assert f['parent'] == b['parent'] == 'relation/12442482'
        official = feature['officialRecords'][basic]
        assert b['baseHeightHKPD'] is None and b['topHeightHKPD'] is None and b['heightSource'] == 'estimated'
        assert official['BaseHeight'] is None and official['TopHeight'] is None and official['Status'] == 'Active' and official['BuildingBlockType'] == 'Open-sided Structure'
        assert feature['officialRecords'][uid]['BuildingCSUID'] == f['buildingCSUID'] == '1627618820T20050430'
        views = 'government-xl-depot120104-canopy' + number + '-views-v1-20261029'
        take(views, base / views / 'summary.json')
        images = []
        for name, path in [(packet, base / packet / 'original-roof-current-official-canopy.png'), (views, base / views / 'before-after-contact-context.png')]:
            assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
            refs.append(path)
            images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
        review = dict(uids=[uid], sourceUid=uid, basicUid=basic, sourceSHA256=sha,
                      currentManifest=manifest_ref, exactBasicForm=b, officialCanopyRecord=official,
                      reviewer='ROOT', imagesActuallyViewed=images,
                      coverageRowsVerbatim=feature['originalRoofComponents'],
                      privateCanopyExperimentApproved=True, coveragePercentageNotAnApprovalRule=True,
                      sourceIdentityApproved=False, physicalAcceptance=False, collisionReviewApproved=False,
                      visualAcceptance=False, installationApproved=False, publication=False,
                      sourceGeometryChanges=0, basicGeometryChanges=0,
                      aiGeometryModelling=False, evidenceInterpretationUsedAI=True,
                      proposedSuppression=dict(ownerUid=uid, sourceSHA256=sha, suppressesBuildingUids=[basic], onlyWhileExactOwnerActive=True),
                      qualification='ROOT inspected the fresh official/BASIC/native roof outlines and exact before/after contact diagrams. This is the same depot canopy feature in the complete authored original, including higher roof bays and columns; the active official canopy has no surveyed base/top while BASIC uses an estimated3m roof. Roof coverage/outline shortfalls remain verbatim; they grant no structural support credit. Approve only conditional visibility experimentation for this exact feature/revision. Full failure/Base-only/Auto/eviction restoration, source-role, collision and desktop/mobile review remain required. No original or BASIC geometry changes.')
        save(out / ('ROOT-PRIVATE-CANOPY-REVIEW-' + number + '.json'), review)
        reviews.append(dict(basicUid=basic, file='ROOT-PRIVATE-CANOPY-REVIEW-' + number + '.json'))
    result = dict(uids=[uid], sourceSHA256=sha, reviews=reviews,
                  privateCanopyExperimentsApproved=True, installationApproved=False, publication=False,
                  qualification='Two separately source-bound feature correspondence reviews; private experiments only, no automatic union/installation/physical approval.')
    save(out / 'summary.json', result)
    module('depot_two_canopy_private_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'two-exact-original-canopy-feature-private-experiment-reviews', refs, result)


if __name__ == '__main__':
    main()
