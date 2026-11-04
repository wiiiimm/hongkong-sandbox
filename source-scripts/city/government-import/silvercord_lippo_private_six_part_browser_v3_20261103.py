"""Observe the exact five-original/retained-owner proposal on private loopback.

This produces diagnostic browser evidence, not physical or publication approval.
No installed file or review flag is changed. Atomic denial/retry is a separate
required phase: the per-source harness runs success views only for this group.
"""
import copy
import functools
import http.server
import os
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from dependency_preflight import inspect_dependencies

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-private-six-part-browser-v3-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
PROPOSAL = 'government-xl-silvercord-lippo-private-dependency-proposal-v1-20261103'
ADMISSION = 'government-xl-silvercord-lippo-complete-floor-admission-v1-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
SCOPE = 'government-xl-silvercord-lippo-full-current-parent-scope-v3-20261103'
OWNER = 'landsd/239465:0'
RETAINED = [OWNER, 'landsd/21915:0', 'landsd/156599:0', 'landsd/234188:0']


def diagnostic_catalogue(before, source_hashes):
    """Only a diagnostic camera priority changes; immutable source/pose retained."""
    assert {m['uid']: m['sha256'] for m in before['models']} == source_hashes
    assert len(before['models']) == len(source_hashes) == 5
    group = sorted(source_hashes)
    result = copy.deepcopy(before)
    for model in result['models']:
        assert model['activationGroup'] == group and model['proceduralWindows'] is False
        assert all(model[k] is False for k in ['publicationApproved', 'placementReviewed',
                                              'identityReviewApproved', 'sourceIdentityReviewed'])
        assert not model.get('suppressesBuildingUids')
        assert all(d['uid'] in source_hashes and d['sha256'] == source_hashes[d['uid']]
                   and d['state'] == 'candidate' for d in model.get('supportDependencies', []))
        model['priority'] = 'landmark'
    return result


