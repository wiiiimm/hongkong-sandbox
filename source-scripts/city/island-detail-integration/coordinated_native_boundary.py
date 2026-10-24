"""Validate an explicitly bound pair of finite adjoining native-terrain boundaries.

Only the shared edge inside the reviewed edit region can use the other member as
its boundary surface. All other edge vertices still join the root terrain under
native_terrain_validation's unchanged rules. This provides no model approval.
"""
import copy,hashlib,json,math,sys
from pathlib import Path
import numpy as np
import shapely

ROOT=Path(__file__).resolve().parents[3]
GOVERNMENT=Path(__file__).resolve().parents[1]/'government-import'
if str(GOVERNMENT)not in sys.path:sys.path.insert(0,str(GOVERNMENT))
from coordinated_native_boundary_v1_20261023 import seam_segments,compatible_seam,value,rational
from finite_native_boundary_strip_v1_20261023 import strip_report
POLICY='finite-native-shared-boundary-v1'


def canonical_sha(patch):
    unbound=copy.deepcopy(patch)
    unbound['nativeMesh'].pop('sourceOverlap',None)
    unbound['nativeMesh']['source'].pop('coordinatedBoundary',None)
    raw=json.dumps(unbound,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def reference(ref):
    assert set(ref)=={'path','sha256'}and isinstance(ref['path'],str)
    path=(ROOT/ref['path']).resolve();assert path.is_relative_to(ROOT.resolve())
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'],'Coordinated boundary input changed'
    return json.loads(raw)


def bounds(patch):
    g=patch['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN']
    values=(x0,z0,x0+(patch['w']-1)*g['aE'],z0-(patch['h']-1)*g['aN'])
    assert all(math.isfinite(v)for v in values)and values[0]<values[2]and values[1]<values[3]
    return values


def triangles(patch):
    mesh=patch['nativeMesh'];v=np.asarray(mesh['position'],dtype='float32').astype('float64')
    assert v.ndim==1 and len(v)%3==0 and np.isfinite(v).all()
    idx=mesh['index'];assert idx and len(idx)%3==0 and all(type(i)is int and 0<=i<len(v)//3 for i in idx)
    return v.reshape(-1,3)[np.asarray(idx).reshape(-1,3)]


def coordinated_boundary(patch,parent):
    marker=patch.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')
    if marker is None:return None
    assert set(marker)=={'policy','proof','member'}and marker['policy']==POLICY
    proof=reference(marker['proof']);assert proof['policy']==POLICY
    parent_data=reference(proof['parent'])
    assert json.dumps(parent_data,sort_keys=True,separators=(',',':'))==json.dumps(parent,sort_keys=True,separators=(',',':')),'Coordinated parent differs'
    members=proof['members'];assert len(members)==2 and marker['member']in members
    names=sorted(members);candidates={};rectangles={}
    for name in names:
        member=members[name];assert set(member)=={'before','candidate','canonicalSHA256'}
        old=reference(member['before']);candidate=reference(member['candidate'])
        assert old.get('nativeMesh')and candidate.get('nativeMesh')and not candidate.get('patches')and not candidate.get('hydro')
        assert not candidate['nativeMesh'].get('sourceOverlap')and not candidate['nativeMesh'].get('source',{}).get('coordinatedBoundary')
        assert canonical_sha(candidate)==member['canonicalSHA256']
        for node in [old,candidate]:
            assert node['meta']['parentTerrain']==patch['meta']['parentTerrain']
            assert node['meta']['parentSha256']==proof['parent']['sha256']
        assert set(old['meta']['targetUids'])<=set(candidate['meta']['targetUids'])
        assert shapely.box(*bounds(candidate)).covers(shapely.box(*bounds(old))),'Coordinated member lost old extent'
        g=parent['meta']['georef'];a,b,c,d=candidate['coarseCells'];assert all(type(v)is int for v in [a,b,c,d])and 0<=a<c<parent['w']and 0<=b<d<parent['h'];expected=(g['bE']+a*g['aE']-834500,816500-g['bN']-b*g['aN'],g['bE']+c*g['aE']-834500,816500-g['bN']-d*g['aN'])
        assert bounds(candidate)==expected,'Coordinated member misaligned with root cells'
        candidates[name]=candidate;rectangles[name]=shapely.box(*bounds(candidate))
    assert canonical_sha(patch)==members[marker['member']]['canonicalSHA256'],'Coordinated own geometry or metadata changed'
    a,b=names;assert rectangles[a].intersection(rectangles[b]).area==0,'Coordinated members overlap in area'
    edge=rectangles[a].boundary.intersection(rectangles[b].boundary)
    assert edge.geom_type=='LineString'and edge.length>0,'Coordinated members must share one finite edge'
    coordinates=list(edge.coords);xs={p[0]for p in coordinates};zs={p[1]for p in coordinates}
    assert len(xs)==1 or len(zs)==1
    axis=0 if len(xs)==1 else 2;coordinate=coordinates[0][0 if axis==0 else 1];other=2 if axis==0 else 0
    edit=shapely.from_wkt(proof['editRegionWKT']);assert edit.is_valid and not edit.is_empty and edit.area>0
    domain=shapely.union_all(list(rectangles.values()));assert domain.covers(edit)and edit.distance(domain.boundary)>0
    allowed=edge.intersection(edit);intervals=[]
    meshes={name:triangles(candidates[name])for name in names}
    for line in shapely.get_parts(allowed):
        if line.geom_type=='Point':continue
        assert line.geom_type=='LineString'and line.length>0
        t=[point[1 if axis==0 else 0]for point in line.coords];lo,hi=min(t),max(t);assert lo<hi
        curves={name:seam_segments(meshes[name],axis,coordinate,lo,hi)for name in names}
        # No sparse sampling: every kink, isolated point and finite interval
        # limit is checked under the existing strict 1cm boundary threshold.
        compatible_seam(curves[a],curves[b],lo,hi)
        intervals.append((rational(lo),rational(hi),curves))
    assert intervals,'Coordinated edit does not meet shared boundary'
    own=marker['member'];mate=next(name for name in names if name!=own)
    # native_terrain_validation nominates every position within the existing
    # 2mm boundary band. Interior nominated vertices need an actual indexed,
    # nonvertical triangle containing the finite orthogonal edge projection.
    # Mere coordinate proximity never supplies boundary credit.
    vertex_faces={};strip_faces={}
    ownmesh=meshes[own]
    selected=np.flatnonzero(np.any(np.abs(ownmesh[:,:,axis]-coordinate)<.002,axis=1))
    for face_id in selected:
        face=ownmesh[face_id];a0,b0,c0=face
        determinant=(b0[2]-c0[2])*(a0[0]-c0[0])+(c0[0]-b0[0])*(a0[2]-c0[2])
        if abs(determinant)<1e-10:
            if np.all(face[:,axis]==coordinate):
                for point in face:strip_faces.setdefault(tuple(point),[]).append(int(face_id))
            continue
        for point in face:
            if abs(point[axis]-coordinate)<.002:vertex_faces.setdefault(tuple(point),[]).append(int(face_id))
    def projection_height(face,x,z):
        a0,b0,c0=[tuple(map(rational,p))for p in face]
        x,z=map(rational,[x,z]);den=(b0[2]-c0[2])*(a0[0]-c0[0])+(c0[0]-b0[0])*(a0[2]-c0[2])
        if not den:return None
        u=((b0[2]-c0[2])*(x-c0[0])+(c0[0]-b0[0])*(z-c0[2]))/den
        v=((c0[2]-a0[2])*(x-c0[0])+(a0[0]-c0[0])*(z-c0[2]))/den;w=1-u-v
        return u*a0[1]+v*b0[1]+w*c0[1]if min(u,v,w)>=0 else None
    def allows(x,y,z):
        point=(x,y,z)
        if abs(rational(point[axis])-rational(coordinate))>=rational(.002):return False
        incident=vertex_faces.get(tuple(point),[])
        strips=strip_faces.get(tuple(point),[])
        if not incident and not strips:return False
        t=rational(point[other]);height=rational(y)
        for lo,hi,curves in intervals:
            if not lo<=t<=hi:continue
            covering=[s for s in curves[mate]if s[0]<=t<=s[1]]
            assert covering,'Coordinated boundary vertex has no finite mate'
            from fractions import Fraction
            expected=max(value(s,t)for s in covering)
            projected=list(point);projected[axis]=coordinate
            witnesses=[projection_height(ownmesh[i],projected[0],projected[2])for i in incident]
            witnesses=[h for h in witnesses if h is not None]
            if not witnesses:
                for face_id in strips:
                    try:strip_report(ownmesh[face_id],axis,coordinate,curves[mate],lo,hi)
                    except AssertionError:continue
                    return True
                return False
            assert any(abs(height-h)<Fraction(1,100)and abs(h-expected)<Fraction(1,100)for h in witnesses),'No finite same-triangle boundary-height witness'
            assert abs(height-expected)<Fraction(1,100),'Coordinated boundary vertex differs from finite mate'
            return True
        return False
    return allows


def validate_effective_coordinated_members(nodes):
    """Both exact members must exist in the effective post-transaction terrain.

A private mate file alone cannot authorize publishing only one half. An existing
unchanged mate is valid only when its complete canonical body matches exactly.
"""
    by_cells={}
    for node in nodes:by_cells.setdefault(tuple(node['coarseCells']),[]).append(node)
    checked=set()
    for node in nodes:
        marker=node.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')
        if marker is None:continue
        assert set(marker)=={'policy','proof','member'}and marker['policy']==POLICY
        proof=reference(marker['proof']);assert proof['policy']==POLICY and len(proof['members'])==2
        assert marker['member']in proof['members']
        assert canonical_sha(node)==proof['members'][marker['member']]['canonicalSHA256']
        key=(marker['proof']['path'],marker['proof']['sha256'])
        if key in checked:continue
        for name,member in proof['members'].items():
            candidate=reference(member['candidate']);assert canonical_sha(candidate)==member['canonicalSHA256']
            matches=[p for p in by_cells.get(tuple(candidate['coarseCells']),[])if canonical_sha(p)==member['canonicalSHA256']]
            assert len(matches)==1,'Every coordinated member must be present exactly once in final terrain'
            other=matches[0].get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')
            if other is not None:
                assert other==dict(policy=POLICY,proof=marker['proof'],member=name),'Coordinated final members disagree on proof identity'
        checked.add(key)
