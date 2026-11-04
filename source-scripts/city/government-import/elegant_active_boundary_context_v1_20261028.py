"""Bounded source-contact context and strict Block2/BASIC vertical separation."""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_footing_prism_contacts_v1_20261028 import clip
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('active-boundary-source-context-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 contact_batch=PREFIX+'active-boundary-contacts-v1-20261028';contacts=take(contact_batch,'summary.json');parts=take(contact_batch,'basic-parts.json')['rows'];selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']}
 attrs=take(PREFIX+'sixteen-original-final-attributes-v1-20261028','attributes.json.gz');attributes={r['uid']:r for r in attrs['rows']};geometry={}
 for uid in ['landsd/236170:0','landsd/173767:0','landsd/173532:0']:
  r=sources[uid];path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256'];refs.append(path);geometry[uid]=decode_original_world_triangles(path.read_bytes())
 separation=[];basic=next(r for r in parts if r['uid']=='landsd/213586:0');highest=max(p['top']for s in ['before','after']for p in basic[s]['parts']);r=attributes['landsd/173532:0'];index=np.asarray(r['completeOriginalIndex']).reshape(-1,3)
 for mode,field in [('original',None),('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  tri=geometry['landsd/173532:0']if field is None else np.asarray(r[field]).reshape(-1,3)[index]
  low=float(tri[:,:,1].min());assert low>highest
  separation.append(dict(mode=mode,sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeSourceFaces=len(tri),wholeSourceMinimumY=low,wholeBasicMaximumY=highest,strictGlobalVerticalGapM=low-highest))
 source_b=sources['landsd/173532:0'];basic_input=take(contact_batch,'basic-part-input.json')['rows'];b=next(r['building']for r in basic_input if r['building']['uid']=='landsd/213586:0')
 review=dict(sourceUid='landsd/173532:0',otherUid=b['uid'],reviewer='Codex ROOT: exact strict interval proof',reviewType='complete-unchanged-original-vs-retained-basic-global-vertical-separation-only',interfaceSeparationApproved=True,sourceSHA256=source_b['sourceSHA256'],rows=separation,sourceGeometryChanges=0,physicalAccepted=False,identityAccepted=False,installationApproved=False,publication=False,
  basis='Every original source vertex in all4coordinate streams is strictly above every rendered BASIC body/footing part. The entire height intervals are disjoint by more than7m, without an epsilon or changed threshold. This resolves physical interference for the exact0.001486m²baseline projection-overlap pair only. It grants no tower support, source identity, other-interface, whole-group or publication approval.')
 save(out/'block2-basic-podium-separation-review.json',review)
 contexts=[];figures=[]
 for name,left,right in [('louis-seam','landsd/236170:0','landsd/173767:0'),('canopy-existing-interfaces','landsd/236170:0','landsd/99061:0')]:
  original_rows=[r for r in contacts['rows']if r['sourceUid']==left and r['otherUid']==right and r['mode']=='original'and(r.get('state','after')=='after')]
  points=[];face_ids=set();contact_records=[]
  for row in original_rows:
   proof=take(contact_batch,row['proof'])
   for c in proof['contacts']:
    pts=c.get('exactPoints',c.get('exactClippedPoints'));points.extend([[float(F(v))for v in p]for p in pts]);face_ids.add(c.get('sourceFaceA',c.get('sourceFace')));contact_records.append(dict(row=row,contact=c))
  assert points
  triangles_a=geometry[left]
  if right=='landsd/99061:0':
   br=next(r for r in parts if r['uid']==right);triangles_b=np.concatenate([np.asarray(p['position']).reshape(-1,3)[np.asarray(p['index']).reshape(-1,3)]for p in br['after']['parts']])
   before_after=[]
   for mode in ['original','literal','leftF32','balancedF32']:
    before=[r for r in contacts['rows']if r['sourceUid']==left and r['otherUid']==right and r['mode']==mode and r.get('state')=='before'];after=[r for r in contacts['rows']if r['sourceUid']==left and r['otherUid']==right and r['mode']==mode and r.get('state')=='after'];assert len(before)==len(after)==3
    for x,y in zip(before,after):
     cp=take(contact_batch,x['proof'])['contacts'];cq=take(contact_batch,y['proof'])['contacts'];assert cp==cq
     before_after.append(dict(mode=mode,partIndex=x['partIndex'],partKind=x['partKind'],completeContactRecordsExactlyUnchanged=True,contacts=len(cp)))
  else:triangles_b=geometry[right];before_after=[]
  p=np.asarray(points);lo=p.min(0)-[3,2.5,3];hi=p.max(0)+[3,2.5,3]
  facets=[]
  for i in sorted(face_ids):
   f=triangles_a[i];n=np.cross(f[1]-f[0],f[2]-f[0]);facets.append(dict(sourceFace=int(i),vertices=f.tolist(),normal=n.tolist(),normalYOverLength=float(n[1]/np.linalg.norm(n))if np.linalg.norm(n)else None))
  contexts.append(dict(name=name,sourceUid=left,otherUid=right,contactSourceFaces=sorted(map(int,face_ids)),contactPointsYRange=[float(p[:,1].min()),float(p[:,1].max())],facets=facets,beforeAfterContacts=before_after,contactRecords=contact_records,physicalAccepted=False))
  def display_polygons(triangles):
   polygons=[]
   for f in triangles:
    if np.any(f.max(0)<lo)or np.any(f.min(0)>hi):continue
    q=[tuple(map(float,v))for v in f]
    for axis in range(3):
     q=clip(q,lambda v,axis=axis:v[axis]-lo[axis]);q=clip(q,lambda v,axis=axis:hi[axis]-v[axis])
    if q:polygons.append(np.asarray(q)[:,[0,2,1]])
   return polygons
  polygons_a,polygons_b=display_polygons(triangles_a),display_polygons(triangles_b)
  for view,(elev,azim)in enumerate([(25,-65),(25,65),(75,-90)]):
   fig=plt.figure(figsize=(13,10),dpi=140);ax=fig.add_subplot(projection='3d')
   for polygons,color in [(polygons_a,'#5482ae'),(polygons_b,'#e1a658')]:ax.add_collection3d(Poly3DCollection(polygons,facecolor=color,edgecolor='#28333d',linewidth=.25,alpha=.76))
   for item in contact_records:
    q=np.asarray([[float(F(v))for v in v]for v in item['contact'].get('exactPoints',item['contact'].get('exactClippedPoints'))]);q=q[:,[0,2,1]];ax.plot(q[:,0],q[:,1],q[:,2],color='#cf163e',linewidth=2);ax.scatter(q[:,0],q[:,1],q[:,2],color='#cf163e',s=8)
   ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]),xlabel='World X / m',ylabel='World Z / m',zlabel='Height / m',title=name+'\nBlue: '+left+' | amber: '+right+' | red: exact contacts\nDisplay crop only; every full primitive checked separately. Not whole-scene acceptance.')
   ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.view_init(elev=elev,azim=azim);fig.tight_layout();file=out/(name+'-'+str(view)+'.png');fig.savefig(file);plt.close(fig);figures.append(dict(path=str(file.relative_to(ROOT)),sha256=digest(file.read_bytes()),sourceUid=left,otherUid=right))
  print(dict(name=name,contactSourceFaces=len(face_ids),contactY=[float(p[:,1].min()),float(p[:,1].max())]),flush=True)
 lookup=[];keys={r['native']['cacheKey']:r['native']['resultSha']for r in sources.values()}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,sha in keys.items():
   assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(sha,)
   matches=db.execute("SELECT m FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m WHERE r.cache_key=%s AND m->>'modelId' LIKE %s ORDER BY m->>'modelId'",(key,'B3228616401%')).fetchall()
   lookup.append(dict(cacheKey=key,resultSHA256=sha,georefPrefix='B3228616401',models=[m for(m,)in matches],scope='These two pinned prepared sheet revisions only; not a claim of government-wide source absence.'))
 save(out/'canopy-exact-prefix-lookup.json',lookup)
 result=dict(uids=['landsd/173532:0','landsd/236170:0','landsd/173767:0','landsd/99061:0','landsd/213586:0'],status='active-boundary-role-context-and-one-strict-separated-interface',block2BasicInterfaceSeparationApproved=True,contexts=contexts,figures=figures,canopyPreparedSourceLookup=lookup,sourceGeometryChanges=0,physicalAccepted=False,identityAccepted=False,installationApproved=False,publication=False,
  qualification='The Block2/BASIC podium pair has a strict complete-height interval separation in all4worlds. Other contacts are preserved for source-role interpretation, with full source facets and before/after BASIC contact equality. Display-cropped isolated plots are not whole-scene or collision approval. No source/BASIC mesh or pose is edited; no optional native Rex podium is activated.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('active_boundary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'active-boundary-source-role-context-and-strict-block2-basic-separation',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
