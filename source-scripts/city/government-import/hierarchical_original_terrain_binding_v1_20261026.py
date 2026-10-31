"""Bind a private group successor to every retained child and old grid value."""
from copy import deepcopy


def target_uids(node):
    values=set(node['meta'].get('targetUids',[]))
    for child in node.get('patches',[]):values.update(target_uids(child))
    return values


def native_triangles(node):
    return len(node.get('nativeMesh',{}).get('index',[]))//3+sum(native_triangles(c)for c in node.get('patches',[]))


def verify_successor(prior, successor, new_uids):
    wanted=set(new_uids);assert wanted and all(u.startswith('landsd/')for u in wanted)
    assert prior.get('patches') and not prior.get('nativeMesh') and not prior.get('hydro')
    assert successor.get('patches') and not successor.get('nativeMesh') and not successor.get('hydro')
    assert successor['patches'][:-1]==prior['patches'],'Retained children changed or reordered'
    child=successor['patches'][-1]
    assert child.get('nativeMesh') and not child.get('patches')
    assert set(child['meta']['targetUids'])==wanted and not wanted&target_uids(prior)
    assert target_uids(successor)==target_uids(prior)|wanted
    assert successor['cell']==prior['cell'] and successor['h']==prior['h'] and successor['w']>=prior['w']
    assert successor['coarseCells'][:2]==prior['coarseCells'][:2] and successor['coarseCells'][3]==prior['coarseCells'][3] and successor['coarseCells'][2]>=prior['coarseCells'][2]
    a,b,c,d=child['coarseCells'];assert 0<=a<c<successor['w'] and 0<=b<d<successor['h']
    for old in prior['patches']:
        x,y,z,w=old['coarseCells'];assert c<=x or a>=z or d<=y or b>=w,'New child overlaps a retained child'
    for name in ['elev','renderedElev','vegetation']:
        assert len(successor[name])==successor['w']*successor['h']
        for row in range(prior['h']):
            assert successor[name][row*successor['w']:row*successor['w']+prior['w']]==prior[name][row*prior['w']:(row+1)*prior['w']],'Old group grid value changed'
    old_meta=deepcopy(prior['meta']);new_meta=deepcopy(successor['meta'])
    new_meta['georef']['W']=old_meta['georef']['W']
    for key in ['targetUids','scriptedOriginalChildExtension']:new_meta.pop(key,None)
    old_meta.pop('targetUids',None)
    assert new_meta==old_meta,'Unrelated group metadata changed'
    # Expansion exclusions cannot remove any original parent cell.
    previous=prior.get('patchExclusions',[]);now=successor.get('patchExclusions',[])
    assert now[:len(previous)]==previous
    for x,y,z,w in now[len(previous):]:assert x>=prior['w']-1 and x<z<=successor['w']-1 and 0<=y<w<=prior['h']-1
    allowed={'w','coarseCells','elev','renderedElev','vegetation','meta','patches','patchExclusions'}
    assert {k:v for k,v in successor.items()if k not in allowed}=={k:v for k,v in prior.items()if k not in allowed}
    return dict(retainedUids=sorted(target_uids(prior)),newUids=sorted(wanted),retainedChildren=len(prior['patches']),
        exactOldGridNodes=prior['w']*prior['h'],oldNativeTriangles=native_triangles(prior),
        newNativeTriangles=native_triangles(successor),allOriginalChildrenUnchanged=True,
        oldRootSurfaceOutsideNewChildUnchanged=True,installationApproved=False)
