"""Inspect original small source and podium against fresh official footprint."""
from pathlib import Path
import numpy as np,shapely,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho301659-compound-context-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho-seven-original-paths-v1-20261020';PRIMARY=BASE/'government-xl-yoho-seven-primary-records-v1-20261020';UID='landsd/301659:0';POD='landsd/301636:0'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [SRC,PRIMARY]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def consume(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
w=consume(HERE/'local'/SRC.name/'original.json.gz')['worlds'];t=np.asarray(w[UID]);s=np.asarray(w[POD]);feature=next(x for x in consume(PRIMARY/'footprints.json')['features']if x['attributes']['BuildingCSUID']=='2167634103T20221222');target=shapely.Polygon()
for ring in feature['geometry']['rings']:target=target.symmetric_difference(shapely.Polygon([(x-834500,816500-y)for x,y in ring]))
a=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));b=shapely.union_all(shapely.polygons(s[:,:,[0,2]]));contact=exact_finite_contacts(t,list(range(len(t))),s,list(range(len(s))));positive=[x for x in contact['contacts']if x['sourcePrimitiveDimensionA']==2 and x['sourcePrimitiveDimensionB']==2 and x['dimension']>0];summary=dict(uid=UID,sourceWorldSHA256=digest(t.tobytes()),podiumWorldSHA256=digest(s.tobytes()),ownSourceFootprintCoverage=float(a.intersection(target).area/target.area),podiumFootprintCoverage=float(b.intersection(target).area/target.area),compoundFootprintCoverage=float(a.union(b).intersection(target).area/target.area),sourceToTargetDistanceM=float(a.distance(target)),positiveOriginalPodiumContacts=len(positive),installationApproved=False)
save(DOC/'context.json',summary);save(DOC/'contacts.json.gz',contact);origin=np.array([target.centroid.x,0,target.centroid.y]);bounds=target.union(a).bounds;extent=[bounds[0]-8,bounds[1]-8,bounds[2]+8,bounds[3]+8];mask=(s[:,:,0].max(1)>=extent[0])&(s[:,:,0].min(1)<=extent[2])&(s[:,:,2].max(1)>=extent[1])&(s[:,:,2].min(1)<=extent[3]);near=s[mask]
fig=plt.figure(figsize=(14,7));ax=fig.add_subplot(1,2,1);ax.add_collection(PolyCollection((near-origin)[:,:,[0,2]],facecolors='#bcd2df',edgecolors='#7896a8',linewidths=.15));ax.add_collection(PolyCollection((t-origin)[:,:,[0,2]],facecolors='#d87542',edgecolors='none'));q=np.array(target.exterior.coords)-origin[[0,2]];ax.plot(q[:,0],q[:,1],'k-',lw=2);ax.set(xlim=(extent[0]-origin[0],extent[2]-origin[0]),ylim=(extent[1]-origin[2],extent[3]-origin[2]));ax.set_aspect('equal');ax.set_title('Black: fresh official footprint; orange: small source')
ax=fig.add_subplot(1,2,2,projection='3d');ax.add_collection3d(Poly3DCollection((near-origin)[:,:,[0,2,1]],facecolors='#bcd2df',edgecolors='#7896a8',linewidths=.15,alpha=.4));ax.add_collection3d(Poly3DCollection((t-origin)[:,:,[0,2,1]],facecolors='#d87542',edgecolors='none'));ax.set(xlim=(extent[0]-origin[0],extent[2]-origin[0]),ylim=(extent[1]-origin[2],extent[3]-origin[2]),zlim=(20,38));ax.view_init(elev=25,azim=35);fig.suptitle('Unchanged government sources; cropped transparent context, not identity approval');fig.savefig(DOC/'context.png',dpi=140);plt.close(fig)
refs.extend([HERE/'exact_original_finite_triangle_contacts_20261010.py']);module('yoho_compound_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'small-original-compound-footprint-context',refs,dict(uids=[UID,POD],**summary));print(summary,flush=True)
