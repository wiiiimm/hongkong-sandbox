"""Exact installed original support acceptance; terrain diagnostics stay recorded."""
import importlib.util
import subprocess
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect

CONTACT_REASONS = {'ground-contact-unresolved', 'sampled-ground-gap-below-model-bottom'}


def resolve_contact(reasons, interface, foundation):
    """Only a complete strict interface and full compound foundation resolve gaps."""
    accepted = (interface.get('passed') is True and interface.get('samples', 0) > 0
                and interface.get('strictContacts') == interface.get('samples')
                and interface.get('wallIntersections') == 0 and not interface.get('unresolved')
                and foundation.get('strictFoundationAccepted') is True)
    return [r for r in reasons if not (accepted and r in CONTACT_REASONS)]


def compound_foundation(doc, local, row, triangles, ground, polygon, closure):
    hashes = {}
    def pinned(path):
        path = Path(path).resolve(); assert path.is_relative_to(ROOT)
        hashes[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        return read(path)
    prior = pinned(closure / 'support-inputs.json')
    pairs = [p for p in prior['pairs'] if p['uid'] == row['uid']]
    assert len(pairs) == 1
    pair = pairs[0]; support_uid = pair['supportUid']
    sources = {r['uid']: r for r in prior['sources']}
    support = sources[support_uid]
    manifest = pinned(ROOT / '3d-viewer/city/data/manifest.json')
    pointer = pinned(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    matches = []
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        catalogue = read(path)
        for entry in catalogue['models']:
            if entry['uid'] == support_uid:
                pinned(path)
                assert catalogue['rootTranslation'] == [-834500, 0, 816500]
                matches.append(({**entry, 'rootTranslation': catalogue['rootTranslation']}, path))
    assert len(matches) == 1
    entry, catalogue_path = matches[0]
    assert entry.get('publicationApproved') and entry.get('sourceIdentityReviewed')
    for key in ('uid', 'objectId', 'buildingCSUID', 'sha256', 'rootTranslation', 'worldBounds'):
        assert entry[key] == support['candidate']['entry'][key], ('Support identity/transform mismatch', key)
    assert entry.get('verticalPlacementOffsetHKPD', 0) == support['candidate']['entry'].get('verticalPlacementOffsetHKPD', 0) == 0
    asset = (catalogue_path.parent / entry['asset']).resolve()
    assert asset.is_relative_to(ROOT / '3d-viewer')
    hashes[str(asset.relative_to(ROOT))] = digest(asset.read_bytes())
    assert hashes[str(asset.relative_to(ROOT))] == entry['sha256']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        review = con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
                             (pointer['snapshotId'], support_uid)).fetchone()
    assert review == ('installed-verified', entry['sha256'])
    support = {**support, 'candidate': {**support['candidate'], 'path': str(asset.relative_to(ROOT))}}
    save(doc / 'support-inputs.json', {'pairs': pairs, 'sources': [row, support]})
    subprocess.run(['node', str(HERE / 'original-support-closure-interfaces.mjs'), str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, check=True)
    checks = read(doc / 'support-checks.json.gz'); assert len(checks['rows']) == 1
    interface = checks['rows'][0]
    assert interface['sourceSHA256'] == row['sourceSHA256'] and interface['supportSHA256'] == entry['sha256']
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        hashes[path] = sha
    spec = importlib.util.spec_from_file_location('current_support_foundation', HERE / 'xl-final-script-pass.py')
    final = importlib.util.module_from_spec(spec); spec.loader.exec_module(final)
    # The established decoder requires a hash-named local asset, copied verbatim.
    cached = local / 'assets' / (entry['sha256'] + '.glb.gz')
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(asset.read_bytes())
    assert digest(cached.read_bytes()) == entry['sha256']
    final.s.LOCAL = local
    decoder_row = {**support, 'modelId': entry['modelId'], 'triangles': entry['triangles'],
                   'native': {'model': {'worldBounds': entry['worldBounds']}}}
    support_triangles = final.s.glb_triangles(decoder_row)
    foundation = final.foundation_context(triangles, np.concatenate([ground, support_triangles]), polygon)
    strict = (foundation['completeTerrainTriangles'] == foundation['triangles']
              and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction'] == 0)
    hashes[str((HERE / 'xl-final-script-pass.py').relative_to(ROOT))] = digest((HERE / 'xl-final-script-pass.py').read_bytes())
    hashes[str(Path(__file__).relative_to(ROOT))] = digest(Path(__file__).read_bytes())
    proof = {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'supportUid': support_uid,
             'supportSHA256': entry['sha256'], 'supportCSUID': entry['buildingCSUID'],
             'snapshotId': pointer['snapshotId'], 'interface': interface['interface'],
             'foundation': {'strictFoundationAccepted': strict}, 'inputHashes': hashes,
             'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False}
    save(doc / 'installed-support-proof.json', proof)
    return foundation, proof


def record_resolution(doc, raw_policy, raw_diagnostics, proof):
    remaining_policy = resolve_contact(raw_policy, proof['interface'], proof['foundation'])
    remaining_diagnostics = resolve_contact(raw_diagnostics, proof['interface'], proof['foundation'])
    save(doc / 'support-ground-resolution.json', {
        'rawPolicyReasons': raw_policy, 'rawDiagnosticReasons': raw_diagnostics,
        'remainingPolicyReasons': remaining_policy, 'remainingDiagnosticReasons': remaining_diagnostics,
        'supportProofSHA256': digest((doc / 'installed-support-proof.json').read_bytes()),
        'metricsSHA256': digest((doc / 'metrics.json').read_bytes()),
        'diagnosticSHA256': digest((doc / 'diagnostic-resolution.json').read_bytes()),
        'qualification': 'Exact current installed original support replaces terrain-only low-rim gap diagnostics. All strict original interface contacts and full compound foundation required. Raw terrain diagnostics retained; no numerical limits changed.'})
    return remaining_policy, remaining_diagnostics


def verify_resolution(doc, raw_policy):
    proof = read(doc / 'installed-support-proof.json'); resolution = read(doc / 'support-ground-resolution.json')
    assert resolution['rawPolicyReasons'] == raw_policy
    assert resolution['supportProofSHA256'] == digest((doc / 'installed-support-proof.json').read_bytes())
    assert resolution['metricsSHA256'] == digest((doc / 'metrics.json').read_bytes())
    assert resolution['diagnosticSHA256'] == digest((doc / 'diagnostic-resolution.json').read_bytes())
    assert read(doc / 'diagnostic-resolution.json')['remaining'] == resolution['rawDiagnosticReasons']
    for path, sha in proof['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha, ('Installed support input changed', path)
    for raw, remaining in [('rawPolicyReasons', 'remainingPolicyReasons'), ('rawDiagnosticReasons', 'remainingDiagnosticReasons')]:
        assert resolution[remaining] == resolve_contact(resolution[raw], proof['interface'], proof['foundation'])
        assert not resolution[remaining]
    assert proof['modelGeometryChanges'] == proof['scriptExternalAICalls'] == 0
    return proof
