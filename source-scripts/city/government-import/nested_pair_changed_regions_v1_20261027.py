"""Prove conservative terrain edit bounds from every retained/derived facet."""
from pathlib import Path
import numpy as np
from run import ROOT,read,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from nested_coordinated_parent_contract_v1_20261027 import verify_parent,targets
from nested_coordinated_native_boundary_v1_20261027 import reference,canonical_sha


def verify_changed_regions(prior,successor,receipt):
    index=receipt['retention']['replacedChildIndex']
    north=successor['patches'][index];south=successor['patches'][-1]
    marker=north['nativeMesh']['source']['coordinatedBoundary'];proof=reference(marker['proof'])
    retention=verify_parent(prior,successor,proof,marker,reference,canonical_sha)
    assert retention==receipt['retention']
    proposal_ref=north['nativeMesh']['source']['originalPartitionedInset']['proposal']
    proposal=reference(proposal_ref)
    authenticated,pins=authenticate((ROOT/proposal_ref['path']).parent)
    assert authenticated==proposal and proposal['uids']==receipt['uids']
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    changed=[];total_unchanged=0;used=[ROOT/proposal_ref['path']]
    for part,node in zip(proposal['rows'],[north,south]):
        path=ROOT/part['privateFacesPath'];assert digest(path.read_bytes())==part['privateFacesSHA256'];used.append(path)
        data=read(path);output=np.asarray(data['triangles'],float);lineage=data['lineage'];rows=lineage['outputLineage']
        assert node['nativeMesh']['position']==output.reshape(-1).tolist()
        assert node['nativeMesh']['index']==list(range(output.size//3))
        assert len(rows)==len(output)
        # The original capture is in the proposal's frozen input set; no new
        # source selection or height fitting is performed by this proof.
        captures=[]
        for name in pins:
            if name.endswith('/parent-'+str(part['index'])+'.json'):
                captures.append(ROOT/name)
        assert len(captures)==1
        parentpath=captures[0];used.append(parentpath);baseline=np.asarray(read(parentpath)['triangles'],float)
        assert len(baseline)==part['parentFaces']
        if part['index']==0:
            mesh=prior['patches'][index]['nativeMesh']
            previous=np.asarray(mesh['position'],dtype='float32').astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
            a,b=previous[:,1]-previous[:,0],previous[:,2]-previous[:,0]
            flip=a[:,2]*b[:,0]-a[:,0]*b[:,2]<0
            previous[flip]=previous[flip][:,[0,2,1]]
            assert np.array_equal(previous,baseline),'Whole actual retained native source differs'
        changed_ids=set(lineage['changedParentFaces']);assert all(type(i)is int and 0<=i<len(baseline) for i in changed_ids)
        seen=set()
        for i,row in enumerate(rows):
            parent=row['parentFace'];assert type(parent)is int and 0<=parent<len(baseline)
            if row['kind']=='unchanged':
                assert parent not in changed_ids and parent not in seen
                assert np.array_equal(output[i],baseline[parent]);seen.add(parent)
            else:
                assert row['kind'] in ['parent-fragment','original-inset-or-return'] and parent in changed_ids
                changed.append(output[i])
        assert seen==set(range(len(baseline)))-changed_ids
        assert len(seen)==part['exactUnchangedParentFaces'];total_unchanged+=len(seen)
        changed.extend(baseline[sorted(changed_ids)])
    assert changed
    values=np.asarray(changed).reshape(-1,3);values=np.concatenate([values,values.astype('float32').astype(float)])
    low,high=values.min(0),values.max(0)
    return dict(retainedUids=sorted(targets(prior)),closedChangedRegions=[[float(low[0]),float(low[2]),float(high[0]),float(high[2])]],
                exactUnchangedParentFacets=total_unchanged,retention=retention,
                inputPaths=[str(p.relative_to(ROOT)) for p in used],installationApproved=False)
