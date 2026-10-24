"""Draft source-only complete finite receipt; genuine root/roles remain independent."""
import argparse,json,importlib.util
from pathlib import Path
import citywalk134332_current_complete_finite_ground_draft_v1_20261013 as Q
from run import ROOT,HERE,read,connect

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);a=p.parse_args();scope,prior,ground,*rest=Q.inputs(a);pins=rest[-1];before=read(Q.LOCAL/'protected-state-before.json');assert scope==before;Q.fence(a,before,pins,ground,True);d=read(Q.D/'diagnostic.json.gz');assert d['sourceOnly']and not d['physicalAccepted']and not d['installationApproved']and not d['gradeRootAccepted']and not d['all193RolesQualified'];assert d['completeSourceFaces']==41277 and d['completeOriginalBodies']==193 and d['ordinaryThresholdM']=='-1/2'
 assert len(d['allSourceGroundBindings'])==12;assert {(b['sourceWorld'],b['groundWorld'])for b in d['allSourceGroundBindings']}=={(m,g)for m in ['providerOriginal','actualLiteral','explicitLeftF32','explicitBalancedF32']for g in ['actualLiteral','explicitLeftF32','explicitBalancedF32']}
 for b in d['allSourceGroundBindings']:assert b['completeSourceFaces']==41277 and b['completeGroundFaces']==4215 and b['groundWorldSHA256']==Q.GROUND_SHA and b['proofTupleSHA256']in d['distinctCompleteFiniteProofs']
 for proof in d['distinctCompleteFiniteProofs'].values():
  rows=proof['allWholeFacetProofs'];assert [r['face']for r in rows]==list(range(41277));assert len(proof['completeOriginalBodyObligations'])==193;assert proof['ordinaryFailingFaces']==[r['face']for r in rows if not r['ordinaryFiniteProved']];assert proof['coverageFailingFaces']==[r['face']for r in rows if not r['completeProjectionCovered']];assert proof['strictUncertifiedFaces']==[r['face']for r in rows if not r['strictPositiveFiniteProved']];assert proof['foundationOrdinarySurfacePolicyProved']==all(r['ordinaryFiniteProved']for r in rows)
 spec=importlib.util.spec_from_file_location('citywalk_full_finite_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F);paths=set();F.local_imports(Path(__file__),paths);F.local_imports(Path(Q.__file__),paths)
 for folder in [Q.D,Q.P]:paths.update(p for p in folder.rglob('*')if p.is_file())
 paths.update([Q.LOCAL/'protected-state-before.json',Q.LOCAL/'immutable-lease-at-start.json']);F.declared_refs(d,paths);F.declared_refs(before,paths);F.declared_refs(read(Q.P/'executable-pins.json'),paths);assert Q.LEASE not in paths;Q.fence(a,before,pins,ground,True)
 result=F.F.freeze(Q.BATCH,'complete-current-citywalk-finite-ground-no-root-role-acceptance',sorted(paths),dict(uids=[Q.UID],sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,completeSourceFaces=41277,completeOriginalBodies=193,currentNativeCount=6650,currentManifest=d['currentManifest'],completeDiagnostic=Q.ref(Q.D/'diagnostic.json.gz'),sourceGroundBindings=12,ordinaryFailingFaceCounts={k:len(v['ordinaryFailingFaces'])for k,v in d['distinctCompleteFiniteProofs'].items()},coverageFailingFaceCounts={k:len(v['coverageFailingFaces'])for k,v in d['distinctCompleteFiniteProofs'].items()},all193RootAndSourceRolesRemainIndependent=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 Q.fence(a,before,pins,ground,True);print(json.dumps(dict(jobId=result['jobId'],resultSHA256=Q.ref(Q.D/'result.json')['sha256'],allRefs=len(result['evidenceRefs']),ordinaryFailures=result['ordinaryFailingFaceCounts'])),flush=True)
if __name__=='__main__':main()
