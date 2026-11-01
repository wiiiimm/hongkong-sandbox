"""Compose exact current source/physical evidence after actual export inspection.

No publication call. Requires a separate ROOT observation file whose complete
image cohorts match authenticated source, retained and lifecycle exports.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from one_peking_cycle_retained_contract_v2_20261101 import SOURCES, SUPPORTS, verify_native_interfaces

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-one-peking-after-twin-'
BATCH = P + 'cycle-final-source-physical-review-v1-20261101'
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}

def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspection', required=True)
    args = parser.parse_args()
    observation_path = (ROOT / args.inspection).resolve()
    assert observation_path.is_relative_to(BASE)
    observation = read(observation_path)
    assert observation['reviewer'] == 'Codex ROOT' and observation['allDeclaredExportsActuallyInspected'] is True
    out = BASE / BATCH
    assert not out.exists()
    refs, pins, receipts = [Path(__file__), observation_path], {}, {}
    def take(batch, path):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    def summary(suffix):
        batch = P + suffix + '-20261101'
        return take(batch, BASE / batch / 'summary.json')
    identity = summary('fresh-current-named-identity-v2')
    assert identity['identityAccepted'] and identity['sourceSHA256ByUid'] == SOURCES
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == identity['currentManifestSHA256']
    refs.append(manifest)
    current, current_paths = {}, {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for m in read(path)['models']:
            assert m['uid'] not in current
            current[m['uid']], current_paths[m['uid']] = m, path
    assert len(current) == 7069 and not set(SOURCES) & current.keys()
    raw_identities = []
    for uid, sha in SOURCES.items():
        b = P + 'fresh-current-named-identity-v2-20261101'
        proof = take(b, BASE / b / (uid.split('/')[1] + '-identity.json'))
        assert proof['passed'] and proof['sourceSHA256'] == sha
        assert {r['uid'] for r in proof['freshCurrentIdentity']['intersectingForms']} <= set(SOURCES) | {'landsd/73140:0'}
        raw_identities.append(proof)
    patch = summary('cycle-preparation-v3')
    assert patch['terrainValidatorPassed'] and patch['newlyDerivedTerrainWorkFaces'] == 5773
    neighbours = summary('cycle-neighbour-checks-v2')
    assert neighbours['allNativePassed'] and neighbours['allBasicPassed'] and neighbours['nativeChecked'] == neighbours['nativePassed'] == 36 and neighbours['basicChecked'] == 84
    nb = P + 'cycle-neighbour-checks-v2-20261101'
    native = take(nb, BASE / nb / 'native-neighbour-checks.json')
    assert len(native['rows']) == 36 and all(r['passed'] and r['terrain']['newlyWhollyBuried'] == r['terrain']['newlyUpwardWhollyBuried'] == 0 for r in native['rows'])
    scope = take(P + 'cycle-current-scope-v2-20261101', BASE / (P + 'cycle-current-scope-v2-20261101') / 'scope.json')
    required = set(scope['touchingNativeUids'])
    assert len(required) == 36 and required == {r['uid'] for r in native['rows']}
    foundations = summary('cycle-drawn-foundations-v2')
    assert len(foundations['rows']) == 8 and {(r['uid'], r['mode']) for r in foundations['rows']} == {(u, m) for u in SOURCES for m in MODES}
    for r in foundations['rows']:
        assert r['covered'] == r['triangles'] == (4114 if r['uid'] == 'landsd/233985:0' else 11670) and r['buried'] == r['buriedUpward'] == 0
    fb = P + 'cycle-drawn-foundations-v2-20261101'
    metrics = take(fb, BASE / fb / 'metrics.json')
    for r in metrics['rows']:
        assert r['sourcePreserved'] and r['sourceSHA256'] == SOURCES[r['uid']] and not r['missingTerrain'] and not r['missingDrawnTerrain']['count'] and r['maxSamplerDelta'] <= .004
        assert all(r['budget'][k] <= metrics['profiles']['mobile'][k] for k in ['geometryBytes', 'residentBytes', 'triangles'])
        if r['uid'] == 'landsd/233985:0': assert r['minSurfaceGap'] >= -.5 and r['minLowGap'] <= .1 and r['maxLowGap'] <= 1
    support = summary('cycle-four-world-tower-podium-support-v1')
    assert support['sourceSHA256ByUid'] == SOURCES and len(support['rows']) == 4 and {r['mode'] for r in support['rows']} == MODES
    assert all(r['support']['strictContacts'] == 287 and r['support']['samples'] == 293 and len(r['support']['strictLowRim']['failed']) == 6 and not r['compoundFoundation']['fullyBuriedTriangles'] for r in support['rows'])
    roots = summary('cycle-six-rim-root-paths-v1')
    assert roots['sourceSHA256ByUid'] == SOURCES and {r['mode'] for r in roots['rows']} == MODES
    assert all(r['targets'] == r['finiteAttachmentPaths'] == 6 and r['disconnected'] == r['aboveExistingEndpointCeiling'] == 0 and r['riseAboveEndpointRangeM'] == [0., 0.] for r in roots['rows'])
    # Bind complete saved witnesses and their exact coordinate-array inputs.
    for suffix in ['cycle-six-rim-root-paths-v1', 'cycle-four-world-tower-podium-support-v1']:
        batch = P + suffix + '-20261101'
        for path in (BASE / batch).rglob('*.json.gz'):
            take(batch, path)
    for r in foundations['rows']:
        take(fb, BASE / fb / (r['uid'].split('/')[1] + '--' + r['mode'] + '.json'))
    interface = summary('hullett-boundary-interface-review-v1')
    assert interface['interfaceRoleApproved'] and not interface['collisionExemption'] and not interface['foreignSupportDependencyApproved']
    browser = summary('cycle-mobile-completion-v1')
    assert browser['allBrowserDiagnosticsPassed'] and browser['sourceSHA256ByUid'] == SOURCES and set(browser['retainedNativeUids']) == required
    browser_batch = P + 'cycle-mobile-completion-v1-20261101'
    stage = HERE / 'local' / browser_batch
    catalogue = take(browser_batch, stage / 'catalogue.json')
    assert {m['uid']: m['sha256'] for m in catalogue['models']} == SOURCES
    for m in catalogue['models']:
        path = stage / m['asset']
        assert digest(path.read_bytes()) == SOURCES[m['uid']]
        refs.append(path)
    lifecycle_batch = P + 'cycle-atomic-lifecycle-v1-20261101'
    lifecycle = take(lifecycle_batch, BASE / lifecycle_batch / 'report.json')
    assert lifecycle['passed'] and len(lifecycle['cases']) == 3 and not lifecycle['pageErrors']
    source_images, retained_images, atomic_images = [], [], []
    for batch, width in [(browser['desktopEvidenceBatch'], 1280), (P + 'cycle-mobile-completion-v1-20261101', 390)]:
        path = BASE / batch / str(width) / 'staged-browser.json'
        report = take(batch, path)
        assert report['passed'] and not report['errors']
        for rows, target in [(report['views'], source_images), (report['retainedNativeOwnViews'], retained_images)]:
            for r in rows:
                if 'time' in r and 'file' in r:
                    image = path.parent / r['file']
                    assert ref(image)['sha256'] == pins[batch][str(image.relative_to(ROOT))]
                    refs.append(image)
                    target.append(ref(image))
    for c in lifecycle['cases']:
        image = BASE / lifecycle_batch / (c['name'] + '.png')
        assert ref(image)['sha256'] == pins[lifecycle_batch][str(image.relative_to(ROOT))]
        refs.append(image)
        atomic_images.append(ref(image))
    assert [len(x) for x in [source_images, retained_images, atomic_images]] == [8, 144, 3]
    for field, expected in [('sourceImagesActuallyViewed', source_images), ('retainedImagesActuallyViewed', retained_images), ('atomicImagesActuallyViewed', atomic_images)]:
        assert sorted(observation[field], key=lambda x: x['path']) == sorted(expected, key=lambda x: x['path'])
    retained_entries = {u: current[u] for u in sorted(required)}
    model_scope = summary('complete-source-scope-v1')
    native_contacts = summary('installed-native-contacts-v1')
    decision = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, currentManifest=ref(manifest), reviewer='Codex ROOT', identityAccepted=True, sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, visualAcceptance=True, qualifiedForLiveVerification=True, rawPhysicalFailuresPreserved=True, rawIdentityProofs=raw_identities, acceptedOriginalNativeInterfaces=[interface], unresolvedExternalBasicContacts=[], supportByUid=SUPPORTS, activationGroup=sorted(SOURCES), groundOwnerUids=['landsd/233985:0'], exactTerrainReplacement={k: patch['replacedNativeTerrain'][0][k] for k in ['url', 'sha256', 'retainedUids']}, retainedNativeEntries=retained_entries, retainedNativeRegression=dict(requiredNativeUids=sorted(required), nativeResolved=sorted(required), nativeRows=native['rows']), leaseResources=sorted(set(scope['resources']) | {'server:127.0.0.1:4177', 'terrain:city/data/terrain.json'}), imagesActuallyViewed=source_images, retainedImagesActuallyViewed=retained_images, supplementalImagesActuallyViewed=atomic_images, sourceGeometryChanges=0, sourcePoseChanges=0, installedMetadataChanges=0, terrainEdits=True, rawStrictSupportPassed=False, strictStructuralSupportApproved=False, authoredOriginalAssemblyJointAccepted=True, collisionExemption=False, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False, installationApproved=False, publication=False,
        interpretation='The exact original tower seats in its matching original podium, which meets the actual bounded original-source terrain. All287 strict tower anchors remain; the six direct-rim gaps connect by finite unchanged source edges to those anchors without rising above endpoints in every coordinate stream. These are authored source attachments, not moved vertices or new structural engineering certification. Preserve complete source detail and all raw warnings. The separately reviewed opaque Hullett boundary interface adds no foreign support or collision exclusion. Current full source clearance, complete native/BASIC regression, both viewport source/retained rendering and per-peer atomic failure/recovery evidence are combined only for this exact source revision/current scene. Ordinary global retained-support checks, fenced publication, live browser and full installed readback remain mandatory.')
    assert verify_native_interfaces(decision, model_scope, native_contacts, current, SOURCES)
    for path, sha in metrics['inputHashes'].items():
        p = ROOT / path
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    for u in required:
        p = current_paths[u].parent / current[u]['asset']
        assert digest(p.read_bytes()) == current[u]['sha256']
        refs.append(p)
    save(out / 'ROOT-PHYSICAL-REVIEW.json', decision)
    save(out / 'ROOT-SOURCE-REVIEW.json', decision)
    save(out / 'summary.json', decision)
    module('one_peking_final_source_review_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-current-source-physical-and-inspected-private-browser-review', list(dict.fromkeys(refs)), decision)

if __name__ == '__main__':
    main()
