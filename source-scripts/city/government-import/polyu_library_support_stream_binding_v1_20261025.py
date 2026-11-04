"""Independently rebind archived library streams to current unchanged loader and bounds."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-library-support-current-stream-binding-v1-20261025'
NATIVE='government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025'
SUPPORT='government-xl-polyu-lee-shau-kee-library-support-v2-20261025'
INVENTORY='government-xl-after-school-current-inventory-v1-20261025'
UID='landsd/305793:0'


def main():
    out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(name,file):
        if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        p=BASE/name/file;assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    probe=take(SUPPORT,'summary.json')
    n=next(r for r in take(NATIVE,'native-input.json.gz')['rows']if r['uid']==UID)
    a=next(r for r in take(NATIVE,'native-attributes.json.gz')['rows']if r['uid']==UID)
    bounds=next(r for r in take(INVENTORY,'complete-bounds.json.gz')['rows']if r['uid']==UID)
    assert bounds['sourceSHA256']==a['sourceSHA256']==n['entry']['sha256']
    assert bounds['completeFourWorldBounds'][1:]==[a[k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
    modules={p:s for p,s in pins[NATIVE].items()if p.startswith('3d-viewer/')and p.endswith('.js')}
    assert '3d-viewer/city/official-model-assets.js' in modules
    # Archived native metrics load assets directly, without the runtime manager.
    # Verify every consumed archived module; bind the current manager separately
    # to the fresh independently verified full installed inventory.
    manager=ROOT/'3d-viewer/city/official-models.js'
    assert digest(manager.read_bytes())==pins[INVENTORY][str(manager.relative_to(ROOT))]
    refs.append(manager)
    for p,s in modules.items():assert digest((ROOT/p).read_bytes())==s;refs.append(ROOT/p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==probe['currentManifestSHA256'];refs.append(manifest)
    cat=ROOT/n['cataloguePath'];assert next(r for r in read(cat)['models']if r['uid']==UID)==n['entry'];refs.append(cat)
    asset=ROOT/n['path'];assert digest(asset.read_bytes())==n['entry']['sha256'];refs.append(asset)
    assert all(r['supportUid']==UID and r['supportSHA256']==n['entry']['sha256']for r in probe['rows'])
    result=dict(uids=probe['uids'],currentManifestSHA256=probe['currentManifestSHA256'],installedNativeUid=UID,installedNativeSHA256=n['entry']['sha256'],currentEntryExactlyUnchanged=True,currentFourStreamBoundsExactlyRebound=True,unchangedCurrentRendererModules=len(modules),nativeStreamReuseVerified=True,sourceGeometryChanges=0,nativeMetadataChanges=0,installationApproved=False,physicalAcceptance=False,qualification='Independent current exact catalogue entry, immutable original bytes, complete renderer module hashes and fresh6929inventory four-stream bounds match the archived library coordinate evidence. This rebinds the source-only support probe; it does not transfer terrain, architectural, support or publication approval.')
    save(out/'summary.json',result)
    module('polyu_native_stream_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-unchanged-installed-library-four-stream-support-evidence-binding',refs,result)


if __name__=='__main__':main()
