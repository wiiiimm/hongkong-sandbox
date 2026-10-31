"""DRAFT immutable source-only bounded grade-cap result; no approval."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import citywalk134332_bounded_whole_facet_grade_cap_draft_v2_20261013 as Q
import parkview_block17_freeze_current_source_evidence_20261011 as F

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);a=p.parse_args();*_,before,contract=Q.inputs(a);lease=read(Q.LOCAL/'reservation.json');assert reservations.owns(lease)and before==read(Q.LOCAL/'protected-state-before.json');d=read(Q.D/'diagnostic.json.gz')
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
 paths.update(p for p in Q.LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');F.declared_refs(d,paths);F.declared_refs(before,paths)
 assert Q.inputs(a)[-2]==before and reservations.owns(lease)
 result=F.F.freeze(Q.BATCH,'bounded-current-grade-MAX-exposure-whole-edge-cap-no-acceptance',sorted(paths),dict(uids=['landsd/134332:0'],sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,completeGroundFaces=4215,currentNativeCount=6650,currentManifest=before['currentState']['currentManifest'],all683BelowBoundRetained=True,all1322CoverageOnlyRetained=True,all193ObligationsRetained=True,diagnostic=Q.ref(Q.D/'diagnostic.json.gz')))
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 assert Q.inputs(a)[-2]==before and reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),resultSHA256=Q.ref(Q.D/'result.json')['sha256'])),flush=True)
if __name__=='__main__':main()
