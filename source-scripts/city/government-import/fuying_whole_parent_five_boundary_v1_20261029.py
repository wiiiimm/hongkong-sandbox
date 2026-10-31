"""PRIVATE exact Fu Ying whole-native-parent partition boundary experiment.

No publisher/runtime registration or source/model acceptance. All outer boundary
checks remain ordinary; only finite internal mates can supply shared-edge credit.
"""
import copy,sys
from contextlib import contextmanager
from pathlib import Path
import numpy as np
import shapely
INTEGRATION=Path(__file__).resolve().parents[1]/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
import coordinated_native_boundary as legacy
from coordinated_native_boundary_v1_20261023 import seam_segments,compatible_seam,value,rational
from finite_native_boundary_strip_v1_20261023 import strip_report
POLICY='finite-fuying-whole-native-parent-five-members-v1'
OLD_SHA='b98d5133458755e790f1a7d514dfcbc46e9ac91b60602ae7c0d2286c198b80fd'
NAMES={'west-west-low-z','west-east-low-z','west-high-z','east-low-z','east-high-z'}
BOUNDARY=legacy.coordinated_boundary
EFFECTIVE=legacy.validate_effective_coordinated_members

def marker(node):return node.get('nativeMesh',{}).get('source',{}).get('coordinatedBoundary')

def load(ref,parent=None):
 proof=legacy.reference(ref)
 assert set(proof)=={'policy','parent','oldNative','members','targetUids'}and proof['policy']==POLICY
 assert proof['oldNative']['sha256']==OLD_SHA
 root=legacy.reference(proof['parent']);old=legacy.reference(proof['oldNative'])
 if parent is not None:assert root==parent,'Different actual root terrain'
 assert old['meta']['parentSha256']==proof['parent']['sha256']
 assert set(proof['targetUids'])==set(old['meta']['targetUids'])|{'landsd/181489:0'}
 assert len(proof['targetUids'])==6 and set(proof['members'])==NAMES
 candidates={};rectangles={}
 for name,item in proof['members'].items():
  assert set(item)=={'candidate','canonicalSHA256'}
  node=legacy.reference(item['candidate'])
  assert node.get('nativeMesh')and not node.get('patches')and not node.get('hydro')
  assert not marker(node)and not node['nativeMesh'].get('sourceOverlap')
  assert legacy.canonical_sha(node)==item['canonicalSHA256']
  assert node['meta']['parentSha256']==proof['parent']['sha256']and node['meta']['parentTerrain']==old['meta']['parentTerrain']
  assert set(node['meta']['targetUids'])==set(proof['targetUids'])
  tri=legacy.triangles(node);assert 0<len(tri)<=25000
  a,b,c,d=node['coarseCells'];g=root['meta']['georef']
  assert all(type(v)is int for v in [a,b,c,d])and 0<=a<c<root['w']and 0<=b<d<root['h']
  assert legacy.bounds(node)==(g['bE']+a*g['aE']-834500,816500-g['bN']-b*g['aN'],g['bE']+c*g['aE']-834500,816500-g['bN']-d*g['aN'])
  # Every legacy grid, land/water and vegetation node remains the exact crop.
  og=old['meta']['georef'];ng=node['meta']['georef']
  assert ng['aE']==og['aE']and ng['aN']==og['aN']
  x=(ng['bE']-og['bE'])/og['aE'];y=(ng['bN']-og['bN'])/og['aN']
  assert x==int(x)and y==int(y);x,y=int(x),int(y)
  assert 0<=x<x+node['w']<=old['w']and 0<=y<y+node['h']<=old['h']
  for field in ['elev','renderedElev','vegetation']:
   assert(field in old)==(field in node)
   if field in old:
    expected=[old[field][j*old['w']+i]for j in range(y,y+node['h'])for i in range(x,x+node['w'])]
    assert node[field]==expected,field+' changed'
  candidates[name]=node;rectangles[name]=shapely.box(*legacy.bounds(node))
 assert shapely.union_all(list(rectangles.values())).equals(shapely.box(*legacy.bounds(old))),'Whole old extent was not replaced exactly'
 edges=[]
 for i,a in enumerate(sorted(candidates)):
  for b in sorted(candidates)[i+1:]:
   assert rectangles[a].intersection(rectangles[b]).area==0,'Partition interiors overlap'
   shared=rectangles[a].boundary.intersection(rectangles[b].boundary)
   if shared.is_empty or shared.geom_type=='Point':continue
   assert shared.geom_type=='LineString'and shared.length>0;edges.append((a,b))
 assert edges and set(n for pair in edges for n in pair)==NAMES
 return proof,candidates,edges

