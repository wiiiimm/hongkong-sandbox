"""Exact all finite raw coverage witnesses in complete residual terrain trial."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from actual_native_parent_transition_v3_20261010 import height_facet_indices
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_slab_projection_coverage_20261010 import slab_coverage
BATCH='government-xl-tung-sing-residual-all-exact-source-coverage-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
RAW=DOC.parent/'government-xl-tung-sing-full-original-residual-candidate-context-20261010/diagnostic.json.gz';CAND=DOC.parent/'government-xl-tung-sing-parent-residual-gap-candidate-20261010/candidate-single-native-residual-surface.json';SELECT=DOC.parent/'government-xl-tung-sing-interior-current-identity-inputs-20261010/selection.json.gz'
assert not DOC.exists();g=faces(read(CAND));ground=g[height_facet_indices(g)];rows=[];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [RAW,CAND,SELECT,Path(__file__)]};selected={r['uid']:r for r in read(SELECT)['rows']}
for r in read(RAW)['rows']:
 row=selected[r['uid']];asset=ROOT/row['candidate']['path'];source=decode_original_world_triangles(asset.read_bytes());hashes[str(asset.relative_to(ROOT))]=digest(asset.read_bytes())
 for i in r['rawUncoveredFaces']:
  p=slab_coverage(source[i],ground);rows.append({'uid':r['uid'],'originalFace':i,'proof':p});print({'uid':r['uid'],'originalFace':i,'exactCovered':p['exactProjectionCovered']},flush=True)
save(DOC/'diagnostic.json.gz',{'rows':rows,'rawFiniteCoverageFlags':len(rows),'allExactlyCovered':all(r['proof']['exactProjectionCovered'] for r in rows),'completeCandidateFacets':len(g),'exactNonzeroGroundFacets':len(ground),'inputHashes':hashes,'physicalAccepted':False,'modelGeometryChanges':0,'qualification':'Full finite Fraction area/slab/closed-edge replays of EVERY raw missing face in the complete11,877face source-only residual candidate check. No sampled-point/epsilon coverage credit. Candidate widening is explicitly proposed; current foreign/native/support/runtime/publication gates stay independent.'});print({'rawFlags':len(rows),'exactCovered':sum(r['proof']['exactProjectionCovered'] for r in rows)},flush=True)
