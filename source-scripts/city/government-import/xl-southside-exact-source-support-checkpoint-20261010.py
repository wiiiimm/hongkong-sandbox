"""Freeze complete original source terrain/coverage/component diagnostics."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-southside-exact-source-support-checkpoint-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['government-xl-southside-station-original-pair-source-tin-context-20261010','government-xl-southside-original-terrain-gap-witnesses-20261010','government-xl-southside-station-original-pair-exact-slab-terrain-20261010','government-xl-southside-station-original-pair-source-anchor-paths-20261010','government-xl-southside-unattached-original-components-20261010']
SCRIPTS=['xl-southside-station-original-pair-source-tin-context-20261010.py','xl-southside-original-terrain-gap-witnesses-20261010.py','xl-southside-station-original-pair-exact-terrain-coverage-20261010.py','xl-southside-station-original-pair-exact-slab-terrain-coverage-20261010.py','xl-southside-station-original-pair-source-ground-interfaces-20261010.mjs','xl-southside-station-original-pair-source-anchor-paths-20261010.py','xl-southside-unattached-original-components-20261010.py','exact_original_slab_projection_coverage_20261010.py','test_exact_original_slab_projection_coverage_20261010.py']
def main():
 assert not DOC.exists();base=DOC.parent;graph=read(base/NAMES[3]/'diagnostic.json.gz');slab=read(base/NAMES[2]/'exact-original-coverage.json.gz');tin=read(base/NAMES[0]/'complete-original-source-tin.json.gz');paths=[Path(__file__)]+[HERE/n for n in SCRIPTS]
 for name in NAMES:paths +=[p for p in (base/name).rglob('*') if p.is_file()]
 paths +=[ROOT/p for p in tin['sourceFileHashes']]
 for name in NAMES:
  for p in (base/name).rglob('*.json*'):
   obj=read(p)
   for key in ['inputHashes','hashes']:
    paths.extend(ROOT/q for q in obj.get(key,{}) if (ROOT/q).is_file())
 summary=read(base/NAMES[0]/'summary.json');rows=slab.get('rows',slab.get('faces',[]));save(DOC/'coverage-source-summary.json',{'sourceSummary':summary,'exactOriginalCoverageResult':slab,'completeSourceGraph':{'components':graph['completeOriginalPairComponents'],'positivePaths':len(graph['completePositivePaths']),'unattachedComponents':graph['componentsWithoutPositiveOriginalGroundPath']},'interruptedSequentialSubtractionAttempt':{'producer':'xl-southside-station-original-pair-exact-terrain-coverage-20261010.py','exit':130,'firstSourceFace':2127,'resultProduced':False,'reason':'Combinatorial Fraction polygon-subtraction growth; interrupted after independently completed exact slab coverage. No source defect inferred.'}})
 (DOC/'README.md').write_text('''# Complete original Southside source support diagnostics

The unchanged 11,699-face Southside and 1,191-face Wong Chuk Hang station originals were tested against 29,497 authenticated government terrain facets from all four covering sheets. Seventy-three raw finite-projection flags are resolved by exact Fraction slab coverage plus all three closed-edge interval checks; 18 meaningful helper tests, including tiny real interior holes, passed locally and independently by the root agent. This is original-source coverage, not current terrain or installation approval.

All 208 original components are retained. Strict source-TIN anchors and complete positive-dimensional original contacts yield 189 paths; 19 remain without such paths. Their complete faces, heights, original counterpart witnesses and raw source-ground interfaces are recorded separately. Floating nearest-surface distances grant no support or decorative role.

The earlier sequential Fraction polygon-subtraction worker was interrupted (exit 130) on its first source face 2127 after combinatorial growth. It produced no coverage result. The independent slab method completed every one of the 73 flags without lowering a threshold or altering geometry.

Current source/provider identity was independently reviewed in the separate frozen named identity receipt. All current terrain, foundations, other actors, collision, runtime, staged/live browser and guarded publication checks remain required. No government mesh, pose or terrain has changed and zero models were installed in this checkpoint.
''')
 spec=importlib.util.spec_from_file_location('southside_source_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);result=m.freeze(BATCH,'complete-original-exact-source-coverage-and-component-support-v1',paths,{'uids':['landsd/315025:0','landsd/300867:0'],'completeOriginalFaces':12890,'completeOriginalComponents':208,'authenticatedOriginalTerrainFaces':29497,'rawProjectionFlagsResolvedExactly':73,'completePositiveOriginalGroundPaths':189,'unattachedOriginalComponents':19,'identityAccepted':False,'physicalAccepted':False,'supportAccepted':False,'scriptFullAcceptancePassed':False,'remainingReason':'19-original-component-roles-plus-independent-current-full-physical-checks','nextStep':'Diagnose exact original architectural roles of all19 parts; preserve all faces and complete current physical/runtime/actor checks before staging.','sourceIdentityReviewUsedAI':True})
 scope=set([str(DOC.relative_to(ROOT))]+[str((base/n).relative_to(ROOT)) for n in NAMES]+[str(p.relative_to(ROOT)) for p in paths]);Path('/tmp/xl-southside-exact-source-support-closed-scope-20261010.json').write_text(json.dumps(sorted(scope),indent=2)+'\n');print({'jobId':result['jobId'],'closedPaths':len(scope)},flush=True)
if __name__=='__main__':main()
