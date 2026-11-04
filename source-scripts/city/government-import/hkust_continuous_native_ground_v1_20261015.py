"""Account for every original HKUST face against both authentic terrain sheets."""
from pathlib import Path
import uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations,connect
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hkust-continuous-native-ground-v1-20261015';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-hkust-adjoining-native-terrain-v1-20261015';PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
def main():
 assert not DOC.exists();prior=read(PRIOR/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 pins={r['path']:r['sha256'] for r in prior['evidenceRefs']};gp=PRIOR/'native-ground.json.gz';assert digest(gp.read_bytes())==pins[str(gp.relative_to(ROOT))];allground=np.array(read(gp)['completeOriginalTerrainTriangles']);rp=PACKET/'two-original-scope-interface-output-v1/result.json';assert digest(rp.read_bytes())==pins[str(rp.relative_to(ROOT))];r=read(rp)
 claim=reservations.claim('hkust-continuous-'+str(uuid.uuid4()),['original-ground-diagnostic:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];paths=[Path(__file__),PRIOR/'result.json',gp,rp]+[HERE/n for n in ['original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','exact_terrain_contact_20261009.py']]
 try:
  DOC.mkdir();rows=[]
  for ref in r['arrayRefs']:
   p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];a=read(p);tri=np.array(a['completeOrderedOriginalTriangles']);uid=a['sourceTuple']['uid'];paths.append(p);lo,hi=tri.min((0,1)),tri.max((0,1));mask=(allground[:,:,0].max(1)>=lo[0])&(allground[:,:,0].min(1)<=hi[0])&(allground[:,:,2].max(1)>=lo[2])&(allground[:,:,2].min(1)<=hi[2]);ids=np.flatnonzero(mask);ground=allground[ids];polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;excluded=ids[~valid].tolist();ids=ids[valid];ground=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);contexts=[]
   for i,face in enumerate(tri):
    c=face_ground_context(face,ground,polys,tree) if lengths[i]>0 else degenerate_ground_context(face,ground,polys,tree);c.update(sourceFace=i,normalYRatio=float(normals[i,1]/lengths[i]) if lengths[i]>0 else None);contexts.append(c)
    if i%500==0:assert reservations.heartbeat(lease,ttl=3600)['ok'];print(uid,i,len(tri),flush=True)
   failures=[c['sourceFace'] for c in contexts if c.get('minimum') and c['minimum']['minimumGapM']<-.5];summary={'uid':uid,'sourceSHA256':a['sourceTuple']['sourceSHA256'],'completeSourceFaces':len(tri),'continuousBelowHalfMetreFaces':failures,'upwardBelowHalfMetreFaces':[i for i in failures if contexts[i]['normalYRatio'] is not None and contexts[i]['normalYRatio']>.25],'uncoveredFaces':[c['sourceFace'] for c in contexts if not c['groundProjectionCovered']],'minimumGapM':min(c['minimum']['minimumGapM'] for c in contexts if c.get('minimum')),'nonHeightFieldTerrainFaceIndices':excluded,'installationApproved':False};rows.append(summary);save(DOC/(uid.replace('/','-').replace(':','-')+'.json.gz'),{'summary':summary,'faces':contexts,'regionalOriginalTerrainFaceIndices':ids.tolist(),'qualification':'Continuous floating intersection diagnostic, not runtime/four-world maximum-envelope or installation acceptance.'});print('COMPLETE SOURCE',uid,len(failures),len(summary['uncoveredFaces']),flush=True)
  save(DOC/'summary.json',{'rows':rows});module('hkust_continuous_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-whole-source-continuous-native-terrain-v1',paths,{'uids':r['uids'],'rows':rows,'nextStep':'Interpret exact remaining source/native crossings, then qualify any private terrain wrapper against current whole-source/runtime/neighbours. No tolerance changes or installation credit.'})
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
