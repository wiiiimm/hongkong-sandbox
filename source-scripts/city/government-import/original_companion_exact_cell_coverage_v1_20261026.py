"""Exact four-world companion coverage of a selected target's geographic cell.

Synthetic cell triangles are diagnostic probes only. No model is emitted or
edited, and companion coverage does not establish source ownership or approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_20261009 import exact_coverage


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','selection','attributes','identity','uid','provider']:
        p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.uid!=a.provider and a.batch.startswith('government-xl-') and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs,pins=[Path(__file__)],{}
    def take(batch,file):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/file;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(a.selection,'selection.json.gz');by={r['uid']:r for r in selection['rows']}
    assert {a.uid,a.provider}<=set(by)
    target,provider=by[a.uid],by[a.provider]
    identity=take(a.identity,a.uid.split('/')[1]+'/identity.json')
    assert identity['sourceSHA256']==target['sourceSHA256']
    cell=identity['geographicCell']['worldXZBounds'];x0,z0,x1,z1=cell
    assert x1-x0==z1-z0==1 and identity['geographicCell']['targetCoversWholeCell']
    attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified']
    attr=next(r for r in attrs['rows']if r['uid']==a.provider)
    assets={}
    for row in [target,provider]:
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);assets[row['uid']]=asset
    assert attr['sourceSHA256']==provider['sourceSHA256']
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(assets[a.provider].read_bytes()),**{
        n:np.asarray(attr[f],dtype='<f8').reshape(-1,3)[index]for n,f in [
            ('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),
            ('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
    probes=np.asarray([[[x0,0,z0],[x1,0,z0],[x1,0,z1]],[[x0,0,z0],[x1,0,z1],[x0,0,z1]]],dtype='<f8')
    rows=[]
    for mode,tri in modes.items():
        assert len(tri)==provider['triangles']
        halves=[exact_coverage(face,tri)for face in probes]
        rows.append(dict(mode=mode,providerWorldSHA256=digest(tri.tobytes()),completeProviderFaces=len(tri),
                         halves=halves,wholeTargetCellExactlyCovered=all(r['exactProjectionCovered']for r in halves)))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid,a.provider],targetUid=a.uid,providerUid=a.provider,
                sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in [target,provider]},
                worldXZCellBounds=cell,rows=rows,allFourWorldTargetCellsCovered=all(r['wholeTargetCellExactlyCovered']for r in rows),
                sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,
                installationApproved=False,publication=False,
                qualification='Exact rational closed-facet coverage of both halves of the unchanged one-metre target cell, using every original provider face in each coordinate representation. No tolerance, buffer, source ownership, physical support, source replacement or acceptance credit. Synthetic probes are not model assets.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_projection_coverage_20261009.py'])
    module('companion_exact_cell_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch,'exact-four-world-original-companion-target-cell-coverage',refs,result)
    print(dict(target=a.uid,provider=a.provider,allFourWorldCellsCovered=result['allFourWorldTargetCellsCovered']),flush=True)


if __name__=='__main__':main()
