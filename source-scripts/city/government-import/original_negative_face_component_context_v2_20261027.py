"""Measure flagged source faces and exact shared-edge components; no role approval."""
import argparse,json
from collections import defaultdict, deque
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def component_context(tri, face_id):
    assert type(face_id) is int and 0 <= face_id < len(tri)
    edges = defaultdict(list)
    for i, face in enumerate(tri):
        vertices = list(map(tuple, face))
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            if a != b:
                edges[tuple(sorted((a, b)))].append(i)
    adjacency = defaultdict(set)
    for incident in edges.values():
        for i in incident:
            adjacency[i].update(j for j in incident if j != i)
    component = {face_id}
    queue = deque([face_id])
    while queue:
        for neighbour in adjacency[queue.popleft()]:
            if neighbour not in component:
                component.add(neighbour)
                queue.append(neighbour)
    face = tri[face_id]
    normal = np.cross(face[1] - face[0], face[2] - face[0])
    component_tri = tri[sorted(component)]
    records = []
    vertices = list(map(tuple, face))
    for a, b in zip(vertices, vertices[1:] + vertices[:1]):
        records.append(dict(endpoints=[a,b], incidentSourceFaces=edges[tuple(sorted((a,b)))]))
    return dict(sourceFace=face_id, vertices=face.tolist(), normal=normal.tolist(),
                areaM2=float(np.linalg.norm(normal)/2),
                exactlyHorizontal=bool(normal[0] == normal[2] == 0 and normal[1] != 0),
                downward=bool(normal[1] < 0),
                wholeSharedEdgeComponentFaces=len(component), componentFaceIds=sorted(component),
                componentBounds=[component_tri.min((0,1)).tolist(), component_tri.max((0,1)).tolist()],
                allVerticesAtComponentMinimum=bool(np.all(face[:,1] == component_tri[:,:,1].min())),
                exactEdgeIncidence=records,
                adjacentFaces=[dict(sourceFace=i,vertices=tri[i].tolist()) for i in sorted(adjacency[face_id])])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','clearance','uid']:
        ap.add_argument('--'+key,required=True)
    ap.add_argument('--face',action='append',type=int,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows'] if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows'] if r['uid']==a.uid)
    low=take(a.clearance,base/a.clearance/'summary.json')
    assert source['sourceSHA256']==attr['sourceSHA256']==low['sourceSHA256']
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
    rows=[]
    assert len(set(a.face))==len(a.face)
    for mode,tri in worlds.items():
        proof=take(a.clearance,base/a.clearance/(mode+'.json.gz'))
        assert digest(tri.astype('<f8').tobytes())==proof['sourceWorldSHA256']
        assert set(a.face)<={r['sourceFace'] for r in proof['rows']}
        rows.append(dict(mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],completeSourceFaces=len(tri),faces=[component_context(tri,i) for i in a.face]))
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,sourceGeometryChanges=0,
                physicalAcceptance=False,sourceRoleAccepted=False,installationApproved=False,publication=False,
                qualification='Exact represented shared-edge incidence and full component bounds only. Downward orientation and component minimum are measured source context, not architectural identity, visibility, support or acceptance. Complete clearance failures remain unchanged.')
    result=json.loads(json.dumps(result,allow_nan=False))
    save(out/'summary.json',result)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('original_negative_component_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'negative-original-face-exact-component-context',list(dict.fromkeys(refs)),result)
    print(dict(batch=a.batch,faces=a.face,worlds=len(rows)),flush=True)


if __name__=='__main__':main()
