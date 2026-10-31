"""Independent interval-coverage verification for exact unchanged Verdant source seams."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-verdant194544-seam-bounds-v1-20261018';ASSEMBLY=BASE/'government-xl-verdant194544-compound-faces-v1-20261018';BATCH='government-xl-verdant194544-seam-review-v1-20261018';DOC=BASE/BATCH;UID='landsd/194544:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[]
 ground=np.asarray(read(BASE/'government-xl-wave-verdant-multicore-ground-capture-v4-20261017/after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3)
 world=read(BASE/'government-xl-verdant194544-four-world-v1-20261018/world-triangles.json.gz')
 source=read(BASE/'government-xl-wave-verdant-194544-original-recovery-v1-20261017/selection.json.gz')['rows'][0]
 final=module('verdant_neighbour_ground_review',HERE/'xl-final-script-pass.py')
 for mode in ['original','literal','left','balanced']:
  data=read(PRIOR/(mode+'-194544:0.json.gz'));support=np.asarray(read(ASSEMBLY/mode/'input.json.gz')['podium']);assert data['allFlaggedEdgesCertified']and len(data['edges'])==5
  from shapely.geometry import Polygon
  from shapely.ops import unary_union
  t=np.asarray(world[mode][UID]);building=source['source']['building'];ground_f=final.foundation_context(t,ground,Polygon(building['rings'][0],building['rings'][1:]));assert ground_f['completeTerrainTriangles']==ground_f['triangles']==42 and ground_f['fullyBuriedTriangles']==0
  raw=read(ASSEMBLY/mode/'foundation.json');assert raw['fullyBuriedTriangles']==1 and raw['fullyBuriedUpwardTriangles']==0
  faces=read(ASSEMBLY/mode/'finite-surface-context.json.gz')['faces'];assert len(faces)==1
  for face in faces:
   assert face['wholeFaceWithinPointOneM']and not face['failed'];original=np.asarray(face['vertices']);assert np.array_equal(original,t[face['sourceFace']]);normal=np.cross(original[1]-original[0],original[2]-original[0]);normal=normal/np.linalg.norm(normal);assert abs(normal[1])<.1
   axes=[i for i in range(3)if i!=np.argmax(np.abs(normal))];target=Polygon(original[:,axes]);pieces=[]
   for leaf in face['leaves']:
    tri=np.asarray(leaf['triangle']);assert np.max(np.abs((tri-original[0])@normal))<1e-8;mid=tri.mean(0);distance=np.linalg.norm(closest(mid,support[leaf['supportFace']])-mid);bound=float(distance+np.linalg.norm(tri-mid,axis=1).max());assert abs(bound-leaf['upperBoundM'])<1e-9 and bound<=.1;pieces.append(Polygon(tri[:,axes]))
   union=unary_union(pieces);assert target.symmetric_difference(union).area<1e-8 and abs(sum(x.area for x in pieces)-union.area)<1e-8
  strict=read(ASSEMBLY/mode/'support.json.gz')['rows'][0]['proof'];f=dict(strictContacts=strict['strictContacts'],unresolved=len(strict['unresolved']))
  intervals=0;maximum=0.;edges=[]
  for e in data['edges']:
   assert e['certifiedWithinPointOneM']and not e['failed'];a,b=np.asarray(e['edge']);d=b-a;assert d@d>0;coverage=[];edges.append((a,b))
   for leaf in e['leaves']:
    x,y=np.asarray(leaf['a']),np.asarray(leaf['b']);mid=(x+y)/2;distance=np.linalg.norm(closest(mid,support[leaf['supportFace']])-mid);bound=float(distance+np.linalg.norm(y-x)/2);assert abs(bound-leaf['upperBoundM'])<1e-9 and bound<=.1
    u,v=sorted([float((x-a)@d/(d@d)),float((y-a)@d/(d@d))]);assert -.000000001<=u<=v<=1.000000001 and np.linalg.norm(x-(a+((x-a)@d/(d@d))*d))<1e-8 and np.linalg.norm(y-(a+((y-a)@d/(d@d))*d))<1e-8;coverage.append((u,v));maximum=max(maximum,bound);intervals+=1
   end=0.
   for u,v in sorted(coverage):assert u<=end+1e-9;end=max(end,v)
   assert end>=1-1e-9
  for point in data['unresolvedPoints']:
   p=np.asarray(point['position']);distance=np.linalg.norm(closest(p,support[point['supportFace']])-p);assert distance<=.1 and abs(distance-point['distanceM'])<1e-9
   assert min(np.linalg.norm(p-(a+np.clip((p-a)@(b-a)/((b-a)@(b-a)),0,1)*(b-a)))for a,b in edges)<.001
  rows.append(dict(mode=mode,completeFlaggedEdgesVerified=5,certifiedIntervals=intervals,maximumCertifiedDistanceM=maximum,maximumSampleDistanceM=max(p['distanceM']for p in data['unresolvedPoints']),strictContacts=f['strictContacts'],rawUnresolved=f['unresolved']))

 review=dict(uid=UID,sourceSHA256=source['sourceSHA256'],sourceSpecificSeamInterpretationAccepted=True,fullAcceptance=False,installationApproved=False,currentMapAcceptance=False,rawStrictWarningsPreserved=True,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reason='The complete42-face original is not buried by actual terrain. The sole compound highest-surface flag is an original near-vertical wall; its complete face is independently covered by verified finite-surface distance certificates within0.1m, with no area gaps or overlaps in the certificate. All5flagged low-rim edges are similarly covered in all4coordinate modes; actual residual samples are within0.036m. Thus the multi-metre vertical-ray warning describes an adjoining original surface, not a wall buried metres into ground. Raw compound flags remain preserved; no generic acceptance threshold or geometry is changed.',remaining=['Current source identity, full affected-neighbour checks and current-map rebind','Complete staged/live browser and failed-download dependency checks','Guarded installation and installed ledger recording'])
 save(DOC/'ROOT-SEAM-REVIEW.json',review);out=module('verdant_seam_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verdant-neighbour-exact-original-wall-and-rim-seam-review-v1',[Path(__file__),PRIOR/'result.json',HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/p for p in pins]],dict(uids=[UID],sourceSpecificSeamInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True);print(rows,flush=True)
if __name__=='__main__':main()
