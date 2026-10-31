"""Complete CGO projected overlap face context against current neighbouring forms."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-west-wing-other-original-identities-v1-20261018';BATCH='government-xl-west-wing-cgo-overlap-context-v1-20261018';DOC=BASE/BATCH
assert not DOC.exists();receipt=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for e in receipt['evidenceRefs']:
 p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
row=next(r for r in read(SRC/'selection.json.gz')['rows']if r['uid']=='landsd/322270:0');asset=(ROOT/row['candidate']['path']).read_bytes();assert digest(asset)==row['sourceSHA256'];t=np.asarray(decode_original_world_triangles(asset),dtype='<f8');xz=t[:,:,[0,2]];polys=shapely.polygons(xz);raw=read(SRC/'322270:0/identity.json');assert digest(t.tobytes())==raw['worldTrianglesSHA256'];final=module('cgo_overlap_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([t[:,:,0].min()-2,t[:,:,2].min()-2,t[:,:,0].max()+2,t[:,:,2].max()+2]);out=[]
for uid,count in [('landsd/315069:0',8),('landsd/320038:0',33)]:
 form,_,tile=next(r for r in forms if r[0]['uid']==uid);p=Polygon(form['rings'][0],form['rings'][1:]);inter=shapely.intersection(polys,p);ids=np.flatnonzero(shapely.area(inter)>0).tolist();assert len(ids)==count,(uid,len(ids));area=shapely.union_all(inter).area;expected=next(v for v in raw['freshCurrentIdentity']['intersectingForms']if v['uid']==uid);assert abs(area-expected['intersectionAreaM2'])<1e-8
 refs.append(ROOT/'3d-viewer'/tile);selected=t[ids];lo=selected.min((0,1));hi=selected.max((0,1));out.append(dict(uid=uid,sourceFaceIds=ids,originalTriangles=selected.tolist(),intersectionAreaM2=area,sourceBounds=[lo.tolist(),hi.tolist()],form=form,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes())))
 fig=plt.figure(figsize=(15,7));ax=fig.add_subplot(121);ax.add_collection(PolyCollection(xz,facecolors='grey',edgecolors='none',alpha=.15));ax.add_collection(PolyCollection(xz[ids],facecolors='red',edgecolors='darkred',alpha=.7,linewidth=.3));ring=np.asarray(p.exterior.coords);ax.plot(ring[:,0],ring[:,1],color='blue');ax.set_xlim(lo[0]-3,hi[0]+3);ax.set_ylim(lo[2]-3,hi[2]+3);ax.set_aspect('equal');ax.set_title('Red CGO faces; blue neighbouring footprint')
 ax=fig.add_subplot(122,projection='3d');display=selected[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(display,facecolor='red',edgecolor='darkred',alpha=.55,linewidth=.4));ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[2]-1,hi[2]+1);ax.set_zlim(lo[1]-1,hi[1]+1);ax.set_box_aspect(np.maximum((hi-lo)[[0,2,1]],1));ax.view_init(30,-50);ax.set_title('Exact complete overlapping original faces');fig.suptitle(uid);fig.tight_layout();DOC.mkdir(exist_ok=True);fig.savefig(DOC/(uid.split('/')[1]+'.png'),dpi=140);plt.close(fig)
save(DOC/'context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],worldSHA256=digest(t.tobytes()),rows=out,installationApproved=False))
r=module('cgo_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-cgo-two-neighbour-overlap-context',list(dict.fromkeys(refs)),dict(uids=[row['uid'],*[x['uid']for x in out]],installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
