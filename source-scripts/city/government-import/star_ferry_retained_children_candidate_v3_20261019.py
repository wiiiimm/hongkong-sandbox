"""Private source terrain candidate retaining both existing native children in full."""
import json, sys, uuid, subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as repair

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-star-ferry-retained-children-candidate-v3-20261019'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
SCOPE = BASE/'government-xl-remaining-two-current-scope-v1-20261019'
PROJECTION = BASE/'government-xl-star-ferry-retained-projection-v1-20261019'
UID = 'landsd/210032:0'

def half(poly, axis, value, sign):
    out = []
    for a, b in zip(poly, poly[1:]+poly[:1]):
        da, db = sign*(a[axis]-value), sign*(b[axis]-value)
        if da >= 0:
            out.append(a)
        if (da < 0 < db) or (db < 0 < da):
            out.append(a+(b-a)*(da/(da-db)))
    return out

def outside(face, bounds):
    """Clip in XYZ, including projected-vertical triangles, without moving planes."""
    inside, result = list(face), []
    for axis, value, sign in [(0,bounds[0],1),(0,bounds[2],-1),(2,bounds[1],1),(2,bounds[3],-1)]:
        if len(inside) < 3:
            break
        rejected = half(inside, axis, value, -sign)
        # Entirely boundary-coincident faces belong to the retained child.
        if any(sign*(p[axis]-value) < 0 for p in inside):
            result.extend([[rejected[0],rejected[i],rejected[i+1]] for i in range(1,len(rejected)-1)])
        inside = half(inside, axis, value, sign)
    return result

def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease)
    refs = [Path(__file__), HERE/'native_patch_resolution.py', HERE/'exact_packed_world_geometry_20261009.py']
    r = read(SCOPE/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone() == ('complete',r)
    for e in r['evidenceRefs']:
        p = ROOT/e['path']; assert digest(p.read_bytes()) == e['sha256']; refs.append(p)
    refs.append(SCOPE/'result.json')
    scope = next(r for r in read(SCOPE/'scope.json')['rows'] if r['uid']==UID)
    info = scope['overlappingInstalledTerrain'][0]
    parentpath = ROOT/'3d-viewer'/info['url']; parent = read(parentpath)
    plan = read(PROJECTION/'projection-checks.json')
    cells, bounds = plan['mergedCells'], plan['mergedExtent']
    builder = module('star_child_constructor',HERE/'resolve-pass-indexed-parent-clipping.py')
    assert builder.extent(cells,parent)==bounds
    children = [c for c in parent['patches'] if c['id'] in plan['retainedChildIds']]
    assert len(children)==2 and not plan['otherOverlappingChildIds']
    selection = BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz'
    row = next(r for r in read(selection)['rows'] if r['uid']==UID)
    asset = ROOT/row['candidate']['path']; assert digest(asset.read_bytes())==row['sourceSHA256']
    groundpath = HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/210032:0-ground.json.gz'
    ground = read(groundpath); native = np.asarray(ground['completeAdjoiningTerrain'])
    native = native[(native[:,:,0].max(1)>=bounds[0]) & (native[:,:,0].min(1)<=bounds[2]) & (native[:,:,2].max(1)>=bounds[1]) & (native[:,:,2].min(1)<=bounds[3])]
    assert len(native) and np.isfinite(native).all()
    save(DOC/"original-waterfront-terrain.json",dict(minimumSourceY=float(native[:,:,1].min()),facesBelowGenericClamp=int((native[:,:,1].min(1)<1.2).sum()),policy="Preserve original waterfront source heights using existing constructor path; final terrain, water-mask, support and neighbour guards still mandatory.",installationApproved=False))
    sourcespath = BASE/'government-xl-next-five-adjoining-ground-v1-20261018/acquisitions.json'
    sources = [s for s in read(sourcespath) if s['sheet'] in ground['sheets']]
    lo, hi = row['candidate']['entry']['worldBounds']
    core = [lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]
    validator = builder.validate_patch
    builder.validate_patch = lambda *_: None
    try:
        patch = builder.make_patch(dict(uids=[UID],cells=cells),parent,native,sources,native_core=core,parent_url=info['url'],parent_sha256=digest(parentpath.read_bytes()),allow_native_below_clamp=True,terrain_triangle_budget=1000000)
    finally:
        builder.validate_patch = validator
    t = decode_original_world_triangles(asset.read_bytes())[:,:,[0,2]]
    projection = shapely.union_all([shapely.union_all(shapely.polygons(t)),shapely.union_all(shapely.linestrings(np.concatenate([t,t[:,:1]],axis=1))),shapely.union_all(shapely.points(t.reshape(-1,2)))])
    sampler = builder.terrain.fine.DemSampler(parent,rendered=True)
    repair.preserve_parent_under_projection(patch,bounds,shapely.box(*bounds).difference(projection.buffer(1,join_style='mitre')),sampler)
    faces = repair._faces(patch)
    preserved = []
    for child in children:
        rect = builder.extent(child['coarseCells'],parent)
        clipped = []
        for face in faces:
            if face[:,0].max()<rect[0] or face[:,0].min()>rect[2] or face[:,2].max()<rect[1] or face[:,2].min()>rect[3]:
                clipped.append(face)
            else:
                clipped.extend(outside(face,rect))
        original = repair._faces(child)
        faces = np.concatenate([np.asarray(clipped).reshape(-1,3,3),original])
        preserved.append(dict(id=child['id'],triangles=len(original),includingProjectedVerticals=True))
    flat = faces.reshape(-1,3)
    patch['nativeMesh']['position']=flat.reshape(-1).tolist()
    patch['nativeMesh']['index']=list(range(len(flat)))
    save(LOCAL/'terrain-private-child.json',patch)
    error = None
    try:
        validator(patch,parent)
    except Exception as exc:
        error = str(exc)
    save(DOC/'candidate.json',dict(uid=UID,changedExtent=bounds,preservedChildren=preserved,triangles=len(faces),nativeValidatorError=error,installationApproved=False,fullNeighbourAndSupportChecksPending=True))
    refs.extend([parentpath,selection,asset,groundpath,sourcespath,PROJECTION/'projection-checks.json',LOCAL/'terrain-private-child.json',HERE/'resolve-pass-indexed-parent-clipping.py'])
    assert reservations.owns(lease)
    module('star_children_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-private-full-retained-child-terrain',list(dict.fromkeys(refs)),dict(uids=[UID],nativeValidatorError=error,installationApproved=False))
    print(dict(triangles=len(faces),nativeValidatorError=error),flush=True)

def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists()
    plan = read(PROJECTION/'projection-checks.json')
    uids = [UID]+[r['uid'] for r in plan['actors']]
    resources = sorted({'building:'+u for u in uids}|{'terrain-patch:'+u for u in uids})
    claim = reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
    assert claim['ok']
    lease = claim['reservation']; save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
    try:
        subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']

if __name__=='__main__':
    main()
