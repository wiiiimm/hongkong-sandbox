"""Prove missing legacy originalGeometryOnly metadata; no approval transfer.

Require canonical source entry, exact source bytes/current form and an exact
production-loader geometry replay. Never repair an explicitly false flag.
"""
import argparse
from copy import deepcopy
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def check_entry(row, canonical):
    if 'originalGeometryOnly' in row:
        assert row['originalGeometryOnly'] is True, 'Explicit non-original flag'
    expected = deepcopy(canonical)
    expected['asset'] = row['candidate']['entry']['asset']
    assert expected == row['candidate']['entry'], 'Noncanonical original source entry'
    assert row['uid'] == expected['uid']
    assert row['sourceSHA256'] == expected['sha256'] == row['native']['model']['asset']['sha256']
    assert expected['rootTranslation'] == [-834500, 0, 816500]
    assert row['triangles'] == expected['triangles'] == row['native']['model']['triangles']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--capture', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    capture = base / args.capture
    _, pins = authenticate(capture)
    refs = [Path(__file__), capture / 'result.json']
    for name, sha in pins.items():
        path = ROOT / name
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    selection_path = capture / 'selection.json.gz'
    geometry_path = HERE / 'local' / args.capture / 'runtime-geometry.json.gz'
    for path in [selection_path, geometry_path]:
        assert str(path.relative_to(ROOT)) in pins
    selection, previous = read(selection_path), read(geometry_path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    canonical = module('normalise_original_source_entry', HERE / 'xl-next-support-recovery-20261005.py')
    refs.extend([HERE / 'xl-next-support-recovery-20261005.py', HERE.parent / 'enhancement-screening/shape_prepare.py', manifest])
    rows = selection['rows']
    assert 0 < len(rows) <= 40 and len({r['uid'] for r in rows}) == len(rows)
    for row in rows:
        expected, _ = canonical.diagnostic_entry(row['native'], row['source']['building'])
        check_entry(row, expected)
        source = ROOT / '3d-viewer' / row['source']['tile']
        assert [b for b in read(source)['buildings'] if b['uid'] == row['uid']] == [row['source']['building']]
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        target = local / row['candidate']['entry']['asset']
        assert target.resolve().is_relative_to(local.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['candidate']['path'] = str(target.relative_to(ROOT))
        refs.extend([source, asset, target])
    # Replay the same production loader, rather than compare different math
    # libraries using a newly invented coordinate tolerance.
    save(doc / 'selection-before-proof.json.gz', selection)
    tool = HERE / 'acceptance_metrics_multi_retained_v2.mjs'
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), '--selection', str((doc / 'selection-before-proof.json.gz').relative_to(ROOT)), '--candidates', str(local.relative_to(ROOT)), '--out', str((doc / 'metrics.json').relative_to(ROOT)), '--geometry-out', str((local / 'runtime-geometry.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    replay = read(local / 'runtime-geometry.json.gz')
    assert replay['rows'] == previous['rows'], 'Production source/ground/geometry replay differs'
    old_selection_key = str(selection_path.relative_to(ROOT))
    new_selection_key = str((doc / 'selection-before-proof.json.gz').relative_to(ROOT))
    assert previous['inputHashes'][old_selection_key] == digest(selection_path.read_bytes())
    assert replay['inputHashes'][new_selection_key] == digest((doc / 'selection-before-proof.json.gz').read_bytes())
    assert {k: v for k, v in previous['inputHashes'].items() if k != old_selection_key} == {k: v for k, v in replay['inputHashes'].items() if k != new_selection_key}, 'Production input hashes changed'
    metrics = read(doc / 'metrics.json')
    assert len(metrics['rows']) == len(rows)
    for item in metrics['rows']:
        assert not item.get('error') and item['sourcePreserved'] is True
    for name, sha in metrics['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    for row in rows:
        row['originalGeometryOnly'] = True
    save(doc / 'selection.json.gz', selection)
    for name, sha in pins.items():
        assert digest((ROOT / name).read_bytes()) == sha
    result = dict(uids=sorted(r['uid'] for r in rows), canonicalEntriesVerified=True, exactProductionReplay=True, installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Legacy provenance compatibility only. Exact original source binding and complete production runtime/ground replay; no identity, placement or publication approval.')
    save(doc / 'summary.json', result)
    refs.extend([tool, local / 'runtime-geometry.json.gz'])
    module('normalise_original_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'original-capture-provenance-compatibility', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
