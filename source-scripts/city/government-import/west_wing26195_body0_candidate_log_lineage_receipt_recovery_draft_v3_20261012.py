"""DRAFT explicit captured-log-prefix recovery; old complete receipt untouched."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,connect,reservations
import west_wing26195_current_body0_source_bound_candidate_role_draft_v2_20261012 as P
BATCH='government-xl-west-wing26195-body0-candidate-log-lineage-receipt-recovery-v3-20261012';DOC=P.R.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=P.R.BASE/'government-xl-west-wing26195-body0-candidate-log-lineage-receipt-recovery-proposal-v3-20261012';ref=P.ref;FREEZER=HERE/'west_wing26195_freeze_body0_candidate_log_lineage_receipt_recovery_draft_v3_20261012.py'
OLD_JOB='039aa8ed90b792aad9ed3fb51c408a2e87519e2cea7e06cb1b3960c9df268cef';OLD_SHA='16c71fa79c721a1cd17699ff3c9adb5130ecdd758a0fd3d2d6db444dfcf093b6';LOG_PATH=str((P.PROPOSAL/'actual-supervised-certificate-v2.log').relative_to(ROOT));LOG_SHA='6d3d457a8590b276217d66658a09be0ed994af488ace6eca400b621e69ba8a01';FULL_SHA='21fbf3e62dfce5e334d638b0fabd0488249a1a2180938a02f83f3cd3b7af7c91'
def inputs():
 old=read(P.DOC/'result.json');assert ref(P.DOC/'result.json')['sha256']==OLD_SHA and old['jobId']==OLD_JOB
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(OLD_JOB,)).fetchone()==('complete',old)
 changed=[];paths=set()
 for e in old['evidenceRefs']:
  if ref(ROOT/e['path'])!=e:changed.append(e)
  else:paths.add(ROOT/e['path'])
 assert changed==[dict(path=LOG_PATH,sha256=LOG_SHA)] and len(old['evidenceRefs'])==1603
 full=ROOT/LOG_PATH;prefix=P.PROPOSAL/'actual-stream-frozen-prefix-evidence-v2.log';terminal=HERE/'execution-logs'/f'{P.BATCH}-terminal.log'
 assert ref(full)['sha256']==FULL_SHA==ref(terminal)['sha256'] and ref(prefix)['sha256']==LOG_SHA
 assert len(prefix.read_bytes())==132 and full.read_bytes()[:132]==prefix.read_bytes()
 audit=read(P.PROPOSAL/'actual-terminal-reference-audit-v2.json');assert audit['exitCode']==1 and not audit['owns']and audit['releasedAt']and audit['allCurrentInputsAnd15ProtectedRowsUnchanged'];assert audit['streamPrefix']['ref']==ref(prefix)
 previous=read(P.LOCAL/'reservation.json');assert not reservations.owns(previous)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT released_at FROM astra_modelling.reservation_groups WHERE token=%s',(previous['token'],)).fetchone()[0] is not None
 assert all(not(Path('/proc')/str(n)).exists()for n in audit['allOwnedPIDsGone'])
 scope,_,certificate=P.inputs();diagnostic=read(P.DOC/'diagnostic.json.gz');assert diagnostic['body0CandidateRoleCertificate']==certificate and diagnostic['currentManifest']==scope['currentManifest']
 paths.update([P.DOC/'result.json',P.DOC/'diagnostic.json.gz',P.PROPOSAL/'actual-terminal-reference-audit-v2.json',P.PROPOSAL/'actual-log-move-postterminal-stat-provenance-v2.json',full,prefix,terminal,P.LOCAL/'reservation.json'])
 return scope,certificate,paths

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');args=parser.parse_args();scope,certificate,paths=inputs();assert not(DOC/'result.json').exists()
 if not args.owned:
  claimed=reservations.claim('westwing-body0-log-lineage-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert claimed['ok'],claimed;save(LOCAL/'reservation.json',json.loads(json.dumps(claimed['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');walker=P.T.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbody0logrecovery');walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);paths.update(ROOT/e['path']for e in P.validation());paths.update(p for p in PROPOSAL.iterdir()if p.is_file());codes=[ref(p)for p in sorted(paths)];P.fence(scope,lease,codes);assert reservations.heartbeat(lease)['ok']
 save(DOC/'receipt-lineage.json',dict(sourceOnly=True,noNumericOrSourceRoleRecomputation=True,oldCompletedReceipt=ref(P.DOC/'result.json'),oldPostfreezeExitCode=1,exactOld1602UnchangedRefs=True,soleHistoricalLog=dict(originalPath=LOG_PATH,historicalSHA256=LOG_SHA,actualStreamPrefix=ref(P.PROPOSAL/'actual-stream-frozen-prefix-evidence-v2.log'),prefixBytes=132,fullTerminalStream=ref(HERE/'execution-logs'/f'{P.BATCH}-terminal.log'),notRestoredToOriginalPath=True),body0CandidateRoleCertificate=certificate,currentManifest=scope['currentManifest'],physicalAccepted=False,installationApproved=False))
 subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
