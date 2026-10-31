"""Retain full-source identity context and every-face terrain diagnostics; no approval."""
import importlib.util,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-unmapped-whole-context-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
INPUT=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();bindings=read(INPUT)
 for r in bindings['evidenceRefs']:assert ref(ROOT/r['path'])==r
 resources=['native-model:'+r['sourceKey']for r in bindings['rows']]+['building:'+b['viewerUID']for r in bindings['rows']for b in r['bindings']]
 claim=reservations.claim('unmapped-whole-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();stage='whole-original-current-context-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,{'input':ref(INPUT),'resources':resources});job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
  subprocess.run(['node',str(HERE/'xl_unmapped_current_ground_v1_20261015.mjs')],cwd=ROOT,check=True)
  ground=read(DOC/'ground.json.gz');native={r['model']['modelId']:r for r in read(BASE/'government-xl-unmapped-full-bounds-provider-v1-20261015/native-inputs.json')['rows']};recovery={r['modelId']:r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']}
  spec=importlib.util.spec_from_file_location('existing_whole_context',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
  rows=[];refs=[ref(INPUT),ref(Path(__file__)),ref(HERE/'xl_unmapped_current_ground_v1_20261015.mjs'),ref(HERE/'xl-final-script-pass.py'),ref(DOC/'ground.json.gz')]
  for r in bindings['rows']:
   source=recovery[r['modelId']];asset=ROOT/source['asset']['path'];assert ref(asset)==source['asset'];refs.append(ref(asset));tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);terrain=np.asarray(next(g['position']for g in ground['regions']if g['modelId']==r['modelId']),dtype=np.float64).reshape(-1,3,3)
   for b in r['bindings']:
    uid=b['viewerUID'];form=next(f for f,_,_ in forms if f['uid']==uid);assert form==b['viewerForm'];row={'uid':uid,'native':native[r['modelId']]};identity=final.identity_context(row,tri,forms);foundation=final.foundation_context(tri,terrain,final.form_polygon(form));rows.append({'uid':uid,'modelId':r['modelId'],'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'identity':identity,'foundationDiagnostic':foundation,'installationApproved':False});print(uid,foundation['fullyBuriedTriangles'],identity['sourceExcessCoveredByUnrelatedFormsM2'],flush=True);assert reservations.heartbeat(lease)['ok']
   refs.extend(ref(ROOT/'3d-viewer'/tile)for tile in sorted({tile for _,_,tile in forms}))
  for p,h in ground['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  for r in bindings['evidenceRefs']:assert ref(ROOT/r['path'])==r
  save(DOC/'context.json',{'rows':rows});refs.append(ref(DOC/'context.json'))
  result={'jobId':jid,'rows':rows,'evidenceRefs':refs,'newlyInstalled':0,'sourceGeometryChanges':0,'publicationApproved':False,'qualification':'Every original face examined at vertices and centroid against actual rendered terrain, not a continuous full-face clearance proof. Original unmatched source metadata retained; no identity or placement approval.'}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(jid,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
