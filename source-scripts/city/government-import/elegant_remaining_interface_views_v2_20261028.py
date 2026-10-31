"""Batch all remaining source contact-role views; diagnostic-only original geometry."""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_footing_prism_contacts_v1_20261028 import clip
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists();rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('remaining-interface-batch-views-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 matrix_batch=PREFIX+'activation-interference-matrix-v1-20261028';matrix=take(matrix_batch,'summary.json');rows=take(matrix_batch,'rows.json.gz');basics={r['uid']:r for r in take(matrix_batch,'basic-parts.json')['rows']}
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']};geometry={}
 attrs={r['uid']:r for r in take(PREFIX+'sixteen-original-final-attributes-v1-20261028','attributes.json.gz')['rows']}
 def world(uid,mode):
  if mode=='original':return geometry[uid]
  fields={'literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'};a=attrs[uid];return np.asarray(a[fields[mode]]).reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
 for uid,r in sources.items():
  path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256'];refs.append(path);geometry[uid]=decode_original_world_triangles(path.read_bytes())
 cases=[]
 for left,right in matrix['positiveOriginalPairs']:
  if {left,right}=={'landsd/236170:0','landsd/173767:0'}:continue # Already reviewed with three inspected views.
  row=next(r for r in rows if r['kind']=='original-original'and r['sourceUid']==left and r['otherUid']==right and r['contacts']>0)
  proof=take(matrix_batch,row['proof']);cases.append(dict(left=left,right=right,contacts=proof['contacts'],ta=world(left,row['mode']),tb=world(right,row['mode']),mode=row['mode'],kind='native-native'))
 left,right='landsd/257493:0','landsd/336456:0';row=next(r for r in rows if r['kind']=='original-basic'and r['sourceUid']==left and r['otherUid']==right and r['mode']=='original'and r['state']=='after');contacts=[]
 for ref in row['contactProofs']:contacts.extend(take(matrix_batch,ref['proof'])['contacts'])
 b=basics[right]['after'];tb=np.concatenate([np.asarray(p['position']).reshape(-1,3)[np.asarray(p['index']).reshape(-1,3)]for p in b['parts']]);cases.append(dict(left=left,right=right,contacts=contacts,ta=geometry[left],tb=tb,mode='original',kind='native-basic'))
 assert len(cases)==14
 contexts=[];cards=[]
 for i,case in enumerate(cases):
  points=[];segments=[]
  for c in case['contacts']:
   q=np.asarray([[float(Fraction(v))for v in p]for p in c.get('exactPoints',c.get('exactClippedPoints'))]);points.extend(q);segments.append(q[:,[0,2,1]])
  q=np.asarray(points);lo=q.min(0)-[2,1.5,2];hi=q.max(0)+[2,1.5,2]
  def polygons(tri):
   result=[]
   for f in tri:
    if np.any(f.max(0)<lo)or np.any(f.min(0)>hi):continue
    p=[tuple(map(float,v))for v in f]
    for axis in range(3):
     p=clip(p,lambda v,axis=axis:v[axis]-lo[axis]);p=clip(p,lambda v,axis=axis:hi[axis]-v[axis])
    if len(p)>=3:result.append(np.asarray(p)[:,[0,2,1]])
   return result
  left_polys,right_polys=polygons(case['ta']),polygons(case['tb'])
  ids=sorted({c.get('sourceFaceA',c.get('sourceFace'))for c in case['contacts']});facets=[]
  for face in ids:
   f=case['ta'][face];n=np.cross(f[1]-f[0],f[2]-f[0]);facets.append(dict(sourceFace=int(face),vertices=f.tolist(),normal=n.tolist()))
  contexts.append(dict(sourceUid=case['left'],otherUid=case['right'],kind=case['kind'],mode=case['mode'],contacts=len(case['contacts']),completeContactYRange=[float(q[:,1].min()),float(q[:,1].max())],sourceFacets=facets,sourceGeometryChanges=0,physicalAccepted=False))
  for elev,azim in [(28,-65),(65,65)]:cards.append((i,case,elev,azim,lo,hi,left_polys,right_polys,segments))
  print('prepared',i,case['left'],case['right'],len(case['contacts']),flush=True)
 images=[]
 for page,start in enumerate(range(0,len(cards),8)):
  fig=plt.figure(figsize=(24,13),dpi=140)
  for slot,(i,case,elev,azim,lo,hi,pa,pb,segs)in enumerate(cards[start:start+8]):
   ax=fig.add_subplot(2,4,slot+1,projection='3d')
   for polys,color in [(pa,'#5482ae'),(pb,'#e1a658')]:ax.add_collection3d(Poly3DCollection(polys,facecolor=color,edgecolor='#364250',linewidth=.2,alpha=.72))
   for q in segs:ax.plot(q[:,0],q[:,1],q[:,2],color='#d0133d',linewidth=1.4)
   ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]),title=str(i)+': '+case['left'].split('/')[1]+' blue / '+case['right'].split('/')[1]+' amber\n'+str(len(case['contacts']))+' contacts ('+case['mode']+')',xlabel='X',ylabel='Z',zlabel='HKPD m');ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.view_init(elev=elev,azim=azim)
  fig.suptitle('Complete remaining interface-role packet: display crops only; original assets unchanged; no acceptance',fontsize=18);fig.tight_layout();path=out/('interfaces-page-'+str(page)+'.png');fig.savefig(path);plt.close(fig);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),cardIndices=list(range(start,min(start+8,len(cards))))))
 save(out/'contexts.json',contexts);result=dict(uids=matrix['uids'],cases=len(cases),views=len(cards),images=images,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='All13 still-unreviewed positive native interfaces plus Grand Scholar/BASIC canopy roof interface, first positive coordinate-stream contacts explicitly labelled and highlighted in two local views each. Complete four-world contact proofs remain separately frozen. Display cropping is visualisation only and does not remove source faces from checks. Requires actual ROOT inspection and bounded role decisions; no automatic acceptance.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_footing_prism_contacts_v1_20261028.py'])
 module('remaining_interface_views_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'all-remaining-native-contact-and-retained-canopy-interface-role-views',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()
