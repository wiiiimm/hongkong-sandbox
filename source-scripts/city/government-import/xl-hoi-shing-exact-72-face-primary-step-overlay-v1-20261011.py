"""Independent primary step association; true upward burial remains unresolved."""
from pathlib import Path
import importlib.util
import numpy as np,shapely
from shapely.geometry import shape,mapping
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-hoi-shing-exact-72-face-primary-step-association-v1-20261011';DOC=BASE/BATCH
PART=BASE/'xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1'
PRIMARY=BASE/'government-xl-hoi-shing-exact-72-face-primary-context-v1-20261011'
VECTOR=BASE/'government-xl-hoi-shing-exact-72-face-primary-vectors-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def lines(g):
 if g.geom_type=='LineString':return [g]
 if hasattr(g,'geoms'):return [x for a in g.geoms for x in lines(a)]
 return []
def main():
 assert not DOC.exists();DOC.mkdir(parents=True)
 part=read(PART/'diagnostic.json.gz');tri=np.asarray(part['complete72OriginalTriangles'],dtype='<f8');assert len(tri)==72
 ids=part['complete72FacePartIds'];failed=part['completeNineRealFailingUpwardFaces'];assert len(failed)==9 and set(failed)<=set(ids)
 projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
 vector=read(VECTOR/'decoded-original-feature-geometries.json.gz');assert vector['exactSourcePartContext']==ref(PART/'diagnostic.json.gz')
 style=read(VECTOR/'original-provider-stair-style-contract.json')['layers'];stepstyles=[s for s in style if s.get('source-layer')=='8_CartoPedLine_1K' and s.get('filter')==['==','_symbol',8]];assert stepstyles and all('/STP E' in s['id']for s in stepstyles)
 contexts=[]
 for fi,r in enumerate(vector['rows']):
  if r['layer']!='8_CartoPedLine_1K' or r['properties'].get('_symbol')not in [5,8]:continue
  for pi,g in enumerate(lines(shape(r['geometry']))):
   if g.distance(projection)>2:continue
   contexts.append(dict(vectorFeatureIndex=fi,partIndex=pi,properties=r['properties'],completeOriginalLineGeometry=mapping(g),quantizationStepM=r['quantizationStepM'],distanceToFull72FaceProjectionM=float(g.distance(projection)),lengthInsideOriginalProjectionM=float(g.intersection(projection).length)))
 steps=[r for r in contexts if r['properties']['_symbol']==8];paths=[r for r in contexts if r['properties']['_symbol']==5];assert steps
 fig,axs=plt.subplots(1,2,figsize=(12,6));lo,hi=np.asarray(part['completePartBounds']);orange=[ids.index(i)for i in failed]
 for j,ax in enumerate(axs):
  ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors='#b4bcc7',edgecolors='#506178',linewidths=.3,alpha=.6))
  ax.add_collection(PolyCollection(tri[orange][:,:,[0,2]],facecolors='#ed8936',edgecolors='#97441a',linewidths=.7,alpha=.85))
  for records,color in [(paths,'#7a378b'),(steps,'#1665b6')]:
   for r in records:
    g=shape(r['completeOriginalLineGeometry']);x,z=g.xy;ax.plot(x,z,color=color,lw=1.4)
  pad=20 if j==0 else 2;ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(hi[2]+pad,lo[2]-pad),xlabel='Viewer X = HK80 E − 834500 (m)',ylabel='Viewer Z = 816500 − HK80 N (m)');ax.set_aspect('equal');ax.grid(alpha=.2)
  ax.set_title('Complete72 unchanged original faces; orange9 true upward failures\nIndependent mapped steps blue / pedestrian paths purple')
 fig.tight_layout();fig.savefig(DOC/'complete-original-72-faces-independent-primary-steps-2400x1200.png',dpi=200);plt.close(fig)
 save(DOC/'diagnostic.json.gz',dict(uids=part['uids'],sourceSHA256=part['sourceSHA256'],completeOriginalWorldSHA256=part['completeOriginalWorldSHA256'],completeOriginalPartFaceIds=ids,completeOriginalPartTriangles=tri.tolist(),allNineUpwardFailureFaceIds=failed,allNineUpwardBurialFailuresPreserved=True,primaryStepStyleContract=stepstyles,completeLocalOriginalPrimaryLines=contexts,stepLengthInsideProjectionM=sum(r['lengthInsideOriginalProjectionM']for r in steps),pathLengthInsideProjectionM=sum(r['lengthInsideOriginalProjectionM']for r in paths),independentWorldOrigin=vector['worldOrigin'],primaryContext=ref(PRIMARY/'diagnostic.json'),primaryVectorContext=ref(VECTOR/'decoded-original-feature-geometries.json.gz'),sourceOnly=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainProposalCreated=False,belowGradeRoleEstablished=False,qualification='Positive independent mapped-step association at the complete original appendage location. 2m limits diagnostic context nomination only; it is NOT geometry fit/acceptance/support tolerance. Original full line records/raw tile and both full72face and9failure inventories retained. Map quantization is cartographic, not surveyed height. Nine genuinely buried upward facets remain unresolved; generic footbridge, ramps or same-estate primary records confer no below-grade or physical credit.'))
 paths=[Path(__file__),HERE/'xl-hoi-shing-exact-72-face-primary-context-v1-20261011.py',HERE/'xl-hoi-shing-exact-72-face-primary-vectors-v1-20261011.py',PART/'result.json',PART/'diagnostic.json.gz',PART/'original-72-face-upward-part-with-authentic-tin-1800x900.png']
 paths +=[p for folder in [PRIMARY,VECTOR,DOC]for p in folder.rglob('*')if p.is_file()]
 spec=importlib.util.spec_from_file_location('hoi_shing_primary_source_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 receipt=m.freeze(BATCH,'exact-original-72-face-appendage-primary-steps-with-nine-true-burial-failures-preserved',paths,dict(uids=part['uids'],sourceSHA256=part['sourceSHA256'],completeOriginalPartFaces=72,trueUpwardBurialFailures=9,identityAccepted=False,physicalAccepted=False,sourceGeometryChanges=0,terrainProposalCreated=False,sourceIdentityInterpretationUsedAI=True,aiGeometryModelling=False))
 print(dict(jobId=receipt['jobId'],localStepSegments=len(steps),stepLengthInsideProjectionM=sum(r['lengthInsideOriginalProjectionM']for r in steps),physicalAccepted=False),flush=True)
if __name__=='__main__':main()
