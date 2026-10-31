"""Bind below-grade original face topology to complete actual grade/cap evidence.

Diagnostic only: no physical acceptance or new physical support/root credit.
"""
import argparse
import sys
import uuid
from collections import defaultdict, deque
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_clearance_cap_paths_v2_20261024 import verify
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def face_adjacency(tri):
    edges = defaultdict(list)
    for i, face in enumerate(tri):
        vertices = [tuple(p) for p in face]
        for a,b in zip(vertices, vertices[1:]+vertices[:1]):
            if a != b:
                edges[tuple(sorted((a,b)))].append(i)
    adjacent = defaultdict(set)
    for faces in edges.values():
        for i in faces:
            adjacent[i].update(j for j in faces if j != i)
    return adjacent


def exact_plane_key(face):
    vertices = [tuple(Fraction(float(v)) for v in point) for point in face]
    a,b,c = vertices
    u = tuple(b[i]-a[i] for i in range(3))
    v = tuple(c[i]-a[i] for i in range(3))
    normal = (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    nonzero = next((x for x in normal if x), None)
    assert nonzero is not None, 'A collapsed primitive has no surface plane'
    offset = -sum(normal[i]*a[i] for i in range(3))
    return tuple(x/nonzero for x in (*normal,offset))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch','uid','runtime','attributes','clearance','grade']:
        p.add_argument('--'+name, required=True)
    p.add_argument('--lease')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.runtime,a.attributes,a.clearance,a.grade])
    base = ROOT/'docs/astra-city/government-import'
    out, local = base/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    if not a.lease:
        assert not local.exists()
        lp = local/'reservation.json'
        claim = reservations.claim('below-grade-source-'+str(uuid.uuid4()), ['building:'+a.uid], batch=a.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable,__file__,*sys.argv[1:],'--lease',str(lp)])
    lease = read(Path(a.lease))
    assert reservations.owns(lease) and 'building:'+a.uid in lease['resources']
    refs, pins = [Path(__file__)], {}
    def take(batch,path):
        if batch not in pins:
            pins[batch] = authenticate(base/batch)[1]
            refs.append(base/batch/'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    source = next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows'] if r['uid']==a.uid)
    g = next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows'] if r['uid']==a.uid)
    attr = next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows'] if r['uid']==a.uid)
    asset = ROOT/source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds = {'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
    ground = np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    outputs = []
    for mode,tri in worlds.items():
        assert reservations.owns(lease)
        oldmode = {'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)
        low = take(a.clearance,base/a.clearance/(oldmode+'.json.gz'))
        grade = take(a.grade,base/a.grade/(mode+'.json.gz'))
        sha = digest(tri.astype('<f8').tobytes())
        assert low['sourceWorldSHA256'] == grade['sourceWorldSHA256'] == sha
        assert low['groundSHA256'] == grade['completeGroundSHA256'] == digest(ground.tobytes())
        assert low['completeSourceFaces'] == grade['sourceFaces'] == len(tri) == source['triangles']
        assert grade['completeDrawnGroundFaces'] == len(ground)
        assert grade['proof']['allPairsExamined'] and grade['proof']['sourceFacesOmitted']==0
        bad = sorted(r['sourceFace'] for r in low['rows'])
        caps = verify(tri,bad)
        initial_unresolved = [r['sourceFace'] for r in caps['paths'] if not r['hasExactSharedEdgeClearCapPath']]
        if initial_unresolved:
            partial = exact_finite_contacts(tri,initial_unresolved,tri,list(range(len(tri))))
            assert partial['allPairsExamined'] and partial['sourceFacesOmitted']==0
            save(out/(mode+'-partial-source-contacts.json.gz'),partial)
            bridges = sorted({tuple(sorted((c['sourceFaceA'],c['sourceFaceB']))) for c in partial['contacts'] if c['sourceFaceA']!=c['sourceFaceB'] and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2})
            caps = verify(tri,bad,bridges)
        paths = {r['sourceFace']:r for r in caps['paths']}
        positive = [c for c in grade['proof']['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
        contacts = defaultdict(list)
        for c in positive:
            contacts[c['sourceFaceA']].append(c)
        normal = np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        lengths = np.linalg.norm(normal,axis=1)
        down = {int(i) for i in np.flatnonzero(normal[:,1]<-.25*lengths)}
        adjacent = face_adjacency(tri)
        plane_by_face = {i:exact_plane_key(tri[i]) for i in down}
        lower, seen = [], set()
        for seed in sorted(set(bad)&down):
            if seed in seen:
                continue
            y = tri[seed,:,1]
            plane = plane_by_face[seed]
            eligible = {i for i in down if plane_by_face[i] == plane}
            group = {seed}
            q = deque([seed])
            while q:
                for j in adjacent[q.popleft()] & eligible - group:
                    group.add(j);q.append(j)
            seen |= group
            boundary = sorted({j for i in group for j in adjacent[i] if j not in group})
            walls = [i for i in boundary if lengths[i]>0 and abs(normal[i,1])<=.25*lengths[i]]
            lower.append(dict(sourcePlaneExact=[str(v) for v in plane],sourceYRange=[float(tri[sorted(group),:,1].min()),float(tri[sorted(group),:,1].max())],exactlyHorizontal=bool(np.all(y==y[0])),allConnectedCoplanarDownwardFaces=sorted(group),negativeDownwardFaces=sorted(group&set(bad)),boundaryFaces=boundary,boundaryWallFaces=walls,boundaryWallGradeContacts={str(i):contacts[i] for i in walls if contacts[i]},boundaryWallClearCapPaths={str(i):paths[i] for i in walls if i in paths},qualification='Original exact shared edges and equal rational plane coefficients only, including tilted literal planes; no horizontal rounding or tolerance. No structural-role, root, bridge or physical approval.'))
        report = dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=low['groundSHA256'],completeNegativeFaces=bad,initialSharedEdgeUnresolvedWallFaces=initial_unresolved,negativeWallFaces=sorted(paths),wallsWithoutSharedEdgeClearCapPath=[i for i,r in paths.items() if not r['hasExactSharedEdgeClearCapPath']],negativeNonWallFaces=caps['negativeNonWallFaces'],allWallCapPaths=caps['paths'],recomputedPositiveFiniteSourceContacts=caps['recomputedPositiveFiniteContacts'],completePositiveGradeContacts=positive,coplanarDownwardGroups=lower)
        save(out/(mode+'.json.gz'),report)
        outputs.append(dict(mode=mode,negativeFaces=len(bad),negativeWalls=len(paths),initialSharedEdgeUnresolvedWalls=len(initial_unresolved),wallsWithoutSharedEdgeClearCapPath=len(report['wallsWithoutSharedEdgeClearCapPath']),negativeNonWallFaces=caps['negativeNonWallFaces'],downwardGroups=[{k:r[k] for k in ['sourcePlaneExact','sourceYRange','exactlyHorizontal','allConnectedCoplanarDownwardFaces','negativeDownwardFaces','boundaryFaces','boundaryWallFaces']}|dict(boundaryWallFacesWithGradeContacts=sorted(map(int,r['boundaryWallGradeContacts'])),boundaryWallFacesWithClearCapPaths=sorted(int(i) for i,v in r['boundaryWallClearCapPaths'].items() if v['hasExactSharedEdgeClearCapPath'])) for r in lower]))
        print(outputs[-1],flush=True)
    for name in ['selected_original_four_world_low_face_context_v2_20261027.py','selected_original_four_world_low_face_context_v3_20261031.py']:
        producer = HERE/name
        assert digest(producer.read_bytes()) == pins[a.clearance][str(producer.relative_to(ROOT))]
        refs.append(producer)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[a.runtime][str(manifest.relative_to(ROOT))]
    refs.extend([manifest,HERE/'complete_clearance_cap_paths_v2_20261024.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py'])
    result = dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=outputs,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,physicalInterComponentSupportBridgeCredit=False,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
    assert reservations.owns(lease)
    save(out/'summary.json',result)
    module('below_grade_source_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-four-world-original-below-grade-surface-context',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
