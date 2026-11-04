"""Freeze exact terrain-only source representation proof, no physical acceptance."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save
BATCH='government-xl-tung-sing-exact-terrain-representation-checkpoint-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['government-xl-tung-sing-flat-parent-child-census-20261010','government-xl-tung-sing-exact-coplanar-terrain-census-20261010','government-xl-tung-sing-coplanar-boundary-census-20261010','government-xl-tung-sing-parent-coplanar-consolidation-20261010','government-xl-tung-sing-indexed-builder-equivalence-20261010','government-xl-tung-sing-whole-original-parent-domain-20261010','government-xl-tung-sing-whole-original-parent-domain-v2-20261010']
SCRIPTS=['native_parent_child_flat_composition_20261010.py','xl-tung-sing-flat-parent-child-census-20261010.py','exact_runtime_coplanar_groups_20261010.py','xl-tung-sing-exact-coplanar-terrain-census-20261010.py','exact_coplanar_boundary_census_20261010.py','xl-tung-sing-coplanar-boundary-census-20261010.py','exact_runtime_coplanar_consolidation_20261010.py','test_exact_runtime_coplanar_consolidation_20261010.py','xl-tung-sing-parent-coplanar-consolidation-20261010.py','parent_cell_clip_broad_phase_20261010.py','test_parent_cell_clip_broad_phase_20261010.py','indexed_original_parent_clip_builder_20261010.py','xl-tung-sing-indexed-builder-equivalence-20261010.py','xl-tung-sing-whole-original-parent-domain-20261010.py','xl-tung-sing-whole-original-parent-domain-v2-20261010.py']
def main():
 assert not DOC.exists();paths=[Path(__file__)]+[HERE/s for s in SCRIPTS];base=DOC.parent
 for n in NAMES:
  assert (base/n).exists(),n;paths +=[p for p in (base/n).rglob('*') if p.is_file()]
  for p in (base/n).rglob('*.json*'):
   x=read(p)
   for key in ['inputHashes','sourceHashes','hashes']:
    paths.extend(ROOT/q for q in x.get(key,{}) if (ROOT/q).is_file())
 proof=read(base/NAMES[3]/'complete-exact-surface-certificates.json.gz');paths.append(ROOT/proof['originalFile']);assert proof['outputFaces']==67610 and proof['allOriginalFacesAccounted'] and proof['allDegenerateOriginalsRetained'];paths.extend([HERE/'resolve-pass.py',HERE/'exact_original_projection_coverage_20261009.py',HERE.parent/'assembly-support-review/exact_tin.py'])
 (DOC/'README.md').parent.mkdir(parents=True,exist_ok=True);(DOC/'README.md').write_text('''# Exact scripted terrain representation recovery

The user explicitly approved “Allow exact scripted terrain consolidation”. Only terrain triangulation is involved; government building bytes, vertices, poses and elevations remain unchanged.

The original 89,785-face actual Float32 native Tung Yat parent surface is re-triangulated to 67,610 faces using only its original Float32 vertices. Every group uses unbounded integer oriented plane coefficients, full oriented manifold edge chains, a simple finite boundary, exact signed areas and exact ear triangulation. Unproved regions, holes, branches, overlapping edge records and all 23 original degenerate facets remain literal originals. Twelve meaningful tests and the complete actual surface/certificate/output replay passed independently with the root agent. This is surface equivalence, not a staged or accepted terrain composition.

The separate parent-cell broad-phase acceleration produced byte-identical complete make_patch outputs on two representative original-source/current-parent fixtures. The unchanged real validator passed the positive fixture and preserved the other fixture's coverage rejection and existing negative guards. Eight helper tests passed independently. No clipping threshold changed.

The initial flat composition is a historical negative: 114,622 faces exceeded the unchanged 100,000-facet budget and its old child seam differs from actual native parent height by up to 2.470661m. Its fragment helper drops tiny fragments by an absolute threshold and therefore cannot grant complete outside-surface equivalence. Whole-original-facet domains are read-only alternative feasibility records; their explicit nonmanifold/branch/raw coverage outcomes are preserved. No old child or initial clipping helper is accepted.

Current finite parent/child seam, complete outside retaining surfaces, current source support, all retained models, foreign actors, foundations, collision/runtime, staged/live browser and guarded publication remain mandatory. No live terrain was changed and no model was installed in this checkpoint.
''')
 spec=importlib.util.spec_from_file_location('tung_surface_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.freeze(BATCH,'user-authorized-exact-original-terrain-representation-diagnostics-v1',paths,{'uids':['landsd/53800:0','landsd/126434:0','landsd/163705:0'],'userAuthorization':'Allow exact scripted terrain consolidation','originalParentFacets':89785,'exactSurfaceEquivalentParentFacets':67610,'savedParentFacets':22175,'candidateTerrainTriangulationChanged':True,'actualRenderedTerrainSurfaceChanged':False,'liveTerrainChanged':False,'governmentBuildingGeometryChanged':False,'identityAccepted':False,'physicalAccepted':False,'scriptFullAcceptancePassed':False,'remainingReason':'actual-parent-child-surface-seam-and-complete-independent-current-physical-gates','nextStep':'Build a valid current single-native terrain composition using the proven exact consolidation; preserve complete actual outside surfaces and all ordinary physical/runtime/current actor checks.'});scope=set([str(DOC.relative_to(ROOT))]+[str((base/n).relative_to(ROOT)) for n in NAMES]+[str(p.relative_to(ROOT)) for p in paths]);Path('/tmp/xl-tung-sing-exact-terrain-representation-closed-scope-20261010.json').write_text(json.dumps(sorted(scope),indent=2)+'\n');print({'jobId':r['jobId'],'closedPaths':len(scope)},flush=True)
if __name__=='__main__':main()
