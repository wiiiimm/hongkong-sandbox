"""Existing support and continuous ground checks on unchanged Esplanade sources."""
from pathlib import Path
import subprocess,uuid,json
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BATCH='government-xl-esplanade-original-support-ground-v1-20261015'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PREV=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015'
LOCAL=HERE/'local/government-xl-esplanade-pair-current-physical-v3-20261015'
UIDS=['landsd/268828:0','landsd/309385:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=read(PREV/'result.json')
 for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
 selection=read(PREV/'selection.json.gz');rows=selection['rows'];assert sorted(r['uid']for r in rows)==sorted(UIDS)
 claim=reservations.claim('esplanade-support-ground-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];job=None
 try:
  DOC.mkdir();stage='unchanged-original-pair-support-and-continuous-ground';jid=jobs.enqueue(BATCH,stage,dict(uids=UIDS,prior=ref(PREV/'result.json')));job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
  cat=read(LOCAL/'catalogue.json');sources=[]
  for row in rows:
   entry=row['candidate']['entry'];sources.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],source=row['source'],candidate=dict(path=row['candidate']['path'],entry={**entry,'rootTranslation':cat['rootTranslation'],'coordinatePolicy':cat.get('coordinatePolicy'),'datasetId':cat.get('datasetId')})))
  save(DOC/'support-inputs.json',dict(sources=sources,pairs=[dict(uid=UIDS[0],supportUid=UIDS[1])]))
  with (DOC/'support.log').open('w')as log:subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
  support=read(DOC/'support-checks.json.gz');assert len(support['rows'])==1
  refs=[ref(Path(__file__)),ref(PREV/'result.json'),ref(PREV/'selection.json.gz'),ref(LOCAL/'catalogue.json'),ref(LOCAL/'runtime-geometry.json.gz'),ref(DOC/'support-checks.json.gz'),ref(DOC/'support.log')]
  for p,h in support['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(dict(path=p,sha256=h))
  row=next(r for r in rows if r['uid']==UIDS[1]);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw)
  geometry=next(r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']if r['uid']==UIDS[1]);assert geometry['sourceSHA256']==row['sourceSHA256'];ground=np.asarray(geometry['drawnGroundGeometry'],float).reshape(-1,3,3)
  polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;excluded=np.flatnonzero(~valid).tolist();ids=np.flatnonzero(valid);ground=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);contexts=[]
  for i,face in enumerate(tri):
   c=face_ground_context(face,ground,polys,tree)if length[i]>0 else degenerate_ground_context(face,ground,polys,tree);c.update(sourceFace=i,normalYRatio=float(normals[i,1]/length[i])if length[i]>0 else None);contexts.append(c)
   if i%200==0:assert reservations.heartbeat(lease)['ok'];print('podium',i,len(tri),flush=True)
  failed=[c['sourceFace']for c in contexts if c.get('minimum')and c['minimum']['minimumGapM']<-.5];uncovered=[c['sourceFace']for c in contexts if not c['groundProjectionCovered']]
  summary=dict(uid=UIDS[1],sourceSHA256=row['sourceSHA256'],sourceFaces=len(tri),belowHalfMetreFaces=failed,upwardBelowHalfMetreFaces=[i for i in failed if contexts[i]['normalYRatio']is not None and contexts[i]['normalYRatio']>.25],uncoveredFaces=uncovered,minimumGapM=min(c['minimum']['minimumGapM']for c in contexts if c.get('minimum')),excludedNonHeightFieldTerrainFaces=excluded)
  save(DOC/'podium-ground.json.gz',dict(summary=summary,faces=contexts,terrainFaceIndices=ids.tolist(),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),groundWorldSHA256=digest(ground.astype('<f8').tobytes()),qualification='Continuous minima with floating intersection arithmetic; no independent maximum-envelope certificate or acceptance. Excluded non-height-field terrain faces retained by index.'))
  refs.append(ref(DOC/'podium-ground.json.gz'));refs.extend(ref(HERE/p)for p in ['original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','exact_terrain_contact_20261009.py'])
  for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
  for r in refs:assert ref(ROOT/r['path'])==r
  interface=support['rows'][0]['interface'];result=dict(jobId=jid,uids=UIDS,sourceOnly=True,newlyInstalled=0,installationApproved=False,publication=False,geometryChanges=0,interface=interface,podiumGround=summary,evidenceRefs=refs)
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(json.dumps(dict(jobId=jid,interfacePassed=interface['passed'],strictContacts=interface['strictContacts'],samples=interface['samples'],podiumFailedFaces=len(failed),podiumUncoveredFaces=len(uncovered))),flush=True)
 except Exception as e:
  if job:jobs.finish(job,error=str(e))
  raise
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
