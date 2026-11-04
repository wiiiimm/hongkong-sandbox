"""Prove an empty current native-contact set from complete four-world bounds.

Reject any nominated native actor. Nonempty cases must use finite-contact tools.
This produces diagnostic evidence only, never identity or installation approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','scope','runtime','attributes','inventory']:p.add_argument('--'+key,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take(a.scope,'summary.json');selection=take(a.runtime,'selection.json.gz')
    attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    attrs={r['uid']:r for r in attrs['rows']};inventory=take(a.inventory,'complete-bounds.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes())
    assert sha==selection['manifestSHA256']==scope['currentManifestSHA256']==pins[a.inventory][str(manifest.relative_to(ROOT))];refs.append(manifest)
    natives=inventory['rows'];assert len(natives)==len({r['uid'] for r in natives})
    assert set(scope['uids'])=={r['uid'] for r in selection['rows']}
    proofs=[]
    for source in selection['rows']:
        uid=source['uid'];r=next(r for r in scope['rows'] if r['uid']==uid);attr=attrs[uid]
        assert r['currentNativeActorsChecked']==len(natives) and r['nearbyNativeActors']==[]
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256']==r['sourceSHA256'];refs.append(asset)
        xyz=[decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)]
        xyz += [np.asarray(attr[k]).reshape(-1,3) for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]
        points=np.concatenate(xyz);assert np.isfinite(points).all();lo,hi=points.min(0),points.max(0)
        assert [lo.tolist(),hi.tolist()]==r['completeSourceFourWorldBounds']
        for native in natives:
            assert native['uid']!=uid
            bounds=np.asarray(native['completeFourWorldBounds']).reshape(-1,3);assert np.isfinite(bounds).all()
            assert not (np.all(hi+.5>=bounds.min(0)) and np.all(bounds.max(0)+.5>=lo)),native['uid']
        proofs.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],completeSourceFourWorldBounds=[lo.tolist(),hi.tolist()],currentNativeActorsChecked=len(natives),closedBoxSeparationMarginMetres=.5))
    result=dict(uids=scope['uids'],rows=[],emptyNativeContactSetProved=True,boundsProofs=proofs,currentManifestSHA256=sha,sourceGeometryChanges=0,installationApproved=False,physicalAcceptance=False,qualification='Every current installed native complete four-world box is disjoint from the complete source box with the existing0.5m nomination margin. Empty finite-contact set follows by spatial separation, not omission of nominated pairs. Any nominated actor rejects this collector.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'selected_original_model_only_scope_v1_20261023.py'])
    module('empty_native_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-empty-native-contact-set-bounds-proof',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
