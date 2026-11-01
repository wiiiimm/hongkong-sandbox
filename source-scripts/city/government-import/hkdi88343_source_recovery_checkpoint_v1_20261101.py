"""Authenticate current HKDI recovery progress; grant no installation credit."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi88343-source-recovery-checkpoint-v1-20261101'
PREFIX = 'government-xl-hkdi88343-after-one-peking-'

def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, records, pins = [Path(__file__)], {}, {}
    names = [PREFIX + 'current-v1-20261101-runtime', PREFIX + 'current-v1-20261101-identity',
        PREFIX + 'attributes-v1-20261101', 'government-xl-after-one-peking-current-native-bounds-v2-20261101',
        PREFIX + 'scope-v1-20261101', PREFIX + 'support-v1-20261101', PREFIX + 'unapproved-preview-v1-20261101',
        PREFIX + 'foundations-v1-20261101', 'government-xl-hkdi88343-original-three-part-context-views-v1-20261101',
        'government-xl-hkdi88343-low-component-views-v2-20261101', 'government-xl-hkdi88343-original-deck-paths-v2-20261101']
    for name in names:
        records[name], pins[name] = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
    def take(name, filename):
        f = BASE / name / filename
        assert digest(f.read_bytes()) == pins[name][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    runtime = take(names[0], 'selection.json.gz')
    identity = records[names[1]]
    assert identity['rows'][0]['passed'] and identity['uids'] == ['landsd/88343:0']
    scope = take(names[4], 'summary.json')
    assert scope['currentManifestSHA256'] == runtime['manifestSHA256']
    assert scope['rows'][0]['currentNativeActorsChecked'] == 7071 and scope['rows'][0]['currentFormsWithinTwoMetreRegion'] == 2
    assert [r['uid'] for r in scope['rows'][0]['nearbyNativeActors']] == ['landsd/22089:0']
    support = take(names[5], 'summary.json')
    assert all(r['unresolved'] == r['finitePaths'] == 6 and r['support']['strictContacts'] == 0 and not r['support']['passed'] for r in support['rows'])
    assert take(names[7], 'summary.json')['establishedFoundationPolicyPassed']
    deck = take(names[-1], 'summary.json')
    assert deck['fourWorldPathCounts'] == [6, 6, 6, 6] and deck['exactNativeDeckFace'] == 3896
    for width in [1280, 390]:
        r = take(names[6], str(width) + '/staged-browser.json')
        assert r['passed'] and not r['errors']
    observation = BASE / 'government-xl-hkdi88343-reviewed-context-observations-v1-20261101.json'
    observed = read(observation)
    assert observed['reviewer'] == 'Codex ROOT' and not observed['physicalAccepted'] and len(observed['imagesActuallyViewed']) == 11
    refs.append(observation)
    for row in observed['imagesActuallyViewed']:
        assert any(p.get(row['path']) == row['sha256'] for p in pins.values())
        f = ROOT / row['path']
        assert digest(f.read_bytes()) == row['sha256']
        refs.append(f)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == runtime['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=['landsd/88343:0'], sourceSHA256=identity['rows'][0]['sourceSHA256'],
        currentManifestSHA256=runtime['manifestSHA256'], completedProofs=[dict(batch=n, jobId=records[n]['jobId']) for n in names],
        currentNativeActors=7071, completeScopedNativeUids=['landsd/22089:0'], currentForms=2,
        identityPassed=True, fourWorldEarthFoundationsPassed=True, sixDeckPathsPassedInEveryWorld=True,
        desktopMobileUnapprovedPreviewPassed=True, exactImagesActuallyViewed=observed['imagesActuallyViewed'],
        humanStatus='In process', processState='queued', requiredResource='Code/compute and bounded exact-source evidence review; no human decision or AI geometry modelling requested',
        nextAction='Reconcile the exact installed-parent source/label scope while preserving identityReviewApproved=false; qualify the authored inclined28face/deck interface without a generic wall-embedding threshold change, preserve full raw failed compound-envelope/rim diagnostics, then complete scoped publication acceptance. Do not install from previews or finite paths alone.',
        rawOrdinaryRimFailureRetained=True, rawCompoundEnvelopeFailureRetained=True, parentLegacyFlagsPreserved=True,
        physicalAcceptance=False, installationApproved=False, publication=False, newlyInstalled=0, newlyTerminal=0,
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, scriptExternalAICalls=0)
    save(out / 'summary.json', result)
    module('hkdi_recovery_checkpoint_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'current-original-hkdi-source-recovery-and-actual-inspection-checkpoint', refs, result)

if __name__ == '__main__': main()
