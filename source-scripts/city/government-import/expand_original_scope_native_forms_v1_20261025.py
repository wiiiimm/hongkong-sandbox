"""Add every nominated native's exact current source form to model-only obligations."""
import argparse, copy
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'scope', 'inventory']: p.add_argument('--' + key, required=True)
    a = p.parse_args(); base = ROOT / 'docs/astra-city/government-import'; out = base / a.batch
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.scope, a.inventory])
    assert not out.exists(); refs, pins = [Path(__file__)], {}
    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]; refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    scope = copy.deepcopy(take(a.scope, 'summary.json'))
    inventory = take(a.inventory, 'complete-bounds.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; sha = digest(manifest.read_bytes())
    assert sha == scope['currentManifestSHA256'] == pins[a.inventory][str(manifest.relative_to(ROOT))]
    refs.append(manifest); native = {r['uid']: r for r in inventory['rows']}
    wanted = {n['uid'] for r in scope['rows'] for n in r['nearbyNativeActors']}; forms = {}
    for tile in read(manifest)['tiles']:
        if not wanted - forms.keys(): break
        path = ROOT / '3d-viewer' / tile['url']; key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == inventory['currentFormTileHashes'][key]
        for f in read(path)['buildings']:
            if f['uid'] in wanted:
                assert f['uid'] not in forms
                forms[f['uid']] = dict(building=f, tile=tile['url'], tileSHA256=digest(path.read_bytes()))
                refs.append(path)
    assert set(forms) == wanted
    additions = []
    for row in scope['rows']:
        assert row['currentNativeActorsChecked'] == len(native)
        filename = row['uid'].split('/')[1] + '-forms.json.gz'
        existing = take(a.scope, filename); byuid = {f['building']['uid']: f for f in existing}
        assert len(byuid) == len(existing)
        added = []
        for n in row['nearbyNativeActors']:
            uid = n['uid']; assert native[uid]['sourceSHA256'] == n['sourceSHA256']
            assert native[uid]['completeFourWorldBounds'] == n['completeFourWorldBounds']
            if uid in byuid: assert byuid[uid] == forms[uid]
            else: byuid[uid] = forms[uid]; added.append(uid)
        # Original nomination counts/bounds stay intact; additions are explicit.
        row['additionalRetainedNativeFormUids'] = sorted(added)
        row['completeCurrentObligationForms'] = len(byuid)
        save(out / filename, list(byuid.values())); additions.append(dict(uid=row['uid'], added=sorted(added)))
    assert digest(manifest.read_bytes()) == sha
    scope.update(retainedNativeFormsAdded=additions, installationApproved=False, publication=False)
    save(out / 'summary.json', scope)
    module('expanded_native_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'model-only-complete-nominated-native-form-obligations', list(dict.fromkeys(refs)), scope)


if __name__ == '__main__': main()
