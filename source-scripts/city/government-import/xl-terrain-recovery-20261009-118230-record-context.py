"""Fence newly measured exact original semantic/identity blockers; no rejection credit."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BATCH='xl-terrain-recovery-20261009-118230-original-components';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-wall-context/diagnostic.json.gz'
BASE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-current-inputs'
LEASE='/tmp/xl-terrain-recovery-20261009-118230-role-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
 d=read(CONTEXT);components=read(DOC/'diagnostic.json.gz');current=read(BASE/'indexed-preflight.json')
 assert d['uid']==components['uid']=='landsd/118230:0' and d['wholeSourceFaces']==19438 and not d['wholeSourceUncoveredFaces']
 assert len(d['affectedWallFaces'])==355 and not d['otherAffectedFaces'] and not d['allAffectedWallsHaveRoles']
 identity=current['rows'][0]['identity'];assert not identity['passed']
 refs=d['evidenceRefs']+components['evidenceRefs']+current['evidenceRefs']+[ref(p) for p in [Path(__file__),CONTEXT,DOC/'diagnostic.json.gz',BASE/'check-selection.json.gz',BASE/'context.json.gz',BASE/'indexed-preflight.json']]
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);payload={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'evidenceRefs':refs};stage='two-harbourfront-complete-original-context-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 counts={}
 for f in d['originalOpenExteriorPaths']['faces']:
  for reason in f['reasons']:counts[reason]=counts.get(reason,0)+1
 result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'humanStatus':'held-unknown','requiresAI':False,'requiresHumanDecision':False,'needsComputeProcessing':True,'sourceGeometryChanges':0,'newlyInstalled':0,'publication':False,'installationApproved':False,'permanentRejection':False,'wholeOriginalFaces':19438,'wholeSourceUncoveredFaces':0,'affectedFaces':355,'affectedNonWalls':0,'rawWallRoleFailureCounts':counts,'currentIdentityReasons':identity['reasons'],'currentSourceExtent':identity['freshCurrentIdentity'],'upwardMinimumGapM':d['upwardContinuousMinimumGapM'],'originalCollapsedFacesAccounted':d['originalZeroAreaFaces'],'originalOpenWindingConflictsPreserved':len(d['originalOpenExteriorPaths']['originalOrientationConflicts']),'heldReasons':['Two original 260-face open vertical cylinders have no authored upward cap or direct wall-only edge path to a clear roof; their exact original attachments/exposed upper boundaries need proof.','Seven crossing faces of a separate original54-face low exterior object have no exposed per-face witness; this fails the current narrow wall contract.','Fresh whole-current-cell identity retains 27.3502m² exterior excess extending11.9967m from target, with zero unrelated overlaps; original provider/component identity needs additional source-specific evidence.'],'nextStep':'Compute exact original cylinder-to-whole-source contacts and complete low-object segmentation context; independently research exact provider source-target extent. Current narrow contract/raw diagnostics remain failed. If a conservative new source-bound contract is justified, require fresh complete terrain/foundation/foreign/native/runtime/browser gates before any install.','qualification':'New continuous face/topology investigation against byte-pinned historical drawn terrain, plus fresh current identity. Historical ground is not a fresh physical acceptance. No source editing, omitted faces, extent waiver, permanent impossibility or AI geometry modelling claim.'}
 try:
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'resultVerified':True,'newlyInstalled':0}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
