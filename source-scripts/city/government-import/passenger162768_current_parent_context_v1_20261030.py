"""Capture current coastal parent geometry; no clamp exception or terrain edits."""
import json
import math
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from ronsdale_local_inset_v2_20261022 import plane, lower_region

BASE = ROOT/'docs/astra-city/government-import'
P = 'government-xl-passenger162768-after-civic-five-'
BATCH = P+'parent-context-v1-20261030'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
UID = 'landsd/162768:0'


def main():
    if '--owned' not in sys.argv:
        assert not DOC.exists() and not LOCAL.exists()
        claim = reservations.claim(BATCH+'-'+str(uuid.uuid4()), ['building:'+UID,'terrain:city/data/terrain.json'], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        lease = claim['reservation']
        save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:
            subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch,filename):
        if batch not in pins:
            _,pins[batch] = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(P+'current-ground-v1-20261030','selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid']==UID)
    attr = next(r for r in take(P+'attributes-v1-20261030','attributes.json.gz')['rows'] if r['uid']==UID)
    asset = ROOT/row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds = [decode_original_world_triangles(asset.read_bytes())]
    worlds += [np.asarray(attr[key]).reshape(-1,3)[ix] for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]
    assert all(len(t)==32238 for t in worlds)
    projections = [shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in triangles]) for triangles in worlds]
    projection = shapely.union_all(projections)
    core = projection.buffer(1,join_style='mitre')
    outer = core.buffer(3,join_style='mitre')
    rootpath = ROOT/'3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    g,size = parent['meta']['georef'],parent['cell']
    a,b,c,d = outer.bounds
    cells = [math.floor((a-.001+834500-g['bE'])/size),math.floor((b-.001-816500+g['bN'])/size),math.ceil((c+.001+834500-g['bE'])/size),math.ceil((d+.001-816500+g['bN'])/size)]
    builder = module('passenger_parent_extent',HERE/'resolve_pass_indexed_parent_clipping_v2.py')
    bounds = builder.extent(cells,parent)
    domain = shapely.box(*bounds)
    assert domain.covers(outer) and outer.distance(domain.boundary)>0
    save(DOC/'scope.json',dict(uids=[UID],cells=cells,bounds=bounds,coreBounds=list(core.bounds),outerBounds=list(outer.bounds)))
    tool = HERE/'selected_original_parent_capture_v2.mjs'
    subprocess.run(['node',str(tool),str((DOC/'scope.json').relative_to(ROOT)),str((LOCAL/'parent.json').relative_to(ROOT))],cwd=ROOT,check=True)
    captured = read(LOCAL/'parent.json')
    assert captured['inputHashes']['3d-viewer/city/data/manifest.json']==selection['manifestSHA256']
    for path,sha in captured['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha
        refs.append(ROOT/path)
    faces = np.asarray(captured['triangles'],dtype='<f8')
    polys = shapely.polygons(faces[:,:,[0,2]])
    valid = shapely.area(polys)>0
    land = shapely.union_all(polys[valid])
    missing = domain.difference(land)
    low = []
    for i in np.flatnonzero(valid & (faces[:,:,1].min(1)<1.2)):
        region = lower_region(polys[i],plane(faces[i])-np.asarray([0.,0.,1.2]))
        if region.is_empty:
            continue
        low.append(dict(parentFace=int(i),minimumHeightM=float(faces[i,:,1].min()),lowRegionAreaM2=region.area,insideOuterAreaM2=region.intersection(outer).area,insideSourceProjectionAreaM2=region.intersection(projection).area))
    result = dict(uids=[UID],sourceSHA256=row['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],completeParentFaces=len(faces),minimumParentHeightM=float(faces[:,:,1].min()),parentBelowClampFaces=len(low),rows=low,missingParentAreaM2=missing.area,missingParentWKT=missing.wkt,sourceProjectionInsideMissingAreaM2=projection.intersection(missing).area,outerInsideMissingAreaM2=outer.intersection(missing).area,sourceGeometryChanges=0,terrainEdits=False,physicalAcceptance=False,installationApproved=False,qualification='Actual current rendered parent and all-four-world original projection context only. No source-height exception, water fill, parent mutation, model edit or architectural/placement acceptance. Missing/low coastal domains must remain explicit in the later bounded terrain design.')
    save(DOC/'summary.json',result)
    refs += [tool,LOCAL/'parent.json',rootpath,HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py']
    assert reservations.owns(lease)
    module('passenger_parent_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-passenger-parent-coastal-clamp-domain-context',refs,result)


if __name__=='__main__':
    main()
