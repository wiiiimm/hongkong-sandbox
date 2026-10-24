"""Routine unchanged underside/shared-edge/actual-ground context. No role credit."""
from pathlib import Path
import numpy as np
from run import ROOT,read,save,digest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
B=ROOT/'docs/astra-city/government-import'
SOURCE=B/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011/complete-four-stream-ground-inputs.json.gz'
GRADE=B/'government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011/diagnostic.json.gz'
FINITE=B/'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011/diagnostic.json.gz'
GROUND=ROOT/'source-scripts/city/government-import/local/government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011/runtime-geometry.json.gz'
OUT=B/'government-xl-evangel-college-91306-two-sloping-undersides-context-v1-20261011'
def edges(face):
 p=[tuple(v)for v in face];return {tuple(sorted((a,b)))for a,b in zip(p,p[1:]+p[:1])if a!=b}
def main():
 assert not OUT.exists()
 data=read(SOURCE);w=np.asarray(data['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');ground=np.asarray(read(GROUND)['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 grade=read(GRADE);r=next(r for r in grade['rows']if r['arithmetic']=='providerOriginal');finite=read(FINITE);fr=next(r for r in finite['rows']if r['arithmetic']=='providerOriginal')
 assert digest(w.tobytes())==r['completeWorldSHA256']==fr['completeWholeWorldSHA256'];assert digest(ground.tobytes())==grade['completeActualCandidateGroundSHA256']
 ids=[3854,3855];t=w[ids];lo=t.min((0,1));hi=t.max((0,1));near=np.flatnonzero(np.all(w.max(1)>=lo-[.5,.5,.5],axis=1)&np.all(w.min(1)<=hi+[.5,.5,.5],axis=1)).tolist();gs=np.flatnonzero(np.all(ground[:,:,[0,2]].max(1)>=lo[[0,2]]-.5,axis=1)&np.all(ground[:,:,[0,2]].min(1)<=hi[[0,2]]+.5,axis=1)).tolist()
 adj=[]
 for i in ids:
  for j in range(len(w)):
   shared=edges(w[i])&edges(w[j])
   if j!=i and shared:adj.append(dict(sourceFace=i,counterpartFace=j,completeOriginalSharedNonzeroEdges=[[list(a),list(b)]for a,b in sorted(shared)],counterpartFiniteVerbatim=fr['complete13960FaceComparisons'][j]))
 fig=plt.figure(figsize=(12,9),dpi=200)
 for panel,(azim,elev)in enumerate([(-65,22),(20,10)]):
  ax=fig.add_subplot(1,2,panel+1,projection='3d');ax.add_collection3d(Poly3DCollection(ground[gs][:,:,[0,2,1]],facecolors='#80985d',edgecolors='#43552b',alpha=.5,linewidths=.2));ax.add_collection3d(Poly3DCollection(w[near][:,:,[0,2,1]],facecolors='#a8bcc4',edgecolors='#50707c',alpha=.17,linewidths=.3));ax.add_collection3d(Poly3DCollection(w[[3846]][:,:,[0,2,1]],facecolors='#418c9b',edgecolors='#125164',alpha=.75));ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=['#e58931','#de523e'],edgecolors='#8d300a',alpha=.88,linewidths=1))
  for i in ids+[3846]:
   p=w[i].mean(0);ax.text(p[0],p[2],p[1],str(i),fontsize=10)
  ax.set_xlim(lo[0]-.5,hi[0]+.5);ax.set_ylim(lo[2]-.5,hi[2]+.5);ax.set_zlim(4.5,9);ax.set_box_aspect((hi[0]-lo[0]+1,hi[2]-lo[2]+1,4.5));ax.view_init(elev,azim);ax.set_xlabel('X / m');ax.set_ylabel('Z / m');ax.set_zlabel('HKPD / m')
 fig.suptitle('Evangel3854/3855: complete original sloping undersides and exact original neighbours\nOrange/red original underside; blue strictly clear original3846; green actual candidate ground. No steep-wall or role credit.',fontsize=11);fig.tight_layout(rect=[0,0,1,.92]);OUT.mkdir();image=OUT/'complete-two-sloping-undersides-original-counterparts-current-ground-2400x1800.png';fig.savefig(image);plt.close(fig)
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(OUT/'context.json.gz',dict(uid=data['uid'],sourceSHA256=data['sourceSHA256'],completeWorldSHA256=digest(w.tobytes()),completeGroundSHA256=digest(ground.tobytes()),completeSourceFaceIds=ids,completeOriginalGeometry=t.tolist(),completeNearbySourceIds=near,completeNearbySourceGeometry=w[near].tolist(),completeNearbyCurrentGroundIds=gs,completeNearbyCurrentGroundGeometry=ground[gs].tolist(),completeOriginalSharedEdgeCounterparts=adj,completeRawFiniteRecords=[fr['complete13960FaceComparisons'][i]for i in ids],completeGenuineActualGradeContacts=[c for c in r['complete5297CurrentGradeContactInventory']['contacts']if c['sourceFaceA']in ids],allFourRaw132FailuresRetained=True,steepWallCredit=False,currentAcceptance=False,sourceGeometryChanges=0,evidenceRefs=[ref(p)for p in [SOURCE,GRADE,FINITE,GROUND,Path(__file__),image]]));print(OUT)
if __name__=='__main__':main()
