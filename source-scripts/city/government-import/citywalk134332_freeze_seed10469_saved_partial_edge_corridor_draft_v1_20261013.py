"""DRAFT source-only one-seed corridor freezer; no root or installation credit."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import citywalk134332_seed10469_saved_partial_edge_corridor_draft_v1_20261013 as Q
import parkview_block17_freeze_current_source_evidence_20261011 as F
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--expected-grade-result-sha',required=True);a=p.parse_args();finite,labels,worlds,ground,before,old,prior,contract=Q.inputs(a);valid=Q.validation();lease=read(Q.LOCAL/'immutable-lease-at-start.json');assert reservations.owns(lease) and before==read(Q.LOCAL/'protected-state-before.json');d=read(Q.D/'diagnostic.json.gz')
 assert d['all12Bindings']==old['all12Bindings'] and len(d['distinctBoundedCorridorDiagnostics'])==3
 assert d['sourceOnly'] and not any(d[k] for k in ['currentAcceptance','physicalAccepted','installationApproved','gradeRootAccepted'])
 for key,z in d['distinctBoundedCorridorDiagnostics'].items():
  seed,miss,donor,incoming,outgoing=Q.select_case(old['distinctGradeCapDiagnostics'][key])
  assert z['seedGradeReusedVerbatim']==seed and z['priorUnresolvedRouteReusedVerbatim']==miss and z['donorPathReusedVerbatim']==donor and z['wholeEdgeNegativePreservedVerbatim']==incoming and z['outgoingWholeEdgePositiveReusedVerbatim']==outgoing
  assert len(z['allBoundedAttempts'])<=Q.MAX_ATTEMPTS and z['routeFound']==any(t.get('routeFound',False) for t in z['allBoundedAttempts'])
  for t in z['allBoundedAttempts']:
   if t.get('pointOnlyRejected'):continue
   assert t['seedFacetMembership']['closedConvexOriginalFacetContainment'] and t['donorFacetMembership']['closedConvexOriginalFacetContainment'] and t['wholeFacetStrictCredit'] is False
   if t['routeFound']:assert Q.route_found(t['incomingSubsegment']['completeGroundSegmentCertificate'],t['gradeToSubedgeExposure'],t['withinDonorCertificate'])
 paths=set();F.local_imports(Path(__file__),paths);F.local_imports(Path(Q.__file__),paths)
 for folder in [Q.D,Q.P]:paths.update(p for p in folder.rglob('*') if p.is_file())
 paths.update(p for p in Q.LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json');F.declared_refs(d,paths);F.declared_refs(before,paths)
 assert Q.inputs(a)[4]==before and reservations.owns(lease)
 result=F.F.freeze(Q.BATCH,'one-original-seed-exposed-subedge-connected-facet-corridor-no-acceptance',sorted(paths),dict(uids=['landsd/134332:0'],sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,completeGroundFaces=4215,currentNativeCount=6650,currentManifest=before['currentState']['currentManifest'],investigatedSeed=10469,donorSeed=10468,priorCap=25910,all683RawFailuresPreserved=True,all1322CoverageOnlyPreserved=True,all193BodyObligationsPreserved=True,diagnostic=Q.ref(Q.D/'diagnostic.json.gz')))
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 assert Q.inputs(a)[4]==before and reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),resultSHA256=Q.ref(Q.D/'result.json')['sha256'])),flush=True)
if __name__=='__main__':main()
