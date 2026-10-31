"""View-only repair; full SAVED-contact facets, no contact/census/classification rerun."""
import json,numpy as np
from pathlib import Path
from fractions import Fraction
from run import ROOT,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';C=B/'government-xl-polyu-sports305582-saved-contact-locus-context-v1-20261012';A=B/'government-xl-polyu-sports305582-current-surviving-neighbour-geometry-context-v1-20261012';X=B/'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012/context.json';D=B/'government-xl-polyu-sports305582-saved-contact-facet-subset-views-v1-20261012'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not D.exists();receipt=read(C/'result.json');assert ref(C/'result.json')['sha256']=='e2914e326ab75fe335fbe30359ef607753324fa086e561d1ac485d038b0d8dfd';assert receipt['jobId']=='44d938828be93d189b7eceddbc399bc4c955fc8375efb317acb05de091b5d3e0'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins=receipt['evidenceRefs']+[ref(C/'result.json'),ref(Path(__file__)),ref(C/'classification.json.gz')]
 def fence():
  for e in pins:assert ref(ROOT/e['path'])==e
 fence();v=read(C/'classification.json.gz');x=read(X);source=decode_original_world_triangles((ROOT/x['source']['path']).read_bytes());assert source.shape==(10536,3,3)and digest(source.astype('<f8').tobytes())==x['completeOriginalWorldSHA256'];a=read(A/'actual-surviving-neighbour-attributes.json.gz');n=a['nativeContextRows'][0];idx=np.asarray(n['completeOriginalIndex']).reshape(-1,3);actors={'landsd/305793:0':np.asarray(n['completeLiteralWorldPosition']).reshape(-1,3)[idx]}
 for q in a['basicContextRows']:actors[q['uid']]=np.asarray(q['position']).reshape(-1,3)[np.asarray(q['index']).reshape(-1,3)]
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 D.mkdir();exports=[]
 for uid,mode in [('landsd/305793:0','nativeLiteral'),('landsd/72322:0','actualProductionBasicF32'),('landsd/258852:0','actualProductionBasicF32')]:
  b=next(b for b in v['all10Bindings']if b['namedHistoricalRegion']==uid and b['arithmetic']==mode);w=actors[uid];assert digest(w.astype('<f8').tobytes())==b['wholeActorWorldSHA256'];rows=v['all8DistinctSavedWitnessClassifications'][b['proofKey']];idsS=sorted({z['savedContact']['sourceFaceA']for z in rows});idsA=sorted({z['savedContact']['sourceFaceB']for z in rows});selectedS,selectedA=source[idsS],w[idsA];assert len(rows)==b['completeSavedContactPairs'];points=np.asarray([[float(Fraction(q))for q in p]for z in rows for p in z['savedContact']['exactPoints']]);allpts=np.concatenate([selectedS.reshape(-1,3),selectedA.reshape(-1,3)]);lo=allpts.min(0)-1;hi=allpts.max(0)+1
  fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(selectedS[:,:,[0,2,1]],facecolors='#c17831',edgecolors='#92581d',linewidths=.25,alpha=.5));ax.add_collection3d(Poly3DCollection(selectedA[:,:,[0,2,1]],facecolors='#4a85bb',edgecolors='#305f85',linewidths=.25,alpha=.4));ax.scatter(points[:,0],points[:,2],points[:,1],s=6,c='red');ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(25,120);ax.set_xlabel('Original world X');ax.set_ylabel('Original world Z');ax.set_zlabel('Original world Y');ax.set_title('All saved-contact WHOLE facets: Sports orange / '+uid+' blue / witnesses red\nSource subset '+str(len(idsS))+'/10536; actor subset '+str(len(idsA))+'/'+str(len(w))+'; no mesh cuts or coordinate fitting');f=D/(uid.split('/')[1].replace(':','-')+'-complete-contact-facet-subset-1800x1500.png');fig.savefig(f,dpi=150);plt.close(fig)
  with Image.open(f)as im:assert im.size==(1800,1500)
  exports.append(dict(**ref(f),dimensions=[1800,1500],originalSourceFaceIDs=idsS,actualActorFaceIDs=idsA,sourceSubsetFaces=len(idsS),sourceWholeFaces=10536,actorSubsetFaces=len(idsA),actorWholeFaces=len(w),allSavedContactPairsIncluded=len(rows),viewBounds=[lo.tolist(),hi.tolist()],wholeSelectedFacetsUncut=True,displayOnlyNotWholeSceneOrGPUVisibility=True))
 fence();save(D/'view-context.json',dict(sourceOnly=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,noContactOrCensusOrClassificationRerun=True,priorOccludedThreeExportsPreserved=True,exactUnwarpedSourceCoordinates=True,wholeSourceContextFaceCount=10536,viewsAreExplicitSavedContactFacetSubsets=True,originalAll21Body4ZeroObligationsPreserved=True,allOriginalHeldReasons=v['rawOriginalHeldReasons'],exports=exports,inputRefs=pins));print(json.dumps(exports),flush=True)
if __name__=='__main__':main()
