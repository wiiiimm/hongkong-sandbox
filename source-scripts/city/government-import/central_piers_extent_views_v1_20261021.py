"""Exact original pier extent faces and independent TD location-plan evidence."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-primary-plan-v1-20261021';DOC=BASE/BATCH
assert not (DOC/'result.json').exists();refs=[Path(__file__)];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
sn='government-xl-next-twenty-current-terrain-v6-20261021';rows=take(sn,BASE/sn/'selection.json.gz')['rows'];summaries=[]
fig,axes=plt.subplots(2,3,figsize=(18,11))
for line,uid in enumerate(['landsd/213352:0','landsd/285475:0']):
 row=next(r for r in rows if r['uid']==uid);path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path);tri=decode_original_world_triangles(path.read_bytes())
 fn='government-xl-six-far-faces-v1-20261021';far=take(fn,BASE/fn/(uid.split('/')[1]+'.json.gz'));assert far['sourceSHA256']==row['sourceSHA256'] and far['worldTrianglesSHA256']==digest(tri.astype('<f8').tobytes());ids=far['farFaceIds'];assert np.array_equal(tri[ids],np.asarray(far['farFaceVertices']))
 for ax,coords in zip(axes[line],[(0,2),(0,1),(2,1)]):
  ax.add_collection(PolyCollection(tri[:,:,coords],facecolors='#94a3b8',edgecolors='none',alpha=.3))
  ax.add_collection(PolyCollection(tri[ids][:,:,coords],facecolors='#dc2626',edgecolors='#b91c1c',linewidth=.15,alpha=.85))
  lo=tri[:,:,coords].min((0,1));hi=tri[:,:,coords].max((0,1));ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[1]-2,hi[1]+2);ax.set_aspect('equal');ax.set_title(row['source']['building'].get('name')+' '+str(coords));ax.ticklabel_format(useOffset=False)
 summaries.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],worldSHA256=far['worldTrianglesSHA256'],farFaceIds=ids,farBounds=far['farBounds'],sourceBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()]))
fig.suptitle('Unchanged original pier sources; all >10m extent faces highlighted red. No geometry edits.')
fig.tight_layout();fig.savefig(DOC/'source-extent-views.png',dpi=150);plt.close(fig)
pdf=DOC/'td-ferry-eoi-2018.pdf';assert pdf.read_bytes().startswith(b'%PDF');assert (DOC/'central-pier8-plan.png').exists()
provenance=dict(url='https://www.td.gov.hk/filemanager/en/content_734/eoi_c-hh_and_wt_final.pdf',publisher='Hong Kong Transport Department',documentDate='2018-08',retrievedDate='2026-10-21',sha256=digest(pdf.read_bytes()),page=25,pageIndex=24,scope='Historical official location plan. Contextual comparison only; not surveyed pixel registration, present-day geometry certification or source-face correspondence by itself.',rootInspectedPlan=True)
save(DOC/'provenance.json',provenance);save(DOC/'source-bindings.json',dict(rows=summaries,installationApproved=False))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.append(HERE/'exact_packed_world_geometry_20261009.py')
r=module('central_pier_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'official-pier-plan-and-complete-source-extent-views',refs,dict(uids=[r['uid']for r in summaries],sourceGeometryChanges=0,identityApproved=False,installationApproved=False));print(r['jobId'],flush=True)
