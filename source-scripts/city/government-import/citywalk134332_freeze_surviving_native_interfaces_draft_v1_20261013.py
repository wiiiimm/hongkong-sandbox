"""Draft source-only immutable complete Citywalk interface receipt; no acceptance."""
import argparse,json,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,connect,reservations
import citywalk134332_surviving_native_supervised_draft_v1_20261013 as W
Q=W.Q
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);a=p.parse_args();before=read(W.LOCAL/'protected-state-before.json');W.fence(a,before);d=read(Q.D/'diagnostic.json.gz');assert d['sourceOnly']and not d['currentAcceptance']and not d['identityAccepted']and not d['physicalAccepted']and not d['installationApproved'];assert d['completeSourceFaces']==41277 and d['completeOriginalBodies']==193 and d['sourceGeometryChanges']==d['terrainGeometryChanges']==0 and d['currentNativeCount']==6650 and d['currentManifest']==before['currentManifest'];assert len(d['bindings'])==48
 modes={'providerOriginal','actualLiteral','explicitLeftF32','explicitBalancedF32'}
 assert {(b['actor'],b['sourceWorld'],b['actorWorld'])for b in d['bindings']}=={(u,m,n)for u in Q.ACTORS for m in modes for n in modes}
 for b in d['bindings']:
  proof=d['proofs'][b['proofKey']];assert proof['allCompleteFiniteFacesAccounted']and proof['completeWholeSourceFaceIDs']==list(range(41277))and proof['completeActorFaceIDs']==list(range(b['actorFaces']))and proof['exactPairsTested']<=1000000
 spec=importlib.util.spec_from_file_location('citywalk_reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');walker=importlib.util.module_from_spec(spec);spec.loader.exec_module(walker);paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(W.__file__),paths);walker.local_imports(Path(Q.__file__),paths)
 for folder in [Q.D,Q.P,W.PROPOSAL]:paths.update(p for p in folder.rglob('*')if p.is_file())
 paths.update([W.LOCAL/'protected-state-before.json',W.LOCAL/'immutable-lease-at-start.json',W.CLOSURE_OUTPUT]);paths.update(ROOT/e['path']for e in d['evidenceRefs'])
 closure=read(W.CLOSURE_OUTPUT);walker.declared_refs(closure,paths);assert closure['inputHashes'][str(Q.JS.relative_to(ROOT))]==W.ref(Q.JS)['sha256'];assert all(attrs_hash==closure['inputHashes'][p]for p,attrs_hash in read(Q.D/'actual-attributes.json.gz')['completeRecursiveProductionModuleClosure']['inputHashes'].items())
 walker.declared_refs(W.verified_plan(),paths);walker.declared_refs(before,paths);walker.declared_refs(read(Q.P/'actual-seven-tests-readonly-preflight-validation-v1.json'),paths)
 attrs=read(Q.D/'actual-attributes.json.gz');paths.update(ROOT/p for p in attrs['inputHashes'])
 for path,h in attrs['inputHashes'].items():assert W.ref(ROOT/path)['sha256']==h
 # Current active lease inode is intentionally not frozen; immutable start snapshot is.
 assert W.LEASE not in paths;W.fence(a,before)
 result=walker.F.freeze(W.BATCH,'complete-original-citywalk-surviving-native-interface-context-no-acceptance',sorted(paths),dict(uids=[Q.UID,*Q.ACTORS],sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,completeSourceFaces=41277,completeOriginalBodies=193,currentNativeCount=6650,currentManifest=before['currentManifest'],fourByFourBindings=48,ordinaryMinusHalfMetrePolicyUnchanged=True,noTerrainOrIdentityRecomputation=True,allSourceRolesAndPhysicalGuardsRemainIndependent=True,completeDiagnostic=W.ref(Q.D/'diagnostic.json.gz')))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert W.ref(ROOT/e['path'])==e
 W.fence(a,before);print(json.dumps(dict(jobId=result['jobId'],resultSHA256=W.ref(Q.D/'result.json')['sha256'],allRefs=len(result['evidenceRefs']),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
