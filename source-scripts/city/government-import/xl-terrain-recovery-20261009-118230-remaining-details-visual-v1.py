"""Untouched remaining source details in cropped original model context."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-remaining-details-visual-v1';DOC=BASE/BATCH
def main():
 assert not (DOC/'render.json').exists();graph=read(BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1/diagnostic.json.gz');row=read(BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw)
 groups=[[330,332],[417,418,419,420],[444]];fig,axes=plt.subplots(3,3,figsize=(15,9));records=[]
 for rr,components in enumerate(groups):
  ids=sorted(i for k in components for i in graph['components'][k]['globalOriginalFaces']);part=tri[ids];lo=part.min(axis=(0,1));hi=part.max(axis=(0,1));pad=np.asarray([2,3,2]);near=np.flatnonzero(np.all(tri.max(axis=1)>=lo-pad,axis=1)&np.all(tri.min(axis=1)<=hi+pad,axis=1));context=[int(i) for i in near if i not in ids];origin=lo.copy();origin[1]=0
  for ax,dims,title in zip(axes[rr],[(0,2),(0,1),(2,1)],['plan','x/elevation','z/elevation']):
   ax.add_collection(PolyCollection((tri[context]-origin)[:,:,dims],facecolors='#d8e4eb',edgecolors='#7e8a91',linewidths=.15,alpha=.35));ax.add_collection(PolyCollection((part-origin)[:,:,dims],facecolors='#df5858',edgecolors='#822222',linewidths=.45,alpha=.9));ax.set_xlim(lo[dims[0]]-origin[dims[0]]-pad[dims[0]],hi[dims[0]]-origin[dims[0]]+pad[dims[0]]);ax.set_ylim(lo[dims[1]]-origin[dims[1]]-pad[dims[1]],hi[dims[1]]-origin[dims[1]]+pad[dims[1]]);ax.set_aspect('equal');ax.set_title(f'Original components {components}: {title}');ax.grid(alpha=.2)
  records.append(dict(components=components,everyOriginalDetailFace=ids,contextOriginalSourceFaces=context,croppedSourceBounds=[(lo-pad).tolist(),(hi+pad).tolist()]))
 fig.suptitle('Two Harbourfront: remaining unsupported original details in unchanged source context\nRed = every detail facet; pale grey = original neighbouring source facets. No terrain, support or acceptance invented.');fig.tight_layout();DOC.mkdir(parents=True,exist_ok=True);out=DOC/'original-remaining-details-1800x1080.png';fig.savefig(out,dpi=120);plt.close(fig)
 save(DOC/'render.json',dict(sourceSHA256=digest(raw),completeOriginalWorldSHA256=digest(tri.tobytes()),details=records,width=1800,height=1080,outputPath=str(out.relative_to(ROOT)),outputSHA256=digest(out.read_bytes()),qualification='Orthographic cropped original-source geometry evidence only; no browser/runtime acceptance or visibility/occlusion certification.',sourceGeometryChanges=0,installationApproved=False))
 print(out,flush=True)
if __name__=='__main__':main()
