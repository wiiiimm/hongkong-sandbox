"""Exact original disconnected surfaces, proportional source-only diagnostic.

All 696 disconnected upper faces shown; no new surface/attachment is drawn.
One overview includes the whole untouched original; isolated panels are labelled.
Source geometry and every raw contact/root failure remain untouched.
"""
import importlib.util
from pathlib import Path
import collections,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-disconnected-original-context-v1';DOC=BASE/BATCH;GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';PRIOR=BASE/'xl-terrain-recovery-20261011-langham-upper-current-native-original-interfaces-v2';UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(GRAPH/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 g=read(GRAPH/'diagnostic.json.gz');prior=read(PRIOR/'diagnostic.json.gz');asset=next(ROOT/r['path']for r in prior['evidenceRefs']if r['sha256']==prior['completeSourceSHA256'][UID]);assert digest(asset.read_bytes())==prior['completeSourceSHA256'][UID];t=decode_original_world_triangles(asset.read_bytes());assert digest(t.tobytes())==prior['completeOriginalWorldSHA256'][UID]
 cs=g['components'];adj=collections.defaultdict(set)
 for p in g['oneExactPositiveWitnessPerContactingBodyPair']:a,b=p['components'];adj[a].add(b);adj[b].add(a)
 reached={i for i,c in enumerate(cs)if c['actorUID']!=UID};todo=list(reached)
 while todo:
  a=todo.pop()
  for b in adj[a]-reached:reached.add(b);todo.append(b)
 missing=[i for i,c in enumerate(cs)if c['actorUID']==UID and i not in reached];ids=sorted(f for i in missing for f in cs[i]['globalOriginalFaces']);assert len(ids)==696 and len(missing)==95
 groups=[[10,20,21,29],[91],[95],[i for i in missing if i not in [10,20,21,29,91,95]]];assert sorted(i for group in groups for i in group)==missing
 sets=[ids,*[sorted(f for i in group for f in cs[i]['globalOriginalFaces'])for group in groups],ids];titles=['Whole original; disconnected surfaces in orange','Four separate 139-face surfaces; isolated','12-face original rooftop part; isolated','10-face original small part; isolated','Other disconnected original surfaces; isolated','All 696 disconnected original faces; isolated']
 fig=plt.figure(figsize=(18,12),dpi=100)
 for k,(faces,title)in enumerate(zip(sets,titles),1):
  shown=t if k==1 else t[faces];center=(shown.min(axis=(0,1))+shown.max(axis=(0,1)))/2;u=(t[faces]-center)[:,:,[0,2,1]];s=(shown-center)[:,:,[0,2,1]];lo=s.min(axis=(0,1));hi=s.max(axis=(0,1));pad=max(float((hi-lo).max())*.035,.02);lo-=pad;hi+=pad
  ax=fig.add_subplot(2,3,k,projection='3d')
  if k==1:ax.add_collection3d(Poly3DCollection(s,facecolors='#bbc3ca',linewidths=0,alpha=.32))
  ax.add_collection3d(Poly3DCollection(u,facecolors='#df9854',edgecolors='#50351d',linewidths=.25,alpha=1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(24,-55 if k!=6 else 130);ax.set_title(title,fontsize=9);ax.set_xlabel('Original X (m)');ax.set_ylabel('Original Z (m)');ax.set_zlabel('Original Y (m)')
 fig.tight_layout();DOC.mkdir(parents=True);png=DOC/'original-disconnected-context-1800x1200.png';fig.savefig(png);plt.close(fig)
 refs=[ref(p)for p in [Path(__file__),asset,png,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PRIOR/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py']];result=dict(uids=[UID],sourceSHA256=prior['completeSourceSHA256'][UID],completeOriginalWorldSHA256=digest(t.tobytes()),completeDisconnectedBodyIds=missing,completeDisconnectedOriginalFaceIds=ids,isolatedGroupBodyIds=groups,originalMetricAxisScale=True,sourceOnly=True,noFreshCurrentCapture=True,roleInterpretation=False,rootOrContactCredit=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
 spec=importlib.util.spec_from_file_location('langham_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-original-langham-disconnected-surfaces-equal-metric-source-visual-context-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,roleInterpretation=False,newlyInstalled=0))
if __name__=='__main__':main()
