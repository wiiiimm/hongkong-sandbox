"""Compare two byte-identical originals; source context only, no acceptance."""
from pathlib import Path
import json,uuid,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from publication_lock import locked_publication
BATCH='government-xl-west-wing26195-neighbour319534-original-context-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAP=DOC.parent/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';CONTEXT=DOC.parent/'government-xl-west-wing26195-current-projection-context-v2-20261015/context.json'
UID='landsd/319534:0';SHA='6f085985d3ea19699c010d73d173d288107c3d3eea372bf5704a854bd2b1e2c1';KEY='828133bbea286a52de1484a5163766bfab7ee42b0b4c07a8be3e756f0cabe7e6'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();claim=reservations.claim('west-wing-neighbour-'+str(uuid.uuid4()),['building:landsd/26195:0','building:'+UID],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];job=None
 try:
  with locked_publication(ROOT):
   with connect()as c:
    c.execute('SET TRANSACTION READ ONLY');record=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,KEY)).fetchone()
   assert record[0]=='9ef4f709c01591edac1bb64be27c347726ea68c401c0fc1f2806dc297994a2b9';native=[x for x in record[1]['models']if x['modelId']=='B351811569301063C0'];assert len(native)==1;native=native[0]
   assert native['asset']['sha256']==SHA and native['triangles']==34
   path=ROOT/'3d-viewer/city/data/official-models/tourist-trial-001'/ (SHA+'.glb.gz');assert ref(path)['sha256']==SHA;tri=decode_original_world_triangles(path.read_bytes());assert tri.shape==(34,3,3)
   manifest=ROOT/'3d-viewer/city/data/manifest.json';tile=ROOT/'3d-viewer/city/data/tiles/0_0.json';current={b['uid']:b for b in read(tile)['buildings']};forms={b['uid']:b for b in read(CAP/'literal-source-inputs.json.gz')['completeCurrentForms']}
   for uid in ['landsd/26195:0',UID]:assert forms[uid]==current[uid]
   assert current[UID]['buildingCSUID']=='3518115693T20110810' and native['matching']['viewerMatches'][0]['uid']==UID
   source=read(CAP/'original-full-source-root-context.json.gz');whole=np.asarray(source['completeOriginalBinary64WorldTriangles']);assert whole.shape==(46918,3,3)
   overlap=next(x for x in read(CONTEXT)['intersections']if x['uid']==UID);ids=overlap['sourceFaceIds'];assert len(ids)==24
   lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));mask=(whole[:,:,0].max(axis=1)>=lo[0]-8)&(whole[:,:,0].min(axis=1)<=hi[0]+8)&(whole[:,:,2].max(axis=1)>=lo[2]-8)&(whole[:,:,2].min(axis=1)<=hi[2]+8);contextids=np.flatnonzero(mask);origin=np.array([lo[0],0,lo[2]])
   fig=plt.figure(figsize=(18,6))
   for i,(el,az)in enumerate([(80,-60),(20,-60),(20,120)]):
    ax=fig.add_subplot(1,3,i+1,projection='3d');xyz=lambda a:(a-origin)[:,:,[0,2,1]]
    ax.add_collection3d(Poly3DCollection(xyz(whole[mask]),facecolors='#afb8bd',edgecolors='#555555',linewidths=.1,alpha=.15))
    ax.add_collection3d(Poly3DCollection(xyz(whole[ids]),facecolors='#e69b24',edgecolors='#725010',linewidths=.5,alpha=.8))
    ax.add_collection3d(Poly3DCollection(xyz(tri),facecolors='#4787ce',edgecolors='#173a64',linewidths=.6,alpha=.65))
    ax.set_xlim(-8,hi[0]-lo[0]+8);ax.set_ylim(-8,hi[2]-lo[2]+8);ax.set_zlim(3,22);ax.set_box_aspect((20,20,19));ax.view_init(elev=el,azim=az);ax.set_zlabel('HKPD m')
   fig.suptitle('Unchanged original West Wing (grey / amber24 overlapping faces) and original319534 (blue34 faces)\nSource identity context only; no physical acceptance');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'two-original-context.png',dpi=140);plt.close(fig)
   save(DOC/'source-context.json',dict(sourceOnly=True,modelGeometryChanges=0,installationApproved=False,newlyInstalled=0,nativeRun=NATIVE_RUN,nativeCacheKey=KEY,nativeResultSHA256=record[0],neighbourNativeRecord=native,neighbourWorldSHA256=digest(np.asarray(tri,dtype='<f8').tobytes()),neighbourCompleteFaces=34,westWingCompleteSourceFaces=46918,westWingOriginalWorldSHA256=source['completeOriginalWorldSHA256'],westWingContextDisplayFaceIds=contextids.tolist(),westWingProjectedOverlapFaceIds=ids,projectionOverlapM2=overlap['sourceIntersectionArea'],currentForms={u:current[u]for u in ['landsd/26195:0',UID]},observedManifestSHA256=ref(manifest)['sha256'],observedTileSHA256=ref(tile)['sha256'],completeNeighbourWorldTriangles=tri.tolist(),physicalChecksPerformed=False,sourceRolesApproved=False))
   refs=[ref(p)for p in [Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',path,CONTEXT,CAP/'original-full-source-root-context.json.gz',CAP/'literal-source-inputs.json.gz',DOC/'source-context.json',DOC/'two-original-context.png']]
   assert reservations.heartbeat(lease)['ok'];kind='west-wing-neighbour-original-source-context-v1';jid=jobs.enqueue(BATCH,kind,dict(uid=UID,sourceSHA256=SHA));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
   result=dict(jobId=jid,batch=BATCH,uids=['landsd/26195:0',UID],sourceOnly=True,newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,completeNeighbourFaces=34,westWingProjectedOverlapFaces=24,evidenceRefs=refs)
   for q in refs:assert ref(ROOT/q['path'])==q
   with connect()as c:
    c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
   with connect()as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
   save(DOC/'result.json',result);print(json.dumps(dict(jobId=jid,sourceOnly=True,neighbourFaces=34)),flush=True)
 except Exception as e:
  if job:jobs.finish(job,error=str(e))
  raise
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
