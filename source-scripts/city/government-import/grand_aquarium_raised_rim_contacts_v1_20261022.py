"""Nominate finite unchanged original-wall ground contacts for raised rim warnings."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import intersection_points,rational_face
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-raised-rim-contacts-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();rp=BASE/'government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022';ap=BASE/'government-xl-grand-aquarium-contact-warning-attribution-v1-20261022';_,pins=authenticate(rp);_,atpins=authenticate(ap);gp=HERE/'local'/rp.name/'runtime-geometry.json.gz';at=ap/'93424:0.json.gz';assert digest(gp.read_bytes())==pins[str(gp.relative_to(ROOT))]and digest(at.read_bytes())==atpins[str(at.relative_to(ROOT))];g=read(gp)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ids=np.flatnonzero(valid);tree=shapely.STRtree(polys[valid]);rows=[];cache={}
 for w in read(at)['warnings']:
  if w['reason']!='raised-rim':continue
  witness=np.asarray(w['point']);ceiling=F.from_float(float(witness[1]+.001));qualified=None;attempts=0
  for i in w['originalIncidentFaces']:
   if i not in cache:
    cache[i]=[];projection=shapely.MultiPoint(tri[i][:,[0,2]]).convex_hull
    for j in ids[tree.query(projection,predicate='intersects')]:
     points=intersection_points(rational_face(tri[i]),rational_face(ground[j]));attempts+=1
     if len(points)>=2:cache[i].append((int(j),sorted(points)))
   for j,points in cache[i]:
    p=min(points,key=lambda p:p[1])
    if p[1]>ceiling:continue
    face=tri[i];normal=np.cross(face[1]-face[0],face[2]-face[0]);residual=abs(float((witness-face[0])@normal))/float(np.linalg.norm(normal));assert residual<=.001
    qualified=dict(sourceFace=i,terrainFace=j,exactContactPoints=[[str(v)for v in p]for p in points],chosenExactContact=[str(v)for v in p],contactPoint=[float(v)for v in p],maximumStraightPathHeightM=max(float(witness[1]),float(p[1])),endpointHeightCeilingM=float(ceiling),witnessPlaneResidualM=residual,finitePositiveDimensionalSourceTerrainIntersection=True,sourcePointFromAuthenticatedIncidentVertexOrEdge=True,qualification='Finite incident-wall contact nomination and endpoint height bound only; original triangle is convex. Complete source, wall role, foreign scope and publication remain independent.');break
   if qualified:break
  rows.append(dict(witness=w,positiveIncidentContact=qualified,exactPairsTested=attempts));print(dict(sample=w['sampleIndex'],hasContact=qualified is not None),flush=True)
 result=dict(uids=['landsd/93424:0'],raisedRimWarnings=len(rows),positiveIncidentContacts=sum(r['positiveIncidentContact']is not None for r in rows),rows=rows,installationApproved=False,sourceGeometryChanges=0,newlyInstalled=0);save(doc/'contacts.json.gz',result);save(doc/'summary.json',{k:v for k,v in result.items()if k!='rows'});refs=[Path(__file__),rp/'result.json',ap/'result.json',gp,at,HERE/'exact_original_shell_intersections_20261009.py'];module('aquarium_raised_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-raised-rim-finite-incident-contact-nomination',refs,{k:v for k,v in result.items()if k!='rows'})
if __name__=='__main__':main()
