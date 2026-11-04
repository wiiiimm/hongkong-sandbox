"""Freeze an exact single-point contact proof against current immutable terrain."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_terrain_point_contact_v1_20261025 import verify


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'scope', 'patch']: p.add_argument('--'+k, required=True)
    a = p.parse_args(); base = ROOT/'docs/astra-city/government-import'; out = base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs = [Path(__file__), HERE/'original_terrain_point_contact_v1_20261025.py']; pins = {}
    for n in [a.scope, a.patch]:
        _, pins[n] = authenticate(base/n); refs.append(base/n/'result.json')
    def take(n, path):
        assert digest(path.read_bytes()) == pins[n][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    scopepath = base/a.scope/'scope.json'; scope = take(a.scope, scopepath)
    receipt, _ = authenticate(base/a.patch)
    candidate = ROOT/receipt['candidate']['path']; patch = take(a.patch, candidate)
    parent = ROOT/'3d-viewer/city/data/terrain.json'; manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[a.scope][str(manifest.relative_to(ROOT))]
    assert digest(manifest.read_bytes()) == pins[a.patch][str(manifest.relative_to(ROOT))]
    assert digest(parent.read_bytes()) == pins[a.patch][str(parent.relative_to(ROOT))]
    refs += [parent, manifest]; urls = {r['url'] for r in read(manifest)['terrainPatches']}
    old, bindings = {}, []
    for contact in scope['terrainContacts']:
        url = contact['url']; assert url in urls
        path = ROOT/'3d-viewer'/url
        assert digest(path.read_bytes()) == pins[a.scope][str(path.relative_to(ROOT))]
        refs.append(path); old[url] = read(path)
        bindings.append(dict(url=url, path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    proof = verify(scope, patch, read(parent), old)
    result = dict(**proof, uids=scope['uids'], oldTerrainBindings=bindings,
                  candidateBinding=dict(path=str(candidate.relative_to(ROOT)), sha256=digest(candidate.read_bytes())),
                  scopeBinding=dict(path=str(scopepath.relative_to(ROOT)), sha256=digest(scopepath.read_bytes())),
                  parentBinding=dict(path=str(parent.relative_to(ROOT)), sha256=digest(parent.read_bytes())),
                  currentManifestSHA256=digest(manifest.read_bytes()))
    save(out/'summary.json', result)
    module('original_point_contact_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-original-terrain-single-corner-current-binding', refs, result)


if __name__ == '__main__': main()
