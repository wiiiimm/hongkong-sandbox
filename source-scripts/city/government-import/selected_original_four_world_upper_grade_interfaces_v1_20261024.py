"""Exact finite upper-grade interfaces on named unchanged source walls; no approval."""
import argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--face',type=int,action='append',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch;ids=sorted(a.face);assert ids==sorted(set(ids))and len(ids)<=40
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds=dict(original=decode_original_world_triangles(raw),**{n:np.asarray(attr[k]).reshape(-1,3)[ix]for n,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]});assert np.array_equal(worlds['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(ground)and np.isfinite(ground).all();assert np.all(shapely.area(shapely.polygons(ground[:,:,[0,2]]))>0),'Zero-XZ terrain requires separate exact vertical-facet context; do not omit it';rows=[]
    for name,tri in worlds.items():
        assert len(tri)==row['triangles']and all(0<=i<len(tri)for i in ids);norm=np.cross(tri[ids,1]-tri[ids,0],tri[ids,2]-tri[ids,0]);length=np.linalg.norm(norm,axis=1);assert np.all(length>0)and np.all(abs(norm[:,1])<=.25*length)
        proof=exact_upper_ground_interfaces(tri,ids,ground);assert {r['sourceFace']for r in proof}==set(ids)
        record=dict(mode=name,sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),completeGroundFacets=len(ground),namedOriginalWallFaces=ids,exactFiniteUpperGradeInterfaces=proof);save(out/(name+'.json.gz'),record);rows.append(dict(mode=name,sourceWorldSHA256=record['sourceWorldSHA256'],groundSHA256=record['groundSHA256'],namedFaces=ids,positiveFiniteInterfaces=len(proof)));print(rows[-1],flush=True)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact positive-dimensional zero-gap intervals on complete actual finite upper ground, with every coverage/height breakpoint partitioned. All terrain facets retained and no zero-XZ omission. This geometric interface proof is not a structural/architectural role, cap path, component root, physical or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']);module('named_wall_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-named-original-wall-finite-upper-grade-interfaces',refs,result)


if __name__=='__main__':main()
