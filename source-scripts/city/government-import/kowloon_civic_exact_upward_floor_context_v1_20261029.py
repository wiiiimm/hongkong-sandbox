"""Reuse exact numeric streams to nominate original low upward facets, not architecture."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-kowloon-city-civic-five-after-fuying-';UID='landsd/82291:0'
def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=PREFIX+'three-private-ground-v1-20261029';attrs=PREFIX+'attributes-v1-20261029';old='government-xl-kowloon-city-civic-podium-low-faces-v1-20261029'
    selection=take(runtime,BASE/runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID)
    geometry=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']==UID)
    attributes=take(attrs,BASE/attrs/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attr=next(r for r in attributes['rows']if r['uid']==UID)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==geometry['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    original=decode_original_world_triangles(asset.read_bytes());assert len(original)==15085
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':original,**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    ground=np.asarray(geometry['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);facts=[];nominated=set()
    for mode,triangles in worlds.items():
        prior=take(old,BASE/old/(mode+'.json.gz'))
        assert prior['groundSHA256']==digest(ground.tobytes()),'Historical complete ground differs; fresh exact face context required'
        assert prior['sourceWorldSHA256']==digest(triangles.astype('<f8').tobytes()),'Historical complete source world differs'
        assert prior['completeSourceFaces']==len(triangles)
        upward=[]
        for face in prior['rows']:
            i=face['sourceFace'];t=triangles[i];assert np.array_equal(t,np.asarray(face['vertices']))
            normal=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(normal))
            if length and float(normal[1])/length>.25:
                assert abs(float(normal[1]))>1e-10;upward.append(i);nominated.add(i)
        facts.append(dict(mode=mode,completeSourceAndGroundStreamsIdentical=True,allHistoricalNegativeFacesPreserved=len(prior['rows']),upwardFacetNominations=upward))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    rows=[]
    for i in sorted(nominated):
        t=original[i];assert np.cross(t[1]-t[0],t[2]-t[0])[1]>1e-10
        rows.append(dict(face=i,vertices=t.tolist()))
    assert rows
    result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],rows=rows,completeFourWorldNumericRebinding=facts,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All four complete source and drawn-ground byte streams match the authenticated earlier exact face census. Every prior negative face remains recorded. Positive-normal nonvertical facets nominate a private lower-only terrain-return experiment; normal orientation is not architectural intent or source/terrain/publication approval. No source edits or waived checks.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('civic_exact_upward_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-four-world-numeric-rebinding-and-upward-source-facet-nomination',refs,result);print(dict(upwardOriginalFacets=len(rows),allFourCompleteNumericStreamsRevalidated=True),flush=True)
if __name__=='__main__':main()
