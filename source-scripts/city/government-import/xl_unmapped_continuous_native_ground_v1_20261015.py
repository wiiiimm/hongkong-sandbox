"""Existing full-face continuous minima against authentic government terrain."""
import importlib.util,uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BATCH='government-xl-unmapped-continuous-native-ground-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows'];models=['B360171738601063C0','B365201779201063C0'];sources=[next(r for r in recovery if r['modelId']==m)for m in models];resources=['native-model:'+r['sourceKey']for r in sources]
 claim=reservations.claim('unmapped-continuous-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();stage='whole-original-continuous-native-ground-v1';jid=jobs.enqueue(BATCH,stage,{'sourceKeys':[r['sourceKey']for r in sources]});job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
  spec=importlib.util.spec_from_file_location('unmapped_continuous_decode',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
  refs=[ref(Path(__file__))]+[ref(HERE/n)for n in ['original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','exact_terrain_contact_20261009.py']];summaries=[]
  for source in sources:
   model=source['modelId'];p=BASE/('government-xl-station-adjoining-terrain-v1-20261015/diagnostic.json'if model==models[0]else'government-xl-unmapped-native-terrain-v1-20261015/'+model+'.json');data=read(p);refs.append(ref(p));paths=[ROOT/x for x in data['terrainPaths']];allground=np.concatenate([f.s.terrain_triangles(p)for p in paths]);asset=ROOT/source['asset']['path'];assert ref(asset)==source['asset'];refs.append(ref(asset));tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));regional=(allground[:,:,0].max(axis=1)>=lo[0])&(allground[:,:,0].min(axis=1)<=hi[0])&(allground[:,:,2].max(axis=1)>=lo[2])&(allground[:,:,2].min(axis=1)<=hi[2]);ids=np.flatnonzero(regional);ground=allground[ids];polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;excluded=ids[~valid].tolist();ids=ids[valid];ground=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);contexts=[]
   for i,face in enumerate(tri):
    c=face_ground_context(face,ground,polys,tree)if length[i]>0 else degenerate_ground_context(face,ground,polys,tree);c.update(sourceFace=i,normalYRatio=float(normal[i,1]/length[i])if length[i]>0 else None);contexts.append(c)
    if i%500==0:assert reservations.heartbeat(lease)['ok'];print(model,i,len(tri),flush=True)
   failures=[c['sourceFace']for c in contexts if c.get('minimum')and c['minimum']['minimumGapM']<-.5];uncovered=[c['sourceFace']for c in contexts if not c['groundProjectionCovered']];summary={'modelId':model,'sourceKey':source['sourceKey'],'sourceSHA256':source['sourceSHA256'],'completeSourceFaces':len(tri),'continuousBelowHalfMetreFaces':failures,'upwardBelowHalfMetreFaces':[i for i in failures if contexts[i]['normalYRatio']is not None and contexts[i]['normalYRatio']>.25],'uncoveredFaces':uncovered,'minimumGapM':min(c['minimum']['minimumGapM']for c in contexts if c.get('minimum')),'nonHeightFieldRegionalTerrainFaces':excluded,'installationApproved':False}
   out=DOC/(model+'.json.gz');save(out,{'summary':summary,'faces':contexts,'terrainPaths':data['terrainPaths'],'regionalOriginalTerrainFaceIndices':ids.tolist(),'sourceWorldSHA256':digest(np.asarray(tri,dtype='<f8').tobytes()),'groundWorldSHA256':digest(np.asarray(ground,dtype='<f8').tobytes()),'qualification':'Continuous minima with floating intersection arithmetic; no maximum-envelope certificate, runtime-terrain replacement or acceptance. Non-height-field terrain facets retained by index as separate context.'});refs.append(ref(out));summaries.append(summary)
   for p in paths:
    refs.append(ref(p))
    for buffer in read(p).get('buffers',[]):
     if buffer.get('uri')and not buffer['uri'].startswith('data:'):refs.append(ref(p.parent/buffer['uri']))
   print('MODEL COMPLETE',model,len(failures),len(uncovered),flush=True)
  for q in refs:assert ref(ROOT/q['path'])==q
  result={'jobId':jid,'rows':summaries,'evidenceRefs':refs,'newlyInstalled':0,'sourceGeometryChanges':0,'publicationApproved':False}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print('COMPLETE',jid,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
