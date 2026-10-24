"""Prove an unchanged original horizontal root heading; never grant identity approval."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from original_source_ownership import document,graph_reasons
from miami_original_yaw_root_20261009 import frame_measurement
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','identity','capture','uid']:parser.add_argument('--'+key,required=True)
    args=parser.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [args.batch,args.identity,args.capture])
    base=ROOT/'docs/astra-city/government-import';out=base/args.batch;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(args.capture,base/args.capture/'selection.json.gz')
    assert sum(r['uid']==args.uid for r in selection['rows'])==1
    row=next(r for r in selection['rows']if r['uid']==args.uid)
    prior=take(args.identity,base/args.identity/(args.uid.split('/')[1]+'/identity.json'))
    assert prior['sourceSHA256']==row['sourceSHA256']and prior['exactCurrentComponentRoute']['qualified']
    assert 'original-unit-hkpd-root-pose'in prior['reasons']
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
    assert digest(raw)==row['sourceSHA256']==row['native']['model']['asset']['sha256'];refs.append(asset)
    doc=document(raw);tri=decode_original_world_triangles(raw)
    assert len(tri)==row['triangles']and graph_reasons(doc,row['modelId'],len(tri))==['original-unit-hkpd-root-pose']
    root=doc['nodes'][doc['scenes'][0]['nodes'][0]]
    frame=frame_measurement(root['matrix'],root['matrix'])
    bounds=np.array([tri.min((0,1)),tri.max((0,1))]);error=float(np.max(np.abs(bounds-np.array(row['native']['model']['worldBounds']))))
    assert frame['passed']and error<.002
    proof=dict(uid=args.uid,sourceSHA256=row['sourceSHA256'],originalRoot=root,legacyIdentityReasons=prior['reasons'],frame=frame,
        completeNativeBoundsErrorM=error,sourceBoundRootFramePassed=True,
        remainingIdentityReasons=[r for r in prior['reasons']if r!='original-unit-hkpd-root-pose'],
        sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,installationApproved=False,
        qualification='Source-bound unit horizontal yaw/HKPD-up diagnostic only, using the unchanged authored matrix and whole-source/native bounds. Remaining footprint/cell/identity, physical and runtime checks are not waived. No root matrix, source vertex or generic identity policy was changed.')
    save(out/'proof.json',proof)
    refs.extend(HERE/n for n in ['original_source_ownership.py','miami_original_yaw_root_20261009.py','exact_packed_world_geometry_20261009.py'])
    module('original_unit_yaw_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'source-bound-original-unit-yaw-context-no-identity-approval',refs,dict(uids=[args.uid],proof=proof,installationApproved=False))
    print(dict(sourceBoundRootFramePassed=True,boundsErrorM=error,remainingIdentityReasons=proof['remainingIdentityReasons']),flush=True)


if __name__=='__main__':main()
