"""Record independent root review and exact source-only closure; no promotion."""
import importlib.util,json,shutil
from pathlib import Path
from run import ROOT,HERE,read
BATCH='government-xl-one-peking-finite-silhouette-source-review-checkpoint-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BATCHES=['government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010','government-xl-one-peking-hullett-original-primary-and-complete-visuals-v1-20261010','government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010','government-xl-one-peking-installed-hullett-finite-silhouette-proposal-v1-20261010','government-xl-one-peking-hullett-literal-production-geometry-v1-20261010','government-xl-one-peking-hullett-complete-literal-silhouette-check-v1-20261010']
def main():
 assert not DOC.exists();DOC.mkdir(parents=True)
 shutil.copyfile('/tmp/one-peking-finite-silhouette-root-tests-20261010.log',DOC/'root-independent-26-tests.log')
 (DOC/'ROOT_REVIEW.md').write_text('Root independently read the named complete finite-silhouette kernel and all 26 actual-source/adverse tests, then ran 26 tests PASS in 2.152 seconds. Identity-only source proposal: no final identity, physical, collision or installation credit. All five current forms and both raw failed reasons remain.\n\nA separate production-loader export retains all 48,419 faces. All eight full original/literal and current/provider target combinations give at most 0.021724296886188 m² effective foreign excess under unchanged 1 m², while the raw basic proxy is 5.270854248362673 m². No source-to-render tolerance supplies spatial credit. Fresh current/raw/native/source/provider binding and all physical gates are still required.\n\nThe V1 illustrative extra tower query was incorrect and nonaccepting; exact-derived V2 primary query supersedes only that query. All old evidence is retained.\n')
 refs=[Path(__file__),HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'test_one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'xl-one-peking-hullett-literal-production-geometry-v1-20261010.mjs',HERE/'xl-one-peking-hullett-complete-literal-silhouette-check-v1-20261010.py']
 paths=set()
 for b in BATCHES:
  d=DOC.parent/b
  refs.extend(p for p in d.rglob('*') if p.is_file())
  result=d/'result.json'
  if result.exists():
   for ref in read(result)['evidenceRefs']:
    if ref['path'].startswith('source-scripts/city/government-import/local/') or ref['path'].startswith('docs/astra-city/government-import/') or ref['path'].startswith('source-scripts/city/government-import/xl-one-peking') or ref['path'].startswith('source-scripts/city/government-import/one_peking') or ref['path'].startswith('source-scripts/city/government-import/test_one_peking'):paths.add(ref['path'])
 s=importlib.util.spec_from_file_location('peking_root_review_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'independent-root-source-review-and-complete-literal-silhouette-checkpoint-v1',refs,dict(uids=['landsd/233985:0','landsd/240487:0','landsd/73140:0'],rootIndependentTests=26,rootIndependentTestsPassed=True,identityAccepted=False,physicalAccepted=False,collisionExemption=False,installationApproved=False,currentManifestAcceptanceClaimed=False,sourceGeometryChanges=0))
 paths.update(str(p.relative_to(ROOT)) for p in refs);paths.update(str(p.relative_to(ROOT)) for p in DOC.rglob('*') if p.is_file())
 Path('/tmp/xl-one-peking-source-finite-silhouette-closed-scope-20261010.json').write_text(json.dumps(dict(paths=sorted(paths),batches=BATCHES+[BATCH]),indent=2))
 print(json.dumps(dict(paths=len(paths),batch=BATCH)),flush=True)
if __name__=='__main__':main()
