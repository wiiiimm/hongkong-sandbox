"""Bound exact platform-component identity, preserving whole-campus rejection.

Only two explicit source/footprint extent failures are interpreted. This neither
changes the installed entry nor approves a new support interface or placement.
"""
import argparse
from pathlib import Path
from copy import deepcopy
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi22089-component-identity-review-v1-20261101'
PROBE = 'government-xl-hkdi22089-current-source-identity-probe-v1-20261101'
PLOT = 'government-xl-hkdi22089-current-projection-views-v1-20261101'
UID = 'landsd/22089:0'
SHA = '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'
EXPECTED_REASONS = ['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent']

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lease', required=True)
    p.add_argument('--observation', required=True)
    a = p.parse_args()
    lease = read(Path(a.lease))
    assert reservations.owns(lease) and 'building:' + UID in lease['resources']
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        f = BASE / batch / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    probe = take(PROBE, 'summary.json')
    selected = take(PROBE, 'selection.json.gz')['rows'][0]
    raw = take(PROBE + '-identity', '22089:0/identity.json')
    context = take(PROBE + '-identity', '22089:0/context.json')['identity']
    assert raw['uid'] == selected['uid'] == UID and raw['sourceSHA256'] == selected['sourceSHA256'] == SHA
    assert not raw['passed'] and raw['reasons'] == EXPECTED_REASONS
    assert raw['sourceFormSHA256'] == '446f5838577d29e5407190a459e5566dd04a618ae9e6b21cc5eeb84070a08aa1'
    assert raw['worldTrianglesSHA256'] == 'ac1f46abeb0bb3924b23d14eb0100ec4901078a2bac3685700969f8351b94788'
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName'] == selected['modelId'] == 'B441831851001063C0'
    assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid'] == UID
    assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == 3965
    assert context['exactObjectAndCSUID'] and context['unrelatedIntersectingForms'] == 0 and context['sourceExcessCoveredByUnrelatedFormsM2'] == 0
    forms = context['intersectingForms']
    assert len(forms) == 5 and all(f['sameParent'] and f['sharedOsmReference'] and f['parent'] == 'way/185631747' for f in forms)
    assert {f['uid'] for f in forms} == {UID, 'landsd/88343:0', 'landsd/89613:0', 'landsd/89615:0', 'landsd/88345:0'}
    assert probe['exactNativeStageRecordRechecked'] and probe['sourceComponentApprovalIsSeparateFromWholeLandmark']
    assert probe['rawInstalledEntry']['identityReviewApproved'] is False and probe['rawInstalledEntry']['wholeLandmarkAccepted'] is False
    plot = take(PLOT, 'summary.json')
    assert plot['sourceSHA256'] == SHA and plot['originalWorldSHA256'] == raw['worldTrianglesSHA256'] and plot['completeSourceFaces'] == 3965
    observation = (ROOT / a.observation).resolve()
    assert observation.is_relative_to(BASE)
    seen = read(observation)
    assert seen['reviewer'] == 'Codex ROOT' and seen['imageActuallyViewed'] == plot['image']
    image = ROOT / plot['image']['path']
    assert digest(image.read_bytes()) == plot['image']['sha256'] == pins[PLOT][plot['image']['path']]
    refs.extend([observation, image])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == raw['exactRouteManifestSHA256'] == probe['currentManifestSHA256']
    matches = [e for u in read(manifest)['officialModelCatalogues'] for e in read(ROOT / '3d-viewer' / u)['models'] if e['uid'] == UID]
    assert matches == [probe['rawInstalledEntry']] and digest((ROOT / selected['candidate']['path']).read_bytes()) == SHA
    refs.extend([manifest, ROOT / selected['candidate']['path']])
    assert reservations.owns(lease)
    proof = dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True)
    reviewed = deepcopy(raw)
    reviewed.update(passed=True, reasons=[], proof=proof, rawIdentityVerbatim=deepcopy(raw), sourceIdentityReviewUsedAI=True,
        rawLegacyCatalogueEntryPreserved=probe['rawInstalledEntry'], sourceComponentOnly=True, wholeLandmarkAccepted=False,
        physicalAccepted=False, installationApproved=False)
    result = dict(uids=[UID], sourceSHA256=SHA, sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'],
        currentManifestSHA256=probe['currentManifestSHA256'], rawInstalledEntry=probe['rawInstalledEntry'], rawIdentityReasonsPreserved=EXPECTED_REASONS,
        reviewedIdentityProof=proof, sourceComponentIdentityAccepted=True, wholeLandmarkAccepted=False,
        installedMetadataChanges=0, sourceGeometryChanges=0, sourcePoseChanges=0, genericThresholdChanges=0,
        physicalAcceptance=False, installationApproved=False, publication=False, sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        imageActuallyViewed=plot['image'], interpretation=[
            'The exact original graph, unique current component route, cached official object/CSUID record and whole geographic cell bind this unchanged platform source. All five intersecting current forms share the same recorded campus reference; there is no unrelated-form overlap.',
            'The complete projection and both whole-source perspectives were inspected. The platform contains the four block openings and extends outside the single mapped platform footprint into access/edge structures. Interpret only the two explicit footprint-extent proxy failures for this exact component; do not increase any generic extent threshold.',
            'This qualifies identity of the existing original platform component only. The raw negative catalogue identity flag and whole-campus incompleteness remain byte-for-byte. It grants no new placement, support-interface, geometry, complete-campus, publication or installation approval.'])
    save(out / 'reviewed-identity.json', reviewed)
    save(out / 'ROOT-COMPONENT-IDENTITY-REVIEW.json', result)
    module('hkdi_component_identity_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-exact-original-campus-platform-component-identity-only', refs, result)

if __name__ == '__main__': main()