def finite_callback(candidates,own):
    names=sorted(candidates);assert len(names)==2 and own in names
    rectangles={n:shapely.box(*legacy.bounds(v))for n,v in candidates.items()}
    a,b=names;assert rectangles[a].intersection(rectangles[b]).area==0,'Coordinated members overlap in area'
    edge=rectangles[a].boundary.intersection(rectangles[b].boundary)
    assert edge.geom_type=='LineString'and edge.length>0,'Coordinated members must share one finite edge'
    coordinates=list(edge.coords);xs={p[0]for p in coordinates};zs={p[1]for p in coordinates}
    assert len(xs)==1 or len(zs)==1
    axis=0 if len(xs)==1 else 2;coordinate=coordinates[0][0 if axis==0 else 1];other=2 if axis==0 else 0
    allowed=edge;intervals=[]
    meshes={name:legacy.triangles(candidates[name])for name in names}
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
    mate=next(name for name in names if name!=own)
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


def coordinated_boundary(node,parent):
 own=marker(node)
 if own is None or own.get('policy')!=POLICY:return BOUNDARY(node,parent)
 assert set(own)=={'policy','proof','member'}
 proof,candidates,edges=load(own['proof'],parent);name=own['member']
 assert name in candidates and legacy.canonical_sha(node)==proof['members'][name]['canonicalSHA256']
 callbacks=[finite_callback({n:candidates[n]for n in edge},name)for edge in edges if name in edge]
 assert callbacks
 return lambda x,y,z:any(f(x,y,z)for f in callbacks)

def validate_effective_coordinated_members(nodes):
 ordinary=[n for n in nodes if not marker(n)or marker(n).get('policy')!=POLICY]
 EFFECTIVE(ordinary);checked=set()
 for node in nodes:
  own=marker(node)
  if not own or own.get('policy')!=POLICY:continue
  assert set(own)=={'policy','proof','member'}
  proof,candidates,_=load(own['proof'])
  assert own['member']in candidates and legacy.canonical_sha(node)==proof['members'][own['member']]['canonicalSHA256']
  key=(own['proof']['path'],own['proof']['sha256'])
  if key in checked:continue
  old=legacy.reference(proof['oldNative'])
  assert not any(legacy.canonical_sha(n)==legacy.canonical_sha(old)for n in nodes),'Old whole parent remains effective'
  for name,candidate in candidates.items():
   matches=[n for n in nodes if tuple(n['coarseCells'])==tuple(candidate['coarseCells'])and legacy.canonical_sha(n)==proof['members'][name]['canonicalSHA256']]
   assert len(matches)==1 and marker(matches[0])==dict(policy=POLICY,proof=own['proof'],member=name),'All five exact members must be effective once'
  checked.add(key)

@contextmanager
def private_validator():
 assert legacy.coordinated_boundary is BOUNDARY and legacy.validate_effective_coordinated_members is EFFECTIVE
 legacy.coordinated_boundary=coordinated_boundary;legacy.validate_effective_coordinated_members=validate_effective_coordinated_members
 try:yield
 finally:legacy.coordinated_boundary=BOUNDARY;legacy.validate_effective_coordinated_members=EFFECTIVE
