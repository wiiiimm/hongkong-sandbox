"""Fresh disjoint original-TIN proposals; no installation or approval."""
import argparse
import json
import subprocess
import sys
import uuid
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import reservations

BATCH = 'government-islands-peng-chau-disjoint-terrain-20261106-v1'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH


def main():
    assert not DOC.exists() and not LOCAL.exists()
    old = module('islands_disjoint_existing', HERE / 'tai-o-terrain-pass.py')
    parent = read(ROOT / '3d-viewer/city/data/terrain.json')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = sha(manifest_path); manifest = read(manifest_path)
    installed = {r['uid'] for u in manifest['officialModelCatalogues'] for r in read(ROOT / '3d-viewer' / u)['models']}
    patches = [read(ROOT / '3d-viewer' / p['url']) for p in manifest['terrainPatches']]
    source = ROOT / 'docs/astra-city/government-import/government-islands-peng-chau-source-terrain-20261106/check-selection.json.gz'
    prior_path = ROOT / 'docs/astra-city/government-import/government-islands-peng-chau-terrain-20261106-v1/terrain-stage.json'
    selection = {r['uid']: r for r in read(source)['rows']}
    chosen, excluded = [], []
    for uid in read(prior_path)['sourceUids']:
        if uid in installed: continue
        cells = old.resolve.rectangle_for(selection[uid]['candidate']['entry']['worldBounds'], parent)
        if any(old.terrain_helpers.overlap(cells, p['coarseCells']) for p in patches):
            excluded.append({'uid': uid, 'reason': 'retain-installed-terrain'}); continue
        if any(old.terrain_helpers.overlap(cells, row['cells']) for row in chosen):
            excluded.append({'uid': uid, 'reason': 'next-disjoint-wave'}); continue
        chosen.append({'uid': uid, 'cells': cells})
    assert len(chosen) == 31 and sha(manifest_path) == manifest_sha
    save(DOC / 'nomination.json', {'uids': [r['uid'] for r in chosen], 'domains': chosen,
        'manifestSHA256': manifest_sha, 'sourceSelectionSHA256': sha(source),
        'priorStageSHA256': sha(prior_path), 'excluded': excluded, 'publication': False,
        'qualification': 'Historical positive source-TIN checks nominate only. Actual TIN/contact, identity, neighbours, runtime and browser must pass again.'})
    LOCAL.mkdir(parents=True)
    resources = ['building:' + r['uid'] for r in chosen] + ['terrain:city/data/terrain.json']
    claim = reservations.claim('codex-islands-disjoint-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
    assert claim['ok'], 'Existing owner; no takeover'
    receipt = json.loads(json.dumps(claim['reservation'], default=str))
    save(LOCAL / 'reservation.json', receipt); save(LOCAL / 'reservations.json', [receipt])
    try:
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
            '--lease-file', str(LOCAL / 'reservation.json'), '--ttl', '3600', '--', sys.executable,
            str(HERE / 'islands_disjoint_terrain_stage_v1_20261106.py')], cwd=ROOT, check=True)
    finally:
        if reservations.owns(receipt): reservations.release(receipt)


if __name__ == '__main__': main()
