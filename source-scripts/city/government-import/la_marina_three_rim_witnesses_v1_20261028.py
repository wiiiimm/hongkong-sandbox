"""Exact finite-face distances for three unresolved original-rim witnesses."""
import argparse,sys,uuid,math
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR='government-xl-six-source-two-case-original-rim-contacts-v1-20261028';BATCH='government-xl-la-marina-three-original-rim-witnesses-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/311761:0'
def inputs():
 _,pins=authenticate(BASE/PRIOR)
 def pinned(name):
  p=BASE/PRIOR/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];return read(p)
 summary=pinned('summary.json');scope=next(r for r in summary['completeOriginalSourceScopes']if r['uid']==UID);row=next(r for r in pinned('input.json.gz')['rows']if r['uid']==UID);report=next(r for r in pinned('contacts.json.gz')['rows']if r['uid']==UID);return scope,row,report

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();scope,row,report=inputs();assert {'building:'+u for u in [UID,*[x['uid']for x in scope['originalSupportMembers']]]}<=set(lease['resources']);points=[r['position']for r in report['mapped']if not r['supportFacesAtOriginalPoint']];assert len(points)==3
 tri=np.asarray(row['support']['position'],float).reshape(-1,3,3);source=np.asarray(row['source']['position'],float).reshape(-1,3,3);assert digest(tri.astype('<f8').tobytes())==row['supportWorldSHA256'];assert digest(source.astype('<f8').tobytes())==row['sourceWorldSHA256'];lo=tri.min(axis=1);hi=tri.max(axis=1);results=[]
 for point in points:
  p=np.asarray(point);assert all(F(float(x+1))-F(float(x))==1 and F(float(x))-F(float(x-1))==1 for x in p)
  ids=np.flatnonzero(((lo<=p+1)&(hi>=p-1)).all(axis=1));distances=[(squared_distance(point,tri[i]),int(i))for i in ids];best=min(x[0]for x in distances);assert best<1;faces=[]
  for distance,i in distances:
   if distance!=best:continue
   member=next(m for m in scope['originalSupportMembers']if m['faceRange'][0]<=i<m['faceRange'][1]);normal=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);norm=float(np.linalg.norm(normal));faces.append(dict(supportUid=member['uid'],sourceSHA256=member['sourceSHA256'],combinedFaceIndex=i,originalMemberFaceIndex=i-member['faceRange'][0],vertices=tri[i].tolist(),unitNormal=(normal/norm).tolist()if norm else None))
  incident=np.flatnonzero((source==p).all(axis=2).any(axis=1));results.append(dict(position=point,nearestDistanceM=math.sqrt(float(best)),exactSquaredDistance=dict(numerator=str(best.numerator),denominator=str(best.denominator)),allCompleteOriginalFacesAccounted=True,examinedFaces=len(ids),omittedFacesAxisSeparatedByMoreThanOneMetre=len(tri)-len(ids),nearestFaces=faces,incidentSourceFaces=[dict(faceIndex=int(i),vertices=source[i].tolist())for i in incident]))
 result=dict(uids=[UID],sourceWorldSHA256=row['sourceWorldSHA256'],supportWorldSHA256=row['supportWorldSHA256'],completeSupportFaces=len(tri),completeSourceFaces=len(source),witnesses=results,sourceGeometryChanges=0,installationApproved=False,physicalAccepted=False,qualification='Exact rational distances to complete finite original support facets; omitted facets have an axis separation greater than 1m, all three minima are below 1m. Source incident faces use exact original vertex equality. Witness context only, no increased tolerance, inferred support role, geometry edit or installation acceptance.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('la_marina_exact_witness_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-unresolved-original-rim-exact-finite-face-distances',[Path(__file__),BASE/PRIOR/'result.json',BASE/PRIOR/'input.json.gz',BASE/PRIOR/'contacts.json.gz',BASE/PRIOR/'summary.json',HERE/'exact_point_triangle_distance_20261018.py'],result);print([(r['position'],r['nearestDistanceM'],[f['supportUid']for f in r['nearestFaces']])for r in results],flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope,_,_=inputs();c=reservations.claim('la-marina-three-exact-witnesses-'+str(uuid.uuid4()),sorted({'building:'+u for u in [UID,*[m['uid']for m in scope['originalSupportMembers']]]}),batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
