"""Persist four exact outline provenance diagnostics and resumable holds."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-outline-provenance-result-20261008';BATCH=DOC.name
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();provenance=BASE/'government-xl-three-outline-provenance-20261008';curve=BASE/'government-xl-three-outline-curve-diagnostic-v3-20261008';rows=read(curve/'summary.json')['rows'];archive=read(provenance/'archive-features.json');assert digest((ROOT/'source-scripts/city/landsd-territory/landsd-hong-kong-source.geojson.gz').read_bytes())==archive['sourceArchiveSHA256'];out=[]
 for r in rows:
  uid=r['uid'];positive=r['archive']['passed'] and r['viewer']['passed']
  reason=('current-densified-chord-differs-from-same-original-circular-arc' if positive else 'archived-outline-vertices-do-not-follow-current-arc-within-2mm')
  followup=('Fresh scoped original-curve identity proof plus independent full physical/terrain/neighbour checks; no install credit.' if positive else 'Need authoritative same-revision curve or an evidenced source revision; do not enlarge2mm equality or relabel changed outline as tessellation only.')
  if uid=='landsd/241723:0':followup='Original tower arc lineage is positive, but Imperial podium258470 remains different; no assembly identity or installation credit.'
  out.append({'uid':uid,'csuid':r['csuid'],'originalArcLineagePassed':positive,'reason':reason,'state':'held-unknown','requiresAI':None,'requiresHumanDecision':False,'inProcess':False,'nextEvidence':followup,'installationApproved':False})
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs=[ref(Path(__file__)),ref(manifest),ref(HERE/'original_outline_curves.py'),ref(HERE/'test_original_outline_curves.py'),ref(HERE/'xl-three-outline-provenance.py'),ref(HERE/'xl-three-outline-curve-diagnostic.py'),ref(ROOT/'source-scripts/city/landsd-territory/manifest.json')]
 for name in ('government-xl-three-outline-provenance-20261008','government-xl-three-outline-curve-diagnostic-20261008','government-xl-three-outline-curve-diagnostic-v2-20261008','government-xl-three-outline-curve-diagnostic-v3-20261008'):
  refs.extend(ref(p) for p in sorted((BASE/name).iterdir()) if p.is_file())
 claim=reservations.claim('codex-outline-provenance-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'rows':out,'manifestSHA256':digest(manifest.read_bytes()),'evidenceRefs':refs};stage='exact-original-outline-true-curve-provenance-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'Source-coordinate diagnosis only; no identity acceptance or old result mutation. ArcGIS true arcs and archive/current viewer vertex chains tested at unchanged2mm anchor/line/radial bounds. Chord sagitta reported separately, never represented as a2mm polygon Hausdorff pass. AI used for code and unchanged source reasoning only.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'rows':out}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
