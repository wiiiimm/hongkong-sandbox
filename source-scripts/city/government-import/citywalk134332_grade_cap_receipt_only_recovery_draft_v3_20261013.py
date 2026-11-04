"""DRAFT immutable source-only bounded grade-cap result; no approval."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,connect,reservations
import citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013 as Q
import parkview_block17_freeze_current_source_evidence_20261011 as F
from archive_declared_terminal_evidence_v1_20261013 import archive_declared_external

LOCAL=HERE/'local/government-xl-citywalk134332-grade-cap-receipt-recovery-v3-20261013'
PROPOSAL=ROOT/'docs/astra-city/government-import/government-xl-citywalk134332-grade-cap-receipt-recovery-proposal-v3-20261013'

def terminal_gate(a):
 t=read(ROOT/a.terminal_audit);assert Q.ref(ROOT/a.terminal_audit)['sha256']==a.expected_terminal_sha
 assert t['authoritativeSession']==53906 and t['exitCode']==1 and t['numericalDiagnosticsComplete']and t['freezerReservationCollisionObserved']
 assert t['actualProducerPIDs']==[1599820,1602373,1602551]and t['allActualProducerPIDsGone']and t['canonicalGroupReleased']and not t['ownsAfterTerminal']
 for pid in t['actualProducerPIDs']:assert not (Path('/proc')/str(pid)).exists()
 ps=subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True)
 assert not any('citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013.py'in line and '/tmp/astra-city-venv/bin/python'in line and '/bin/bash'not in line for line in ps.splitlines())
 for e in t['actualTerminalEvidenceRefs']+t['allCompletedPerSeedRefs']+t['completedTupleRefs']:assert Q.ref(ROOT/e['path'])==e
 assert len(t['allCompletedPerSeedRefs'])==2049 and len(t['completedTupleRefs'])==3
 assert t['savedCompleteDiagnostic']==Q.ref(Q.D/'diagnostic.json.gz')
 for e in read(PROPOSAL/'executable-pins.json')['refs']:assert Q.ref(ROOT/e['path'])==e
 return t


def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--owned',action='store_true');p.add_argument('--preflight-only',action='store_true');p.add_argument('--terminal-audit',required=True);p.add_argument('--expected-terminal-sha',required=True);a=p.parse_args();terminal=terminal_gate(a);*_,before,contract=Q.inputs(a);oldlease=read(Q.LOCAL/'immutable-lease-at-start.json');assert not reservations.owns(oldlease);assert before==read(Q.LOCAL/'protected-state-before.json');assert read(Q.LOCAL/'parent-release-audit.json')['ownsAfterCleanup']is False;assert (Q.LOCAL/'failed-terminal-parent-audit.json').is_file();d=read(Q.D/'diagnostic.json.gz')
 if a.preflight_only:print(json.dumps(dict(savedDiagnosticPresent=True,authoritativeTerminalAndActualPIDsVerified=True,noNumericalReplay=True,oldCanonicalGroupNotOwned=True)));return
 if not a.owned:
  assert not LOCAL.exists();resources=sorted(['building:'+u for u in before['currentState']['uids']]+['native-model:'+before['currentState']['sourceKey'],'source-context:'+Q.BATCH+'-receipt-recovery-v3-compute']);claim=reservations.claim('citywalk-grade-receipt-'+str(uuid.uuid4()),resources,batch=Q.BATCH+'-receipt-recovery',ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
  try:
   subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
  except BaseException as error:
   save(LOCAL/'failed-recovery-parent-audit.json',dict(errorType=type(error).__name__,error=str(error),noNumericalReplay=True));raise
  finally:
   owned=reservations.owns(lease);released=reservations.release(lease)if owned else None;save(LOCAL/'recovery-parent-release-audit.json',dict(ownedBeforeCleanup=owned,cleanupRelease=released,ownsAfterCleanup=reservations.owns(lease)))
  return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);save(LOCAL/'immutable-lease-at-start.json',lease)
 assert d['completeSourceFaces']==41277 and d['originalBodies']==193 and d['completeGroundFaces']==4215 and len(d['all12Bindings'])==12 and len(d['distinctGradeCapDiagnostics'])==3;assert d['sourceOnly']and not d['currentAcceptance']and not d['gradeRootAccepted']and not d['physicalAccepted']and not d['installationApproved']
 for key,z in d['distinctGradeCapDiagnostics'].items():
  assert len(z['all683SeedProofs'])==len(z['all683Routes'])==683 and len(z['coverageOnlyFaceIDs'])==1322 and z['all193BodyObligationsRetained'];seeds={s['seed']:s for s in z['all683SeedProofs']};assert len(seeds)==683
  for s in seeds.values():assert read(Q.LOCAL/'grade'/key/f"{s['seed']:05d}.json.gz")==s
  edges={tuple(e['sourceFaces']):e for e in z['allExaminedWholeSharedEdges']}
  for route in z['all683Routes']:
   path=route['pathCapToSeed']
   if path:
    assert path[-1]==route['seed']and seeds[path[-1]]['qualifiedGradeDiagnostic'];assert route['capSavedWholeFacetProof']['strictPositiveFiniteProved'];assert all(edges[tuple(sorted((x,y)))]['completeGroundProof']['strictlyExposedWholePositiveInterface']for x,y in zip(path,path[1:]))
 paths=set();F.local_imports(Path(__file__),paths);F.local_imports(Path(Q.__file__),paths)
 for folder in [Q.D,Q.P]:paths.update(p for p in folder.rglob('*')if p.is_file())
 paths.update(p for p in Q.LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');paths.update(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');F.declared_refs(d,paths);F.declared_refs(before,paths);F.declared_refs(terminal,paths);paths.add(ROOT/a.terminal_audit);paths.update(p for p in PROPOSAL.rglob('*')if p.is_file())
 paths,archives=archive_declared_external(paths,ROOT,PROPOSAL/'external-terminal-archive',terminal['actualTerminalEvidenceRefs'])
 save(LOCAL/'external-terminal-archive-map.json',dict(records=archives,originalTerminalAudit=Q.ref(ROOT/a.terminal_audit),noNumericalReplay=True))
 paths.add(LOCAL/'external-terminal-archive-map.json')
 assert Q.inputs(a)[-2]==before and reservations.owns(lease)and terminal_gate(a)==terminal
 result=F.F.freeze(Q.BATCH,'bounded-current-grade-MAX-exposure-whole-edge-cap-no-acceptance',sorted(paths),dict(uids=['landsd/134332:0'],sourceOnly=True,externalTerminalArchives=archives,originalTerminalAudit=Q.ref(ROOT/a.terminal_audit),currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,completeGroundFaces=4215,currentNativeCount=6650,currentManifest=before['currentState']['currentManifest'],all683BelowBoundRetained=True,all1322CoverageOnlyRetained=True,all193ObligationsRetained=True,diagnostic=Q.ref(Q.D/'diagnostic.json.gz')))
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 assert Q.inputs(a)[-2]==before and reservations.owns(lease)and terminal_gate(a)==terminal;print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),resultSHA256=Q.ref(Q.D/'result.json')['sha256'])),flush=True)
if __name__=='__main__':main()