def exact_owner_after(before, after, update):
    """Private support-only substitution, preserving all owner/other metadata."""
    assert update['changedFields'] == ['supportDependencies']
    expected = copy.deepcopy(before)
    model = next(m for m in expected['models'] if m['uid'] == update['ownerUid'])
    assert model == update['beforeEntry'] and model['sha256'] == update['ownerSHA256']
    model['supportDependencies'] = update['afterEntry']['supportDependencies']
    assert model == update['afterEntry'] and expected == after
    return True


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    sources = {r['uid']: r['sourceSHA256'] for r in selection['rows']}
    proposal = take(PROPOSAL, BASE / PROPOSAL / 'summary.json')
    assert proposal['sourceSHA256ByUid'] == sources and not proposal['supportMigrationApproved']
    catalogue = diagnostic_catalogue(take(PROPOSAL, BASE / PROPOSAL / 'private-five-original-catalogue.json'), sources)
    admission = take(ADMISSION, BASE / ADMISSION / 'summary.json')
    assert admission['privateTerrainValidatorPassed'] and admission['exactEffectiveMembers'] == 16
    assert admission['finiteEdges'] == 22 and not admission['publication']
    candidate = take(CANDIDATE, BASE / CANDIDATE / 'summary.json')
    scope = take(SCOPE, BASE / SCOPE / 'summary.json')
    assert len(scope['affectedNativeUids']) == 1228 and scope['basicFormsInFullParentScope'] == 5408
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == proposal['currentManifestSHA256']
    assert scope['currentManifestSHA256'] == admission['currentManifestSHA256'] == selection['manifestSHA256']
    public_pins = {manifest: digest(manifest.read_bytes())}
    models = []
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        public_pins[path] = digest(path.read_bytes())
        models.extend(read(path)['models'])
    assert len(models) == len({m['uid'] for m in models}) == 7101
    assert not set(sources) & {m['uid'] for m in models}
    update = proposal['installedSupportUpdate']
    assert update['ownerUid'] == OWNER
    old = ROOT / '3d-viewer' / update['url']
    after_path = ROOT / update['source']
    after = take(PROPOSAL, after_path)
    assert public_pins[old] == update['beforeSHA256'] and digest(after_path.read_bytes()) == update['sha256']
    assert exact_owner_after(read(old), after, update)
    effective = [update['afterEntry'] if m['uid'] == OWNER else m for m in models]
    assert not any(r['blockers'] for r in inspect_dependencies(effective, catalogue['models'])['rows'])
    refs.extend(public_pins)
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        model = next(m for m in catalogue['models'] if m['uid'] == row['uid'])
        destination = LOCAL / model['asset']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(asset.read_bytes())
        assert destination.stat().st_size == model['bytes']
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == row['uid']) == row['source']['building']
        refs += [asset, tile]
    save(LOCAL / 'catalogue.json', catalogue)
    save(LOCAL / 'source-forms.json', [r['source']['building'] for r in selection['rows']])
    save(LOCAL / 'validation-forms.json', {r['uid']: r['source'] for r in selection['rows']})
    terrain = []
    for filename, suffix in [('unapproved-successor-terrain.json', 'parent'), ('unapproved-north-root-cell.json', 'north')]:
        path = BASE / ADMISSION / filename
        node = take(ADMISSION, path)
        entry = dict(source=str(path.relative_to(ROOT)), destination='city/data/' + BATCH + '-' + suffix + '.json',
                     sha256=digest(path.read_bytes()), resolution=node['cell'], area='Private exact original assembly')
        if suffix == 'parent':
            replacement = candidate['replacedParent']
            old_path = ROOT / '3d-viewer' / replacement['url']
            assert digest(old_path.read_bytes()) == replacement['sha256']
            public_pins[old_path] = replacement['sha256']
            refs.append(old_path)
            entry['replaces'] = replacement
        terrain.append(entry)
    root = ROOT / '3d-viewer/city/data/terrain.json'
    assert digest(root.read_bytes()) == candidate['additionalTopLevelPatch']['parentSHA256']
    public_pins[root] = digest(root.read_bytes())
    refs.append(root)
    config = dict(viewerURL='http://127.0.0.1:4177/city.html', stage=str(LOCAL.relative_to(ROOT))+'/',
        catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json', terrain=terrain,
        browserUids=list(sources), fitBox=True, captureDirectionByModel={u: [.5, .65, .7] for u in sources},
        jointUids=list(sources), nativeSupportUidsByModel={u: [p] for u, p in proposal['supportByUid'].items()},
        additionalRetainedUids=RETAINED, retainedNativeOwnViews=True, catalogueReplacements=[update],
        dependencyFallbackRetainedUids=[], retainedBuildingUids=[], diagnosticOnly=True, publication=False)
    tool = HERE / 'silvercord_retained_readiness_browser_v1_20261103.mjs'
    refs.append(tool)
    server = thread = None
    try:
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *unused):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 4177), functools.partial(Handler, directory=str(ROOT/'3d-viewer')))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        preflight = LOCAL / 'preflight-config.json'
        save(preflight, dict(**config, doc=str((BASE/BATCH).relative_to(ROOT))+'/'))
        subprocess.run(['node', str(tool), 'preflight', str(preflight.relative_to(ROOT))], cwd=ROOT, check=True)
        for width in [1280, 390]:
            assert reservations.owns(lease)
            path = LOCAL / ('browser-config-'+str(width)+'.json')
            save(path, dict(**config, viewportWidths=[width], failureTestUids=[],
                           doc=str((BASE/BATCH/str(width)).relative_to(ROOT))+'/'))
            (BASE/BATCH).mkdir(parents=True, exist_ok=True)
            with (BASE/BATCH/('browser-'+str(width)+'.log')).open('w') as log:
                result = subprocess.run(['node', str(tool), 'staged', str(path.relative_to(ROOT))], cwd=ROOT,
                    stdout=log, stderr=subprocess.STDOUT, timeout=1600,
                    env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'})
            save(BASE/BATCH/('command-'+str(width)+'.json'), dict(exitCode=result.returncode))
            assert result.returncode == 0 and read(BASE/BATCH/str(width)/'staged-browser.json')['passed']
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)
    for path, sha in public_pins.items():
        assert digest(path.read_bytes()) == sha, 'Public input changed during private preview'
    assert reservations.owns(lease)
    save(BASE/BATCH/'summary.json', dict(uids=list(sources), retainedNativeUids=RETAINED,
        diagnosticOnly=True, physicalAcceptance=False, installationApproved=False, visualAcceptance=False,
        publication=False, sourceGeometryChanges=0, sourcePoseChanges=0, publicInputsUnchanged=True,
        sourceViewports=[1280,390], fullRetainedTerrainNativeObligations=1228, fullRetainedFormObligations=5408,
        fullRetainedScopeBrowserApproval=False, atomicDenialRetryStillRequired=True,
        isolatedSupportOnlyMetadataProposal=True, diagnosticCameraPriorityOnly='landmark', scriptExternalAICalls=0))
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name != 'reservation.json')
    module('silvercord_private_six_part_browser_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-original-assembly-and-retained-owner-desktop-mobile-success-diagnostic',
        list(dict.fromkeys(refs)), read(BASE/BATCH/'summary.json'))


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        scope = read(BASE/SCOPE/'summary.json')
        forms = read(BASE/SCOPE/'full-parent-form-obligations.json.gz')
        selected = read(BASE/RUNTIME/'selection.json.gz')
        # Installed actors outside these observed sources are read-only inputs,
        # bound by the full scope and public-byte fences, not proposed mutations.
        # Lock every new original, retained browser witness, actual retained parent
        # target and changed terrain/server resource using the existing contract.
        replacement = read(BASE/CANDIDATE/'summary.json')['replacedParent']
        parent = read(ROOT/'3d-viewer'/replacement['url'])
        resources = {'building:'+u for u in [*RETAINED, *parent['meta']['targetUids']]}
        resources |= {'building:'+r['uid'] for r in selected['rows']}
        resources |= {'terrain:city/data/terrain.json', 'terrain:'+replacement['url'],
                      'server:127.0.0.1:4177', 'immutable-source-proof:'+BATCH}
        claim = reservations.claim('silvercord-private-six-part-'+str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL/'reservation.json', [sys.executable, __file__, '--owned'])
