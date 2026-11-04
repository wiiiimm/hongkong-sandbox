"""Recheck exposed, terrain-intersecting original walls without inventing cap/root credit.

The missing-cap diagnostic remains verbatim. This records actual finite grade
contacts and a conservative complete drawn-ground upper bound for each wall.
It never accepts a physical role, source, bridge or installation.
"""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face
from exact_original_component_contacts_20261009 import contact_measure

def wall_evidence(face,ground,contact_ids):
    normal=np.cross(face[1]-face[0],face[2]-face[0]);size=np.linalg.norm(normal)
    assert size>0 and abs(normal[1])<=.25*size,'Only unchanged nondegenerate wall-like faces'
    lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0)
    mask=np.all(ground[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(ground[:,:,[0,2]].min(1)<=hi,axis=1)
    candidate_ids=np.flatnonzero(mask);assert len(candidate_ids)
    upper=float(ground[candidate_ids,:,1].max());top=float(face[:,1].max())
    margin=Fraction(top)-Fraction(upper)
    assert margin>0,'No exposed-top credit when complete ground bound reaches wall top'
    contact=None
    for j in contact_ids:
        assert type(j)is int and 0<=j<len(ground)
        measure=contact_measure(finite_intersection_points(rational_face(face),rational_face(ground[j])))
        if measure['dimension']>0:
            contact=dict(groundFace=j,**measure);break
    assert contact is not None,'A point-only contact or missing grade intersection cannot qualify'
    return dict(completeInclusiveGroundCandidates=len(candidate_ids),completeGroundUpperY=upper,wallHighestY=top,exactExposedMargin=str(margin),independentlyRecomputedPositiveGradeContact=contact)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','uid','runtime','attributes','grade-context']:p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json'
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('original-grade-wall-'+str(uuid.uuid4()),['building:'+a.uid],batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    geom=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']==geom['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[key]).reshape(-1,3)[ix]
    ground=np.asarray(geom['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);rows=[]
    for mode,tri in worlds.items():
        raw=take(a.grade_context,base/a.grade_context/(mode+'.json.gz'))
        assert raw['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())and raw['completeGroundSHA256']==digest(ground.tobytes())
        ids=raw['wallsWithoutSharedEdgeClearCapPath'];assert ids and not raw['negativeNonWallFaces']
        contacts={i:[]for i in ids}
        for c in raw['completePositiveGradeContacts']:
            if c['sourceFaceA']in contacts and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2:contacts[c['sourceFaceA']].append(c['sourceFaceB'])
        evidence=[dict(sourceFace=i,**wall_evidence(tri[i],ground,contacts[i]))for i in ids]
        detail=dict(mode=mode,rawMissingCapFaceIds=ids,sourceWorldSHA256=raw['sourceWorldSHA256'],completeGroundSHA256=raw['completeGroundSHA256'],rows=evidence,rawCapFailurePreserved=True)
        save(out/(mode+'.json.gz'),detail);rows.append(dict(mode=mode,walls=len(ids),allPositiveFiniteGradeContactsRecomputed=True,allTopsExceedCompleteLocalGroundUpperBound=True,minimumExposedMargin=min(float(Fraction(r['exactExposedMargin']))for r in evidence)))
        assert reservations.owns(lease)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,rawCapFailuresPreserved=True,physicalAcceptance=False,sourceRoleAccepted=False,groundRootCredit=False,physicalInterComponentSupportBridgeCredit=False,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'summary.json',result);refs.extend(HERE/f for f in ['exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_packed_world_geometry_20261009.py'])
    module('positive_grade_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-exposed-original-wall-positive-grade-context',list(dict.fromkeys(refs)),result);print(rows,flush=True)
if __name__=='__main__':main()
