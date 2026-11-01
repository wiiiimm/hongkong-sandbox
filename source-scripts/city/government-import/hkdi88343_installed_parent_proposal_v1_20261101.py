"""Early exact-original dependency routing only; preserve the parent's flags."""
import argparse, copy, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from dependency_preflight import from_catalogues

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi88343-installed-parent-proposal-v1-20261101'
RUNTIME = 'government-xl-cohort19-current-original-checks-v1-20261101-runtime'
UID, PARENT = 'landsd/88343:0', 'landsd/22089:0'
SHA = '98e25a696418680d31f70de499561a68412fc1b08d50ab4e49365ef63adadcc8'
PARENT_SHA = '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists()
    resources = ['building:' + UID, 'building:' + PARENT]
    lp = local / 'reservation.json'
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('hkdi-original-dependency-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=1800)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(resources) == set(lease['resources'])
    _, pins = authenticate(BASE / RUNTIME)
    selection = BASE / RUNTIME / 'selection.json.gz'
    assert digest(selection.read_bytes()) == pins[str(selection.relative_to(ROOT))]
    row = next(r for r in read(selection)['rows'] if r['uid'] == UID)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == SHA
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = manifest.read_bytes()
    entries, paths = {}, {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        for entry in read(path)['models']:
            assert entry['uid'] not in entries
            entries[entry['uid']], paths[entry['uid']] = entry, path
    assert UID not in entries and entries[PARENT]['sha256'] == PARENT_SHA
    parent = entries[PARENT]
    parent_asset = paths[PARENT].parent / parent['asset']
    assert digest(parent_asset.read_bytes()) == PARENT_SHA
    proposal = copy.deepcopy(row['candidate']['entry'])
    assert proposal['sha256'] == SHA and not proposal.get('supportDependencies')
    proposal.update(publicationApproved=False, placementReviewed=False, identityReviewApproved=False, sourceIdentityReviewed=False,
                    supportDependencies=[dict(uid=PARENT, state='installed', buildingCSUID=parent['buildingCSUID'], sha256=PARENT_SHA)])
    cat = out / 'unapproved-dependency-proposal.json'
    save(cat, dict(models=[proposal], publication=False, installationApproved=False))
    report = from_catalogues(manifest, [cat])
    save(out / 'dependencies.json', report)
    refs = [Path(__file__), BASE / RUNTIME / 'result.json', selection, asset, parent_asset, cat]
    for path, sha in report['inputHashes'].items():
        p = ROOT / path
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    assert reservations.owns(lease) and manifest.read_bytes() == before
    result = dict(uids=[UID, PARENT], candidateUid=UID, proposedSupportUid=PARENT, sourceSHA256=SHA, supportSHA256=PARENT_SHA,
                  currentManifestSHA256=digest(before), candidateCount=1, requiresAssemblyInvestigation=report['requiresAssemblyInvestigation'],
                  rawInstalledParentEntry=parent, parentIdentityReviewApproved=parent.get('identityReviewApproved'),
                  sourceGeometryChanges=0, sourcePoseChanges=0, installedMetadataChanges=0, identityAccepted=False, physicalAcceptance=False,
                  requiresFreshCurrentSceneCapture=True, installationApproved=False, publication=False,
                  nextStep='Fresh source/current-parent attributes and exact four-world support/compound-foundation checks after the active One Peking transaction. Preserve parent identityReviewApproved=false; reconcile its exact source/label review evidence before any dependency acceptance. Topology preflight alone grants no approval.')
    save(out / 'summary.json', result)
    module('hkdi_original_parent_proposal_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'unapproved-exact-original-installed-parent-topology-proposal', refs, result)

if __name__ == '__main__':
    main()
