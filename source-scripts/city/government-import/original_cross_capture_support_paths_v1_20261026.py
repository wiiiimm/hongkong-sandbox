"""Explain strict support witnesses with original endpoint-bounded source paths.

Keeps strict probe failures; topology paths do not grant physical acceptance.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_contact_paths_with_finite_joins_v1_20261023 import paths
from pool_incident_wall_contacts_v1_20261017 import closest
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','runtime','attributes','probe']:
        p.add_argument('--'+name,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    probe=take(a.probe,'summary.json');uid,support=probe['uids'];selected=take(a.runtime,'selection.json.gz')
    rows={r['uid']:r for r in selected['rows']};attributes=take(a.attributes,'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']}
    worlds={}
    for key in [uid,support]:
        row=rows[key];attr=attrs[key];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==probe['sourceSHA256ByUid'][key];refs.append(asset)
        ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds[key]=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]})
    results=[]
    for item in probe['rows']:
        mode=item['mode'];t,u=worlds[uid][mode],worlds[support][mode]
        assert probe['sourceWorldSHA256ByMode'][mode]=={uid:digest(t.astype('<f8').tobytes()),support:digest(u.astype('<f8').tobytes())}
        proof=exact_finite_contacts(t,range(len(t)),u,range(len(u)));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
        targets=[];lo,hi=t.min(1),t.max(1)
        for witness in item['interface']['unresolved']:
            point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
            incident=[int(i)for i in broad if np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0 and np.linalg.norm(closest(point,t[i])-point)<=.001]
            assert incident;targets.append(dict(witness=witness,incidentFaces=incident))
        traced=paths(t,dict(targets=targets,proof=proof),[])
        save(out/(mode+'.json.gz'),dict(mode=mode,strictInterface=item['interface'],completeFiniteContacts=proof,paths=traced))
        result=dict(mode=mode,strictSamples=item['interface']['samples'],strictContacts=item['interface']['strictContacts'],strictUnresolved=len(targets),exactSharedEdgeEndpointBoundedPaths=sum(r['verifiedPath']is not None for r in traced),remaining=sum(r['verifiedPath']is None for r in traced))
        results.append(result);print(result,flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[uid,support],sourceSHA256ByUid=probe['sourceSHA256ByUid'],rows=results,sourceGeometryChanges=0,sourcePoseChanges=0,strictFailuresRetained=True,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All raw strict support witnesses retained; exact shared-edge paths to complete positive finite original contacts replay existing 1mm residual and endpoint-height gates. No extra finite joins, source edits, source-role, foundation, structural or collision acceptance.')
    save(out/'summary.json',result);refs.extend(HERE/name for name in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','original_contact_paths_with_finite_joins_v1_20261023.py','pool_incident_wall_contacts_v1_20261017.py'])
    module('cross_capture_support_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-shared-edge-endpoint-bounded-support-paths',refs,result)


if __name__=='__main__':main()
