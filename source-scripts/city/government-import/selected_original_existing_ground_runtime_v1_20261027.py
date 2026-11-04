"""Capture unchanged selected originals against the actual existing viewer ground.

No private terrain replacement, acceptance, geometry edits or catalogue writes.
"""
import argparse
from pathlib import Path
import subprocess
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'lease']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture])
    lease = read(Path(a.lease))
    assert reservations.owns(lease)
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / a.batch, HERE / 'local' / a.batch
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(base / a.capture)
    source = base / a.capture / 'selection.json.gz'
    assert digest(source.read_bytes()) == pins[str(source.relative_to(ROOT))]
    selection = read(source)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    uids = [r['uid'] for r in selection['rows']]
    assert uids and len(set(uids)) == len(uids)
    assert {'building:' + u for u in uids} <= set(lease['resources'])
    refs = [Path(__file__), base / a.capture / 'result.json', source, manifest]
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        entry = row['candidate']['entry']
        assert digest(raw) == row['sourceSHA256'] == entry['sha256']
        target = local / entry['asset']
        assert target.resolve().is_relative_to(local.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['candidate'] = dict(path=str(target.relative_to(ROOT)), entry=entry)
        refs.extend([asset, target])
    save(doc / 'selection.json.gz', selection)
    tool = HERE / 'acceptance-metrics-multi-retained.mjs'
    command = ['node', str(tool), '--selection', str((doc / 'selection.json.gz').relative_to(ROOT)),
               '--candidates', str(local.relative_to(ROOT)), '--out', str((doc / 'metrics.json').relative_to(ROOT)),
               '--geometry-out', str((local / 'runtime-geometry.json.gz').relative_to(ROOT))]
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    metrics = read(doc / 'metrics.json')
    geometry = read(local / 'runtime-geometry.json.gz')
    assert {r['uid'] for r in metrics['rows']} == set(uids)
    assert {r['uid'] for r in geometry['rows']} == {r['uid'] for r in metrics['rows'] if not r.get('error')}
    for path, sha in metrics['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    assert reservations.owns(lease)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(uids=uids, rows=metrics['rows'], errors=sum(bool(r.get('error')) for r in metrics['rows']),
                  sourceGeometryChanges=0, sourcePoseChanges=0, terrainGeometryChanges=0,
                  physicalAcceptance=False, identityAccepted=False, installationApproved=False,
                  publication=False, qualification='Actual production decoder and existing viewer terrain, '
                  'with complete per-source drawn-ground capture. Runtime measurements only; raised sources '
                  'still need original supporting structures, identity/placement and full acceptance.')
    save(doc / 'summary.json', result)
    refs.extend([tool, local / 'runtime-geometry.json.gz'])
    module('existing_ground_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'selected-original-existing-drawn-ground-runtime-diagnostic', refs, result)
    print(dict(models=len(uids), errors=result['errors']), flush=True)


if __name__ == '__main__':
    main()
