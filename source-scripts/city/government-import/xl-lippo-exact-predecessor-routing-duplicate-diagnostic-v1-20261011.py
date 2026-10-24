"""Freeze exact old routing duplicates, preserving new source recursive checks.
No historical HTML reference is reused as new identity evidence.
"""
import importlib.util,json,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
import lippo_exact_pending_predecessor_routing_copies_v1_20261011 as routing
import lippo_exact_pending_embedded_geometry_reference_v1_20261011 as typed
BATCH='government-xl-lippo-exact-predecessor-routing-duplicate-diagnostic-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CENSUS=Path('/tmp/xl-lippo-pending-predecessor-all-direct-reference-census-20261011.json')
FAILED=Path('/tmp/xl-lippo-exact-pending-additive-resume-root-closure-v6-20261011.log')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 capture=ROOT/routing.CAPTURE_PATH;previous=ROOT/routing.PREVIOUS_PATH;pending=ROOT/routing.PENDING_PATH;tile=ROOT/typed.TILE_PATH
 c,a,b,t=[p.read_bytes() for p in [capture,previous,pending,tile]]
 proof=routing.BoundRoutingCopies(c,a,b);embedded=typed.BoundResolver(c,t)
 typed_refs=[embedded.resolve(typed.CAPTURE_PATH,p,typed.at(embedded.context,p)) for p in typed.POINTERS]
 for p in proof.pointers:assert proof.verify_value(routing.CAPTURE_PATH,p,routing.at(proof.context,p))['completeDuplicateRoutingRowVerified']
 assert not proof.handles(routing.CAPTURE_PATH,proof.proof()['newCandidatePointer'])
 assert not proof.handles(routing.CAPTURE_PATH,'/fixtureFiles/completeRole')
 census=read(CENSUS);assert census['allUniqueOrdinaryPathSHAPairs']==135 and len(census['missing'])==2 and len(census['mismatching'])==3
 save(DOC/'diagnostic.json',dict(batch=BATCH,completeExactOldRoutingCopies=proof.proof(),sixEmbeddedReferencesStillPositivelyVerified=typed_refs,
  newCandidateRoutingRow=proof.pending['parts'][proof.newindex],currentGeometryRoleStageAndNewCandidateRemainOrdinaryRecursive=True,
  sourceOnly=True,newNumericGeometryExclusions=0,blanketContextLeaf=False,historicalMissingHTMLGainsNoNewEvidenceCredit=True,
  unresolvedHistoricalCacheReferences=[dict(historicalSourcePath=r['path'],historicalDeclaredSHA256=r['sha256'],duplicateOldRoutingPointers=r['pointers']) for r in census['missing']],
  sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,publication=False,newlyInstalled=0))
 # These are preserved failed diagnostic logs, not accepted source evidence.
 for source,name in [(CENSUS,'preserved-all-direct-reference-census.txt'),(FAILED,'preserved-v6-old-cache-reference-mismatch.log')]:
  assert source.is_file();target=DOC/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
 tests=HERE/'test_lippo_exact_pending_predecessor_routing_copies_v1_20261011.py';p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',tests.name,'-v'],cwd=ROOT,capture_output=True,text=True)
 save(DOC/'tests.json',dict(exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr,actualImmutableSourceCounterexamples=True));assert p.returncode==0,p.stderr
 assert [p.read_bytes() for p in [capture,previous,pending,tile]]==[c,a,b,t]
 refs=[Path(__file__),capture,previous,pending,tile,HERE/'lippo_exact_pending_predecessor_routing_copies_v1_20261011.py',tests,
  HERE/'lippo_exact_pending_embedded_geometry_reference_v1_20261011.py',HERE/'verify_lippo_closed_model_checkpoint_typed_routing_v7_20261011.py']
 spec=importlib.util.spec_from_file_location('lippo_exact_routing_copy_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'exact-old-routing-duplicates-new-candidate-current-geometry-recursive-no-exclusions',refs,
  dict(uids=['landsd/239465:0'],completeOldRoutingRecords=4944,completeDuplicateOldRoutingRows=9888,newCandidateRecursive=True,completeCurrentRoleAndStageRecursive=True,
  newNumericGeometryExclusions=0,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,publication=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=result['jobId'],completeOldRoutingRecords=4944,newCandidateRecursive=True,publication=False)),flush=True)
if __name__=='__main__':main()
