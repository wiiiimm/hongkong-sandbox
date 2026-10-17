"""Routine source views: all85 proper original contact records; no acceptance."""
from fractions import Fraction as F
from pathlib import Path
import collections,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-heya-aqua-complete85-coupled-source-join-context-v1-20261011'
ACTUAL=BASE/'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011'
NATIVE=BASE/'government-xl-heya-aqua-complete-current6648-native-exclusions-v1-20261011'
T,P='landsd/184286:0','landsd/184285:0'
def main():
 assert not DOC.exists();data=read(ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];native=read(NATIVE/'diagnostic.json.gz');rows=[]
 for item in native['completeCoupledOriginalPrimitiveContext']:
  mode=item['arithmetic'];worlds={u:np.asarray(data[u]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8')for u in [T,P]}
  records=item['completeTowerPodiumPrimitiveClassifications'];assert len(records)==85and len(item['properTriangleInteriorCrossings'])==85
  points=[tuple(F(x)for x in p)for r in records for p in r['contact']['exactPoints']]
  ids={T:sorted({r['contact']['sourceFaceA']for r in records}),P:sorted({r['contact']['sourceFaceB']for r in records})}
  rows.append(dict(arithmetic=mode,completeContacts=85,exactContactBounds=[[str(min(p[k]for p in points))for k in range(3)],[str(max(p[k]for p in points))for k in range(3)]],
   completeAffectedSourceFaceIds=ids,completeAffectedWholeFacetBounds={u:[worlds[u][ids[u]].min((0,1)).tolist(),worlds[u][ids[u]].max((0,1)).tolist()]for u in [T,P]},
   completeCrossComponentCounts=dict(collections.Counter(str((r['contact']['towerComponent'],r['contact']['podiumComponent']))for r in records)),
   noBoundaryOnlyContactOrEngineeringConclusion=True))
 worlds={u:np.asarray(data[u]['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8')for u in [T,P]};records=native['completeCoupledOriginalPrimitiveContext'][0]['completeTowerPodiumPrimitiveClassifications']
 points=np.asarray([[float(F(x))for x in p]for r in records for p in r['contact']['exactPoints']]);ids={T:rows[0]['completeAffectedSourceFaceIds'][T],P:rows[0]['completeAffectedSourceFaceIds'][P]}
 fig,axes=plt.subplots(2,2,figsize=(16,9),dpi=200)
 for ax,coords,title,zoom in [(axes[0,0],[0,2],'Complete unchanged original pair: plan',False),(axes[0,1],[0,1],'Complete unchanged original pair: elevation',False),(axes[1,0],[0,1],'Observed85 contact layer: X/Y display crop',True),(axes[1,1],[2,1],'Observed85 contact layer: Z/Y display crop',True)]:
  for u,color in [(P,'#839bb1'),(T,'#c5b886')]:
   ax.add_collection(PolyCollection(worlds[u][:,:,coords],facecolors=color,edgecolors=color,linewidths=.1,alpha=.08))
   ax.add_collection(PolyCollection(worlds[u][ids[u]][:,:,coords],facecolors=color,edgecolors=color,linewidths=.3,alpha=.35))
  ax.scatter(points[:,coords[0]],points[:,coords[1]],s=4,c='#be2e30',label='All85 exact proper contacts (float display only)')
  ax.autoscale();ax.set_title(title);ax.set_xlabel(['X','Y','Z'][coords[0]]+' m');ax.set_ylabel(['X','Y','Z'][coords[1]]+' m');ax.grid(alpha=.15)
  if zoom:ax.set_ylim(points[:,1].min()-1,points[:,1].max()+1)
  ax.legend(fontsize=7)
 fig.suptitle('Heya unchanged originals: T184286 / installed P184285. Complete85 relative-interior crossings retained. No acceptance, support or volumetric claim.');fig.tight_layout()
 DOC.mkdir(parents=True);image=DOC/'complete85-original-source-join-context-3200x1800.png';fig.savefig(image);plt.close(fig)
 refs=[Path(__file__),ACTUAL/'result.json',ACTUAL/'complete-two-actor-four-stream-ground-inputs.json.gz',NATIVE/'result.json',NATIVE/'diagnostic.json.gz',image]
 save(DOC/'context.json',dict(uids=[T,P],rows=rows,images=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in refs],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False))
 print(json.dumps(dict(image=str(image.relative_to(ROOT)),rows=rows)))
if __name__=='__main__':main()
