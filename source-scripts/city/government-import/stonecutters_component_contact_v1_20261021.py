"""Measure exact component vertices against all remaining original faces; diagnostic only."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stonecutters-component-contact-v1-20261021';DOC=BASE/BATCH;assert not DOC.exists();refs=[Path(__file__),HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py']
def take(n,f):
 _,pins=authenticate(BASE/n);p=BASE/n/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
c=take('government-xl-stonecutters-far-components-v1-20261021','components.json');g=next(r for r in take('government-xl-six-extent-review-views-v1-20261021','geometry.json.gz')['rows']if r['uid']==c['uids'][0]);row=next(r for r in take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz')['rows']if r['uid']==c['uids'][0]);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==c['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert digest(tri.astype('<f8').tobytes())==c['worldTrianglesSHA256'];ids=set(c['components'][0]['faceIds']);hostids=[i for i in range(len(tri))if i not in ids];host=tri[hostids];vertices=np.unique(tri[sorted(ids)].reshape(-1,3),axis=0);foot=shapely.from_wkt(g['targetWKT']);details=[]
for v in vertices:
 i,q,d=nearest(v,host);details.append(dict(position=v.tolist(),nearestOtherFace=hostids[i],nearestOtherPoint=q.tolist(),distanceM=d,insideTargetFootprint=bool(shapely.covers(foot,shapely.Point(v[0],v[2])))))
ordered=sorted(details,key=lambda x:x['distanceM']);summary=dict(uids=c['uids'],sourceSHA256=c['sourceSHA256'],verticesChecked=len(vertices),otherFacesChecked=len(hostids),minimumDistanceM=ordered[0]['distanceM'],exactContacts=sum(r['distanceM']==0 for r in details),withinOneMillimetre=sum(r['distanceM']<=.001 for r in details),nearestTen=ordered[:10],sourceGeometryChanges=0,installationApproved=False,qualification='Exact original component vertex-to-all-other-face distances. Contact evidence only, not semantic identity or terrain acceptance.')
save(DOC/'contacts.json.gz',dict(rows=details));save(DOC/'summary.json',summary);module('stone_contact',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-contact-diagnostic',refs,summary);print({k:summary[k]for k in ['verticesChecked','minimumDistanceM','exactContacts','withinOneMillimetre']},flush=True)
