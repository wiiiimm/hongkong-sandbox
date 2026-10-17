"""DRAFT source-only diagnostic freezer; never backfill legacy acceptance."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_bounded_current_grade_cap_routes_draft_v1_20261012 as G

def main():
 a=argparse.ArgumentParser();a.add_argument('--lease-file',required=True);a=a.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(G.DOC/'result.json').exists();receipt,scope,worlds,ground,prior=G.inputs();d=read(G.DOC/'diagnostic.json.gz');assert d['completeFaces']==46918 and d['completeGroundFaces']==3240 and d['wholeGroundSHA256']==G.F.GROUND_SHA and set(d['allFourStreamBindings'])==G.F.NAMES and d['all118OriginalBodyObligationsRetained']and d['allOrdinaryAndStrictFailuresRetained']
 assert not any(d[k]for k in ['sourceGeometryChanges','terrainGeometryChanges','gradeRootAccepted','burialRoleAccepted','physicalAccepted','installationApproved'])
 for name,b in d['allFourStreamBindings'].items():
  assert b==prior['allFourStreamBindings'][name];p=d['distinctBoundedRouteDiagnostics'][b['proofTupleSHA256']];assert p['all42FailingSteepFaces']==prior['distinctCompleteFiniteProofs'][b['proofTupleSHA256']]['ordinaryFailingFaces']and len(p['all443StrictUncertifiedFacesRetained'])==443 and len(p['routes'])==42 and p['other117OriginalBodyObligationsUndischarged']
  for r in p['routes']:
   if r['boundedOriginalPath']:assert r['genuineExposedGradeDiagnostic']and r['allTraversedWholeEdgesStrictlyExposed']and r['allNonseedPathFacesStrictPositive']and r['independentExistingCapKernelDiagnostic']['allAffectedHavePaths']
 walker=G.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_grade_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(G.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']:assert G.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(G.DOC/'diagnostic.json.gz');paths.add(G.PROPOSAL/'METHOD.md');paths.add(G.PROPOSAL/'no-worker-schema-hash-validation.json');paths.add(Path(a.lease_file));paths.update(p for p in G.LOCAL.rglob('*')if p.is_file());result=walker.F.freeze(G.BATCH,'bounded-steep-grade-whole-exposed-edge-strict-cap-context-no-root-role-approval',sorted(paths),dict(uids=[G.F.UID],sourceOnly=True,physicalAccepted=False,gradeRootAccepted=False,burialRoleAccepted=False,legacyInstalledDeliveryPreserved=True,modelReviewWrites=0,completeFaces=46918,all118OriginalBodyObligationsRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert G.ref(ROOT/e['path'])==e
 G.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
