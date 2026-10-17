"""Persist concrete source-specific holds without declaring corruption/impossibility."""
import uuid,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-original-hold-followthrough-20261008';DOC=BASE/BATCH
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();names=['government-xl-outline-provenance-result-20261008','government-xl-gleneagles-three-original-closure-20261008','government-xl-gleneagles-original-contact-seams-20261008','government-xl-gleneagles-original-contact-seams-v2-20261008','government-xl-ocean-walk-current-wall-clearance-diagnostic-20261008'];receipts=[];refs=[ref(Path(__file__))]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for v in r['evidenceRefs']:assert ref(ROOT/v['path'])==v
   receipts.append(r);refs.append(ref(p));refs.extend(r['evidenceRefs'])
 geo=BASE/'government-xl-four-current-geojson-provenance-20261008';refs.extend(ref(p) for p in geo.iterdir() if p.is_file());refs.append(ref(HERE/'xl-four-current-geojson-provenance.py'));refs.append(ref(HERE/'test_original_outline_government_examples.py'));manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(ref(manifest))
 outline=receipts[0];rows=[]
 for r in outline['rows']:
  rows.append({**r,'humanStatus':'held-unknown','permanentRejection':False,'retainCurrentModel':True,'needsAIProcessing':None,'needsComputeProcessing':None,'needsHumanDecision':False,'nextStep':r['nextEvidence']})
 closure=receipts[1]
 for r in closure['rows']:
  assert r['unresolvedSamples'] in (47,109)
  rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'supportUid':r['supportUid'],'supportSHA256':r['supportSHA256'],'humanStatus':'held-unknown','reasons':['original-support-interface-unresolved'],'unresolvedSamples':r['unresolvedSamples'],'samples':r['samples'],'nextStep':'Use the recovered original tower and podium face/gap evidence to establish an actual original support route. No new seam correction; do not repeat this same source pair. All identity/compound-foundation/terrain/neighbour/browser/publication gates remain.','permanentRejection':False,'retainCurrentModel':True,'needsAIProcessing':None,'needsComputeProcessing':None,'needsHumanDecision':False,'inProcess':False})
 ocean=receipts[4];rows.append({'uid':ocean['uid'],'sourceSHA256':ocean['sourceSHA256'],'humanStatus':'held-unknown','reasons':['current-rendered-terrain-source-clearance-over-0.5m','current-failed-faces-include-non-vertical-surfaces'],'rawMinimumGapM':ocean['rawClearance']['minSurfaceGap'],'failedSamples':ocean['rawClearance']['failedSamples'],'wholeFoundationPassed':ocean['foundation']['fullyBuriedAreaFraction']==0 and ocean['foundation']['fullyBuriedUpwardTriangles']==0,'nextStep':'Current terrain cannot use a vertical-wall-only explanation. Original TIN has different wall-only failures but six retained basic-neighbour regressions and unresolved original support contacts; new source-specific visible-surface/terrain/support evidence is required. Do not repeat unchanged checks.','permanentRejection':False,'retainCurrentModel':True,'needsAIProcessing':None,'needsComputeProcessing':None,'needsHumanDecision':False,'inProcess':False})
 next(r for r in rows if r['uid']=='landsd/195849:0')['nextStep']='Original arc lineage is established, but historical original source-local terrain has11.47m source clearance and two retained basic-neighbour regressions; newly recovered tower originals retain47/109 interface failures. Need a new original source/terrain/support explanation, not an outline or threshold waiver.'
 refs=list({v['path']:v for v in refs}.values());payload={'rows':rows,'evidenceRefs':refs,'priorJobIds':[r['jobId'] for r in receipts],'manifestSHA256':digest(manifest.read_bytes())};claim=reservations.claim('codex-original-hold-followthrough-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  stage='original-source-specific-hold-followthrough-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'batch':BATCH,'jobId':jid,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'aiGeometryModelling':False,'qualification':'Exact source-specific failures and revisit conditions, not permanent noninstallability, source corruption or inferred AI/human decisions. Prior two Gleneagles seam input-order assertions are diagnostic setup errors; the corrected two-pair run has zero loader errors and genuine unresolved contact results. Fresh GeoJSON differs from archive by8–61mm; no polygon equality approval.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for v in refs:assert ref(ROOT/v['path'])==v
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'neonVerified':True,'heldRecords':len(rows),'newlyInstalled':0}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
