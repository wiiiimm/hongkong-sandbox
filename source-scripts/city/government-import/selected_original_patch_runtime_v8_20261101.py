# V8 extends only the bounded diagnostic selection capacity to24.
# Per-model runtime budgets, exact source pins, complete patch target inclusion,
# terrain scope, native input and publication prohibitions remain unchanged.
"""Capture actual renderer geometry for an explicitly scoped private terrain candidate with up to24 companion originals."""
import argparse
import subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--patch', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--scope', help='Authenticated complete additive terrain domain scope')
    parser.add_argument('--uid', action='append', help='Explicit companion originals to capture with the same private terrain')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    patchdoc, cap = base / args.patch, base / args.capture
    receipt, pp = authenticate(patchdoc)
    _, cp = authenticate(cap)
    refs = [Path(__file__), patchdoc / 'result.json', cap / 'result.json']
    pins = {}
    for bound in (pp, cp):
        for name, sha in bound.items():
            assert name not in pins or pins[name] == sha
            assert digest((ROOT / name).read_bytes()) == sha
            pins[name] = sha
            refs.append(ROOT / name)
    assert receipt['status'] == 'private-terrain-validator-passed'
    candidate = receipt['candidate']
    patchpath = ROOT / candidate['path']
    assert digest(patchpath.read_bytes()) == candidate['sha256']
    refs.append(patchpath)
    sourcepath = cap / 'selection.json.gz'
    assert digest(sourcepath.read_bytes()) == cp[str(sourcepath.relative_to(ROOT))]
    refs.append(sourcepath)
    wanted = set(args.uid or receipt['uids'])
    assert set(receipt['uids']) <= wanted and len(wanted)==len(args.uid or receipt['uids']) and len(wanted)<=24
    rows = [r for r in read(sourcepath)['rows'] if r['uid'] in wanted]
    assert len(rows) == len(wanted)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    current_manifest = digest(manifest.read_bytes())
    refs.append(manifest)
    for row in rows:
        source = row['source']
        tile = ROOT / '3d-viewer' / source['tile']
        current = [b for b in read(tile)['buildings'] if b['uid'] == row['uid']]
        assert current == [source['building']]
        refs.append(tile)
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        entry = row['candidate']['entry']
        assert entry['sha256'] == row['sourceSHA256'] and entry['uid'] == row['uid']
        target = local / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        refs.extend([asset, target])
        row['candidate'] = dict(path=str(target.relative_to(ROOT)), entry=entry)
    save(doc / 'selection.json.gz', dict(rows=rows, manifestSHA256=current_manifest))
    patch = read(patchpath)
    scopepath = patchdoc / 'scope.json'
    assert digest(scopepath.read_bytes()) == pp[str(scopepath.relative_to(ROOT))]
    refs.append(scopepath)
    replacements=[]
    current=read(manifest);urls={r['url']for r in current['terrainPatches']}
    for old in receipt.get('replacedNativeTerrain',[]):
        assert old['url']in urls
        path=ROOT/'3d-viewer'/old['url'];assert digest(path.read_bytes())==old['sha256']
        prior=read(path);assert prior['meta']['targetUids']==old['targetUids']and prior['coarseCells']==old['coarseCells']
        assert set(prior['meta']['targetUids'])<=set(patch['meta']['targetUids'])
        assert prior['meta']['parentTerrain']==patch['meta']['parentTerrain']and prior['meta']['parentSha256']==patch['meta']['parentSha256']
        a,b,c,d=prior['coarseCells'];aa,bb,cc,dd=patch['coarseCells'];assert aa<=a<c<=cc and bb<=b<d<=dd
        replacements.append(dict(url=old['url'],sha256=old['sha256'],retainedUids=old['targetUids']));refs.append(path)
    if replacements:
        binding={'replaces':replacements[0]}if len(replacements)==1 else {'replacesMany':replacements}
    else:
        assert args.scope,'An additive candidate requires complete current domain proof'
        scopedoc=base/args.scope
        scope_receipt,scope_pins=authenticate(scopedoc)
        scoped=scopedoc/'scope.json'
        assert digest(scoped.read_bytes())==scope_pins[str(scoped.relative_to(ROOT))]
        assert scope_pins[str(manifest.relative_to(ROOT))]==current_manifest
        assert scope_pins[str(patchpath.relative_to(ROOT))]==candidate['sha256']
        proof=read(scoped)
        assert proof['positiveAreaTerrainOverlaps']==0 and not proof['terrainContacts']
        assert set(proof['uids'])==set(receipt['uids'])==set(patch['meta']['targetUids'])
        assert not receipt.get('replacedNativeTerrain')
        refs.extend([scopedoc/'result.json',scoped]);binding={}
    save(doc / 'terrain-candidates.json', [dict(**candidate, **binding, uids=sorted(wanted), bounds=read(scopepath)['bounds'], triangles=len(patch['nativeMesh']['index']) // 3)])
    command = ['node', str(HERE / 'acceptance_metrics_multi_retained_v2.mjs'), '--selection', str((doc / 'selection.json.gz').relative_to(ROOT)), '--candidates', str(local.relative_to(ROOT)), '--terrain-candidates', str((doc / 'terrain-candidates.json').relative_to(ROOT)), '--out', str((doc / 'metrics.json').relative_to(ROOT)), '--geometry-out', str((local / 'runtime-geometry.json.gz').relative_to(ROOT))]
    with (doc / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    metrics = read(doc / 'metrics.json')
    assert len(metrics['rows']) == len(rows)
    for path, sha in metrics['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == current_manifest
    for name, sha in pins.items():
        assert digest((ROOT / name).read_bytes()) == sha
    geometrypath = local / 'runtime-geometry.json.gz'
    geometry = {r['uid']: r for r in read(geometrypath)['rows']}
    final = module('selected_patch_foundation', HERE / 'xl-final-script-pass.py')
    summary = []
    for row in rows:
        uid = row['uid']
        if uid not in geometry:
            summary.append(dict(uid=uid, status='runtime-error', metric=next(r for r in metrics['rows'] if r['uid'] == uid)))
            continue
        g = geometry[uid]
        assert g['sourceSHA256'] == row['sourceSHA256']
        tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
        b = row['source']['building']
        foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
        save(doc / (uid.split('/')[1] + '.json'), dict(uid=uid, foundation=foundation))
        summary.append(dict(uid=uid, status='captured', triangles=len(tri), **{k: foundation[k] for k in ['completeTerrainTriangles', 'fullyBuriedTriangles', 'fullyBuriedUpwardTriangles', 'minimumGapM']}))
    result = dict(uids=sorted(wanted), rows=summary, installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Private actual-renderer geometry and whole-source foundation diagnostics only. Tower support, identity, neighbours and publication remain separate.')
    save(doc / 'summary.json', result)
    refs.extend([HERE/'terrain-replacements.mjs',geometrypath, HERE / 'acceptance_metrics_multi_retained_v2.mjs', HERE / 'xl-final-script-pass.py'])
    module('selected_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-private-original-patch-runtime', list(dict.fromkeys(refs)), result)
    print(summary, flush=True)


if __name__ == '__main__':
    main()
