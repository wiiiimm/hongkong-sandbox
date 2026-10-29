"""Read-only nearest indexed terrain-plane nomination for exact rejected points."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import fuying_whole_parent_five_boundary_v1_20261029 as boundary
from coordinated_native_boundary_v1_20261023 import seam_segments,value,rational
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-boundary-local-plane-nomination-v1-20261029';WITNESS='government-xl-fuying181489-five-boundary-witnesses-v2-20261029';CANDIDATE='government-xl-fuying181489-five-member-boundary-contract-v1-20261029'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'fuying_whole_parent_five_boundary_v1_20261029.py'];pins={}
 for batch in [WITNESS,CANDIDATE]:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
 def take(batch,p):assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 summary=take(CANDIDATE,BASE/CANDIDATE/'summary.json');proofpath=BASE/CANDIDATE/'whole-parent-contract.json';proof=take(CANDIDATE,proofpath);pref=dict(path=str(proofpath.relative_to(ROOT)),sha256=digest(proofpath.read_bytes()));_,candidates,edges=boundary.load(pref);rows=[]
 for member in summary['members']:
  name=member['member'];witness=take(WITNESS,BASE/WITNESS/(name+'-witnesses.json'));node=take(CANDIDATE,ROOT/member['candidate']['path']);tri=boundary.legacy.triangles(node);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nonvertical=np.abs(normal[:,1])>1e-10
  for w in witness['witnesses']:
   p=np.asarray(w['point']);near=nonvertical&np.all(tri[:,:,[0,2]].min(1)<=p[[0,2]]+.01,axis=1)&np.all(tri[:,:,[0,2]].max(1)>=p[[0,2]]-.01,axis=1);ids=np.flatnonzero(near);options=[]
   for i in ids:
    planeY=float(tri[i,0,1]-(normal[i,0]*(p[0]-tri[i,0,0])+normal[i,2]*(p[2]-tri[i,0,2]))/normal[i,1]);distance=float(shapely.distance(shapely.Polygon(tri[i,:,[0,2]].T),shapely.Point(p[0],p[2])))
    options.append(dict(faceIndex=int(i),distanceXZ=distance,sourcePlaneY=planeY,sourcePlaneDeltaY=float(p[1]-planeY),face=tri[i].tolist()))
   options.sort(key=lambda q:(abs(q['sourcePlaneDeltaY'])>=.01,q['distanceXZ'],abs(q['sourcePlaneDeltaY'])))
   mates=[]
   for pair in edges:
    if name not in pair:continue
    mate=next(n for n in pair if n!=name);a=shapely.box(*boundary.legacy.bounds(candidates[name]));edge=a.boundary.intersection(shapely.box(*boundary.legacy.bounds(candidates[mate])).boundary);xy=list(edge.coords);axis=0 if xy[0][0]==xy[1][0]else 2;other=2 if axis==0 else 0;coordinate=xy[0][0 if axis==0 else 1];lo=min(t[1 if axis==0 else 0]for t in xy);hi=max(t[1 if axis==0 else 0]for t in xy)
    if abs(p[axis]-coordinate)>=.002 or not lo<=p[other]<=hi:continue
    segments=seam_segments(boundary.legacy.triangles(candidates[mate]),axis,coordinate,lo,hi);t=rational(p[other]);covered=[s for s in segments if s[0]<=t<=s[1]];assert covered
    expected=float(max(value(s,t)for s in covered));mates.append(dict(member=mate,axis=axis,coordinate=coordinate,expectedMateY=expected,pointDeltaM=float(p[1]-expected)))
   rows.append(dict(member=name,point=w['point'],closestPlaneCandidates=options[:3],mateCurves=mates,hasLocalPlaneWithin1cm=bool(options and abs(options[0]['sourcePlaneDeltaY'])<.01 and options[0]['distanceXZ']<.01),hasFiniteMateWithin1cm=any(abs(q['pointDeltaM'])<.01 for q in mates)))
 result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],witnesses=rows,allHaveLocalPlaneNomination=all(q['hasLocalPlaneWithin1cm']for q in rows),allHaveFiniteMateNomination=all(q['hasFiniteMateWithin1cm']for q in rows),sourceGeometryChanges=0,candidateChanges=False,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Source-bound point/plane and finite-mate nomination only. No derived connector, geometry edit, same-triangle proof, complete-surface height/coverage, renderer or model approval.')
 save(out/'summary.json',result);module('fuying_local_plane_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'read-only-complete-boundary-point-local-plane-and-finite-mate-nomination',refs,result);print(dict(witnesses=len(rows),planes=result['allHaveLocalPlaneNomination'],mates=result['allHaveFiniteMateNomination']),flush=True)
if __name__=='__main__':main()
