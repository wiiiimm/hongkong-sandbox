"""Exact unchanged original component/context orthographic evidence, no credit."""
import argparse,json,importlib.util
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--support',required=True);p.add_argument('--physical',required=True);p.add_argument('--component',required=True,action='append',type=int);p.add_argument('--batch',required=True);a=p.parse_args();doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists()
 graphpath=ROOT/a.support/'diagnostic.json.gz';selectionpath=ROOT/a.physical/'selection.json.gz';g=read(graphpath);rows=read(selectionpath)['rows'];assets=[ROOT/r['candidate']['path'] for r in rows];assert all(digest(p.read_bytes())==r['sourceSHA256'] for p,r in zip(assets,rows));tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 fig,axes=plt.subplots(len(a.component),3,figsize=(15,3*len(a.component)),squeeze=False);records=[]
 for rr,k in enumerate(a.component):
  ids=g['components'][k]['globalOriginalFaces'];part=tri[ids];lo=part.min(axis=(0,1));hi=part.max(axis=(0,1));pad=np.asarray([.8,.8,.8]);near=np.flatnonzero(np.all(tri.max(axis=1)>=lo-pad,axis=1)&np.all(tri.min(axis=1)<=hi+pad,axis=1));context=[int(i) for i in near if i not in ids];origin=lo.copy();origin[1]=0
  for ax,dims,title in zip(axes[rr],[(0,2),(0,1),(2,1)],['plan','x/elevation','z/elevation']):
   ax.add_collection(PolyCollection((tri[context]-origin)[:,:,dims],facecolors='#d8e4eb',edgecolors='#7e8a91',linewidths=.2,alpha=.3));ax.add_collection(PolyCollection((part-origin)[:,:,dims],facecolors='#df5858',edgecolors='#822222',linewidths=.7,alpha=.9));ax.set_xlim(lo[dims[0]]-origin[dims[0]]-pad[dims[0]],hi[dims[0]]-origin[dims[0]]+pad[dims[0]]);ax.set_ylim(lo[dims[1]]-origin[dims[1]]-pad[dims[1]],hi[dims[1]]-origin[dims[1]]+pad[dims[1]]);ax.set_aspect('equal');ax.set_title(f'Original component {k}: {title}');ax.grid(alpha=.2)
  records.append(dict(component=k,everyOriginalDetailFace=ids,contextOriginalSourceFaces=context,croppedSourceBounds=[(lo-pad).tolist(),(hi+pad).tolist()]))
 fig.suptitle('Untouched original government details in complete original context\nRed = every detail facet; grey = nearby original facets. Geometry evidence only.');fig.tight_layout();doc.mkdir(parents=True);out=doc/('original-detail-context-1800x'+str(360*len(a.component))+'.png');fig.savefig(out,dpi=120);plt.close(fig)
 refs=[ref(q) for q in [Path(__file__),graphpath,selectionpath,*assets]];save(doc/'render.json',dict(uids=[r['uid'] for r in rows],completeOriginalWorldSHA256=digest(tri.tobytes()),details=records,width=1800,height=360*len(a.component),output=ref(out),evidenceRefs=refs,sourceGeometryChanges=0,installationApproved=False))
 spec=importlib.util.spec_from_file_location('visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'unchanged-original-component-context-orthographic-visual-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in rows],sourceComponents=len(a.component),scriptFullAcceptancePassed=False))
 print(out,flush=True)
if __name__=='__main__':main()
