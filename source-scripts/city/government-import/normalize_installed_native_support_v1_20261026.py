"""Package one authenticated installed-support diagnostic without changing its verdict."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch','checks','runtime','attributes','uid','native']:
        p.add_argument('--'+key, required=True)
    a = p.parse_args(); base = ROOT/'docs/astra-city/government-import'; out = base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs = [Path(__file__)]; pins = {}
    def take(batch, name, local=False):
        if batch not in pins:
            pins[batch] = authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        path = (HERE/'local'/batch if local else base/batch)/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selected = take(a.runtime,'selection.json.gz'); source = next(r for r in selected['rows'] if r['uid']==a.uid)
    attr = next(r for r in take(a.attributes,'attributes.json.gz')['rows'] if r['uid']==a.uid)
    checks = take(a.checks,'summary.json'); entry = checks['installedNativeEntry']
    assert a.uid != a.native == entry['uid']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == checks['currentManifestSHA256'] == selected['manifestSHA256']; refs.append(manifest)
    matches = []
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url
        for m in read(path)['models']:
            if m['uid']==a.native: matches.append((m,path))
    assert len(matches)==1 and matches[0][0]==entry
    cat = matches[0][1]; native_asset = cat.parent/entry['asset']; asset = ROOT/source['candidate']['path']
    assert digest(native_asset.read_bytes())==entry['sha256']
    assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256']; refs.extend([cat,native_asset,asset])
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds = dict(original=decode_original_world_triangles(asset.read_bytes()))
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]: worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
    rows = []
    for mode,tri in worlds.items():
        raw = take(a.checks,a.uid.split('/')[1]+'-'+mode+'.json.gz')
        inp = take(a.checks,a.uid.split('/')[1]+'/'+mode+'/input.json.gz',True)
        support = np.asarray(inp['podium'],dtype='<f8'); actual = np.asarray(inp['rows'][0]['position'],dtype='<f8').reshape(-1,3,3)
        assert np.array_equal(actual,tri) and raw['sourceWorldSHA256']==digest(tri.tobytes())
        assert support.shape==(entry['triangles'],3,3) and raw['supportWorldSHA256']==digest(support.tobytes())
        assert raw['sourceSHA256']==source['sourceSHA256'] and raw['supportSHA256']==entry['sha256']
        if mode=='original': assert np.array_equal(support,decode_original_world_triangles(native_asset.read_bytes()))
        # Copy the complete pinned arrays/verdict verbatim. No source or native
        # entry is added to a replacement selection or reapproved.
        save(out/mode/'input.json.gz',inp)
        row = dict(mode=mode,sourceWorldSHA256ByUid={a.uid:raw['sourceWorldSHA256'],a.native:raw['supportWorldSHA256']},support=raw['strictSupport'],compoundFoundation=raw['compoundFoundation'],passed=next(r['strictPassed'] for r in checks['rows'] if r['uid']==a.uid and r['mode']==mode))
        save(out/mode/'diagnostic.json',row); rows.append(row)
    result = dict(uids=[a.uid,a.native],supportedUid=a.uid,supportUid=a.native,installedSupportUid=a.native,
        sourceSHA256ByUid={a.uid:source['sourceSHA256'],a.native:entry['sha256']},rows=rows,
        allFourModesPassed=all(r['passed'] for r in rows),currentManifestSHA256=digest(manifest.read_bytes()),
        installedNativeEntry=entry,rawVerdictsUnchanged=True,sourceGeometryChanges=0,nativeMetadataChanges=0,
        physicalSupportAccepted=False,installationApproved=False,publication=False,
        qualification='Verbatim packaging of authenticated one-source installed-native support inputs and canonical strict/compound verdicts. Source arrays are checked against current four-world attributes and native original against actual source bytes. No approval, source-selection relabelling or geometry change. Pure diagnostic consumers must retain all raw failures.')
    save(out/'summary.json',result); refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('normalize_installed_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-installed-support-diagnostic-schema-binding-without-verdict-change',refs,result)


if __name__=='__main__': main()
