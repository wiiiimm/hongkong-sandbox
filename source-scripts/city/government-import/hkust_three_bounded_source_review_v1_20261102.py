"""Bounded identity and source-surface review of the exact HKUST original assembly.

No joint scene, BASIC modification, browser, installation or publication approval.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-academic309823-after-harbour-'
SOURCES = {
    'landsd/309823:0': '7270510e89f268a8c114ba787cdf9a1d4255d55acdc0d05bb4dfd81922f0e65a',
    'landsd/309829:0': '60d6732e907f0caf6833a87e362cad4504faf2f5a691354acb2f6810a2ba300b',
    'landsd/336320:0': '5641d68aac3d490fabbd916160cd3c2f96719973a9fd449beb52e2029657a899',
}

def name(suffix):
    return P + suffix + '-20261102'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--lease-file', required=True)
    args = parser.parse_args()
    assert args.batch == name('bounded-source-review-v1')
    out = BASE / args.batch
    assert not out.exists()
    lease = read(Path(args.lease_file))
    assert reservations.owns(lease) and {'building:' + u for u in SOURCES} <= set(lease['resources'])
    refs, pins = [Path(__file__)], {}

    def take(batch, filename='summary.json'):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(name('repaired-floor-runtime-v1'), 'selection.json.gz')
    sources = {r['uid']: r for r in selected['rows']}
    assert {u: r['sourceSHA256'] for u, r in sources.items()} == SOURCES
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == selected['manifestSHA256']
    refs.append(manifest)
    association = take(name('assembly-identity-context-v1'))
    spatial = take(name('foreign-excess-context-v1'))
    revision = take(name('primary-revision-v1'))
    primary = take(name('current-primary-records-v1'), 'footprints.json')
    official = {r['attributes']['BuildingCSUID']: r['attributes'] for r in primary['features']}
    assert association['requiredOriginalAssembly'] == spatial['requiredOriginalAssembly'] == SOURCES
    assert association['currentManifestSHA256'] == start
    assert spatial['retainedScopeUidsStillForeign'] == ['landsd/26949:0']
    assert not spatial['allFourSpatialLimitsPassed']
    assert all(r['compoundTargetCoverage'] >= spatial['limits']['minimumTargetCoverage'] and r['maximumExtentM'] <= spatial['limits']['maximumExtentM'] for r in spatial['rows'])
    assert all(r['unrelatedExcessM2'] > spatial['limits']['maximumUnrelatedExcessM2'] for r in spatial['rows'])
    assert spatial['limits'] == dict(minimumTargetCoverage=.95, maximumExtentM=10, maximumUnrelatedExcessM2=1)
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        foreign = take(name('foreign-excess-context-v1'), mode + '-foreign-excess.json')
        assert len(foreign['rows']) == foreign['completeForeignFormCount'] == 33
        assert len([r for r in foreign['rows'] if r['projectedExcessOverlapM2'] > 0]) == 17
        assert foreign['unionForeignExcessM2'] == next(r['unrelatedExcessM2'] for r in spatial['rows'] if r['mode'] == mode)
    foreign = take(name('current-foreign-contacts-v1'))
    native = take(name('current-native-contacts-v1'))
    assert foreign['foreignPairs'] == len(foreign['rows']) == 27 and len(native['rows']) == 1
    assert native['rows'][0]['nativeUid'] == 'landsd/26949:0'
    assert len(native['rows'][0]['modes']) == 4
    take(name('complete-source-pairs-v1'))
    take(name('pair-plane-context-v1'))
    take(name('native-contact-roles-v1'))
    retained = take(name('retained-native-regression-v1'))
    assert retained['requiredNativeUids'] == retained['nativeResolved'] == ['landsd/26949:0']
    assert retained['nativeRows'][0]['passed'] and retained['nativeRows'][0]['terrain']['newlyWhollyBuried'] == 0
    observed_path = BASE / name('junction-inspection-sheets-v1') / 'ROOT-OBSERVATIONS.json'
    observed = read(observed_path)
    refs.append(observed_path)
    assert observed['reviewer'] == 'Codex ROOT' and observed['aiGeometryModelling'] is False
    assert len(observed['sheetsActuallyViewed']) == 5 and len(observed['directImagesActuallyViewed']) == 3
    for image in [*observed['sheetsActuallyViewed'], *observed['directImagesActuallyViewed']]:
        path = ROOT / image['path']
        assert digest(path.read_bytes()) == image['sha256']
        refs.append(path)
        for original in image.get('inputs', []):
            path = ROOT / original['path']
            assert digest(path.read_bytes()) == original['sha256']
            refs.append(path)
    witnesses = take(name('lower-patch-witnesses-v1'))
    assert witnesses['sourceSHA256'] == SOURCES['landsd/309823:0'] and not witnesses['physicalAcceptance']
    assert len(witnesses['rows']) == 4
    assert all(r['failedWitnesses'] == 913 and r['unattributedWitnesses'] == 0 and r['negativeDownwardFaces'] == 11 and r['downwardPatches'] == r['downwardPatchesWithGradeAndClearCap'] == 2 and r['allNegativeWallsHaveClearCaps'] for r in witnesses['rows'])
    roots = take(name('current-ground-root-paths-v1'))
    for row in roots['rows']:
        if row['uid'] == 'landsd/336320:0':
            continue
        assert row['targets'] == row['finitePaths'] and row['aboveEndpointCeiling'] == 0 and row['strictRoots'] > 0
    identity_rows = []
    for uid, sha in SOURCES.items():
        source = sources[uid]
        raw = take(name('current-identity-v1'), uid.split('/')[1] + '/identity.json')
        form = source['source']['building']
        current = official[form['buildingCSUID']]
        epoch = next(r for r in revision['rows'] if r['uid'] == uid)
        assembly = next(r for r in association['rows'] if r['uid'] == uid)
        assert raw['uid'] == uid and raw['sourceSHA256'] == source['sourceSHA256'] == sha
        assert not raw['passed'] and raw['reasons']
        assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName'] == source['modelId']
        route = raw['exactCurrentComponentRoute']
        assert route['qualified'] and route['official']['objectId'] == form['objectId'] == int(uid.split('/')[1].split(':')[0])
        assert route['official']['buildingCSUID'] == current['BuildingCSUID'] == form['buildingCSUID']
        assert current['Status'] == 'Active' and current['BuildingBlockType'] == form['structureType']
        assert current['GeoRefNo'] == source['modelId'][1:11]
        assert current['BaseHeight'] == form['baseHeightHKPD'] and current['TopHeight'] == form['topHeightHKPD']
        assert epoch['cachedObjectId'] == form['objectId'] and epoch['currentProviderObjectId'] == current['OBJECTID']
        assert not epoch['objectIdExact'] and epoch['buildingIdExact'] and epoch['modelGeoRefExact'] and epoch['baseAndTopHeightsExact']
        assert assembly['completeAssemblyWholeCellCovered'] and assembly['completeAssemblyTargetCoverage'] >= .95
        path = ROOT / source['candidate']['path']
        assert digest(path.read_bytes()) == sha
        refs.append(path)
        tile = ROOT / '3d-viewer' / source['source']['tile']
        assert digest(tile.read_bytes()) == source['source']['tileSHA256']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == uid) == form
        refs.append(tile)
        foundation = take(name('repaired-floor-' + uid.split('/')[1].replace(':', '-') + '-foundations-v1'))
        assert foundation['establishedFoundationPolicyPassed'] and all(r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
        if uid != 'landsd/309823:0':
            rim = take(name('canonical-rims-' + uid.split('/')[1].replace(':', '-') + '-v1'))
            assert all(r['allCanonicalSamplePredicatesPass'] and r['failedSamples'] == 0 for r in rim['rows'])
        proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True,
                     identifierScope='current-viewer-record-and-frozen-native-match', currentProviderObjectIdExact=False,
                     currentProviderRevisionAssociationReviewed=True, requiredOriginalAssembly=SOURCES)
        reviewed = deepcopy(raw)
        reviewed.update(passed=True, reasons=[], proof=proof, rawIdentityVerbatim=deepcopy(raw), requiredOriginalAssembly=SOURCES,
                        currentProviderRevision=epoch, componentIdentityOnly=True, wholeLandmarkAccepted=False,
                        sourceSurfaceAndGroundReviewAccepted=True, physicalAcceptance=False, installationApproved=False,
                        sourceIdentityReviewUsedAI=True, aiGeometryModelling=False)
        save(out / (uid.split('/')[1] + '-reviewed-identity.json'), reviewed)
        identity_rows.append(dict(uid=uid, sourceSHA256=sha, sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'], identityAccepted=True, identityProof=proof, rawReasonsPreserved=raw['reasons'], currentProviderRevision=epoch))
    result = dict(uids=list(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES, activationGroupRequired=True,
                  currentManifestSHA256=start, rows=identity_rows, identityAccepted=True, sourceSurfaceAndGroundReviewAccepted=True,
                  rawCompoundForeignOverlapFailureRetained=True, genericThresholdChanges=0, sourceGeometryChanges=0, sourcePoseChanges=0,
                  sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, wholeLandmarkAccepted=False,
                  physicalAcceptance=False, jointSceneAccepted=False, visualRuntimeAcceptance=False, installationApproved=False, publication=False,
                  interpretation=[
                      'Accept association only of these three exact original government components together. Their intact typed GeoRef roots, unique current viewer UID/CSUID routes, fresh stable BuildingID/GeoRef/heights and exact assembly cells bind the source. The provider has renumbered OBJECTIDs: exactObjectId refers to the current viewer/frozen-native epoch only; fresh provider object IDs are explicitly different and preserved.',
                      'Individual coverage reflects source component partitioning across the connected academic/podium/library assembly. Complete assembly coverage exceeds the unchanged95percent criterion for every target and compound extent is below10m. No source is cropped, shifted, rescaled or claimed to complete the entire campus.',
                      'Retain the734.323487m² foreign-excess failure and all17positive/33scoped foreign records. All27current foreign contact pairs,28transverse installed-carpark contacts and all original pair/plane records remain. This review neither claims common permit ownership nor clears any genuine neighbour, collision or fallback failure. No foreign actor is removed or relabelled.',
                      'Accept the named source-surface/ground composition: both smaller originals pass ordinary criteria in allfour streams; the academic source passes established foundation policy with no upward burial. Every one of913failed canonical witnesses is attributed to510clear-cap walls, two exact-edge-connected downward patches meeting actual grade/cap boundaries, or the58exact canonical root paths. All underlying failures remain verbatim. No new strict-root requirement is imposed on the ordinarily passing extension.',
                      'This positive bounded identity/surface review is conditional on the complete3-source atomic assembly and exact current inputs. The7roof and3named/Temporary BASIC changes still require their own guarded publication/lifecycle evidence. Actual desktop/mobile day/night, picking/collision/failure-retry, source availability, final fenced publication and independent installed readback remain mandatory.'])
    save(out / 'ROOT-BOUNDED-SOURCE-REVIEW.json', result)
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    module('hkust_bounded_source_surface_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'bounded-exact-hkust-three-component-identity-and-source-ground-review-only', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
