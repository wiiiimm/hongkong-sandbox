"""DRAFT saved-witness classification and three focused unchanged-source views."""
from pathlib import Path
import json,numpy as np
from run import ROOT,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from polyu_sports305582_saved_contact_classification_helper_v1_20261012 import classify
BASE=ROOT/'docs/astra-city/government-import';S=ROOT/'source-scripts/city/government-import'
PREV=BASE/'government-xl-polyu-sports305582-current-surviving-neighbour-finite-region-context-v2-20261012'
CAP=BASE/'government-xl-polyu-sports305582-current-surviving-neighbour-geometry-context-v1-20261012'
CTX=BASE/'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012/context.json'
DOC=BASE/'government-xl-polyu-sports305582-saved-contact-locus-context-v1-20261012'
PROPOSAL=BASE/'government-xl-polyu-sports305582-saved-contact-locus-proposal-v1-20261012'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();result=read(PREV/'result.json');assert result['jobId']=='ab6777e2a68b46a3727ebfac7912e95d8106ad878c5b251fbcb9042c2c690e49'and ref(PREV/'result.json')['sha256']=='7d9ac2cde5f49f57f4dc1e4a99f9f4233353f167798182f1f791362464f51d14'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 pins=read(PROPOSAL/'input-pins.json')['refs']+result['evidenceRefs']
 def fence():
  for e in pins:assert ref(ROOT/e['path'])==e
 fence();d=read(PREV/'diagnostic.json.gz');ctx=read(CTX);source=decode_original_world_triangles((ROOT/ctx['source']['path']).read_bytes());assert source.shape==(10536,3,3)and digest(source.astype('<f8').tobytes())==ctx['completeOriginalWorldSHA256'];actual=read(CAP/'actual-surviving-neighbour-attributes.json.gz');n=actual['nativeContextRows'][0];idx=np.asarray(n['completeOriginalIndex']).reshape(-1,3);actors={('landsd/305793:0',mode):np.asarray(n[key],float).reshape(-1,3)[idx]for mode,key in [('nativeLiteral','completeLiteralWorldPosition'),('nativeLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('nativeBalancedF32','completeExplicitBalancedFloat32WorldPosition')]};i=read(CAP/'current-neighbour-input.json.gz');actors[('landsd/305793:0','nativeProviderOriginal')]=decode_original_world_triangles((ROOT/i['rows'][0]['path']).read_bytes())
 for x in actual['basicContextRows']:actors[(x['uid'],'actualProductionBasicF32')]=np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)]
 out={};summaries=[]
 for b in d['bindings']:
  w=actors[(b['actualSurvivingActor'],b['arithmetic'])];assert digest(w.astype('<f8').tobytes())==b['wholeActorWorldSHA256'];key=b['proofKey']
  if key not in out:
   out[key]=[dict(savedContact=c,classification=classify(c,source[c['sourceFaceA']],w[c['sourceFaceB']]))for c in d['distinctExactProofs'][key]['contacts']]
  rows=out[key];summaries.append(dict(**b,completeSavedContactPairs=len(rows),properBothRelativeInteriorSegments=sum(x['classification']['noncoplanarBothRelativeInteriorSegment']for x in rows),exactWholeTriangleDuplicates=sum(x['classification']['exactEqualWholeFiniteTriangleVertexSets']for x in rows),coplanarPatchPairs=sum(x['classification']['exactCoplanar']and x['savedContact']['dimension']==2 for x in rows)))
 DOC.mkdir();images=[]
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 # Complete actor surfaces submitted, bounded display axes only; no clipped or altered geometry.
 for uid,mode in [('landsd/305793:0','nativeLiteral'),('landsd/72322:0','actualProductionBasicF32'),('landsd/258852:0','actualProductionBasicF32')]:
  binding=next(b for b in d['bindings']if b['namedHistoricalRegion']==uid and b['arithmetic']==mode);w=actors[(uid,mode)];rows=out[binding['proofKey']]
  from fractions import Fraction
  points=np.asarray([[float(Fraction(v))for v in p]for x in rows for p in x['savedContact']['exactPoints']]);assert points.size;lo=points.min(0)-1;hi=points.max(0)+1;fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(source[:,:,[0,2,1]],facecolors='#be762f',edgecolors='none',alpha=.24));ax.add_collection3d(Poly3DCollection(w[:,:,[0,2,1]],facecolors='#477fba',edgecolors='none',alpha=.24));ax.scatter(points[:,0],points[:,2],points[:,1],s=3,c='red');ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(25,120);ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('World Y');ax.set_title('Original Sports10536 orange + complete actual '+uid+' blue; saved contact points red\nDisplay crop/transparent/possible occlusion; no source fit, current SportsGPU or support proof');f=DOC/(uid.split('/')[1].replace(':','-')+'-saved-contact-context-1800x1500.png');fig.savefig(f,dpi=150);plt.close(fig)
  with Image.open(f)as image:assert image.size==(1800,1500)
  images.append(dict(**ref(f),dimensions=[1800,1500],sourceTrianglesSubmitted=10536,actorTrianglesSubmitted=len(w),transparentOverlaidDisplayOnly=True))
 fence();save(DOC/'classification.json.gz',dict(sourceOnly=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,noContactKernelRecomputed=True,all10Bindings=summaries,all8DistinctSavedWitnessClassifications=out,completeSourceFaces=10536,originalBodies=21,originalZeros=4,sourceOwnCurrentFourWorldNotProved=True,rawOriginalHeldReasons=result['rawHistoricalOriginalHeldReasons'],renderedImages=images,evidenceRefs=pins,actualBuildingUseContext='Official campus maps distinguish BlockX sports centre, Library campus complex, Innovation Tower and Communal Building. Named use does not grant ownership/attachment/intended joint/solid support/collision exemption.',qualification='Saved finite witness midpoint classification and whole finite triangle/patch containment only. Proper surface crossing is not solid penetration or invalid architecture. Coplanar shared patch is not whole duplicate unless exact vertex sets match. Display axes crop only; full original source/current actor surfaces submitted without geometry edits.'))
 print(json.dumps(summaries),flush=True)
if __name__=='__main__':main()
