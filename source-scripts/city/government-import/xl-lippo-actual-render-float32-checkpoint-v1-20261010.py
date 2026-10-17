"""Freeze actual render attribute/F32 checks; no current identity promotion."""
from pathlib import Path
import importlib.util,json,subprocess,sys
from run import ROOT,HERE,read,save,digest
from lippo_current_bound_six_roof_identity_v1_20261010 import DOC as INPUT
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lippo_actual_render_float32_diagnostic_20261010 import verify
BATCH='government-xl-lippo-actual-render-attributes-and-float32-world-diagnostic-v1-20261010';DOC=INPUT.parent/BATCH
def main():
 assert not (DOC/'result.json').exists()
 export=read(DOC/'actual-render-attribute-geometry.json.gz');pins=export['inputHashes']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 rows=read(INPUT/'selection.json.gz')['rows'];originals={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows}
 literal=read(INPUT/'literal-production-geometry.json.gz');capture=read(INPUT/'current-inputs.json.gz');primary=read(INPUT/'exact-current-primary.json')['features']
 result=verify(export,literal,originals,capture['forms'],primary)
 result.update(historicalManifestSHA256=capture['manifestSHA256'],historicalCurrentCatalogueBindingOnly=True,currentRegionalRebindRequired=True,completeSourceFaces=29580,completeCurrentForms=12)
 save(DOC/'diagnostic.json.gz',result)
 with (DOC/'test-result.txt').open('w') as f:subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_lippo_actual_render_float32_diagnostic_20261010.py'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
 refs=[Path(__file__),HERE/'lippo_actual_render_float32_diagnostic_20261010.py',HERE/'test_lippo_actual_render_float32_diagnostic_20261010.py',HERE/'lippo_current_bound_six_roof_identity_v1_20261010.py',HERE/'lippo_three_original_current_inventory_20261010.py',HERE/'lippo_original_six_roof_current_scope_proposal_v2_20261010.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',INPUT/'result.json',INPUT/'literal-production-geometry.json.gz',INPUT/'selection.json.gz',INPUT/'current-inputs.json.gz',INPUT/'exact-current-primary.json']
 refs += [ROOT/p for p in pins]
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 sp=importlib.util.spec_from_file_location('lippo_render_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-actual-render-attribute-f32-source-only-checkpoint-v1',refs,dict(uids=sorted(originals),completeSourceFaces=29580,completeCurrentForms=12,completeF32Representations=2,testsPassed=20,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,currentRegionalRebindRequired=True,qualification=result['qualification']))
 print(json.dumps(dict(jobId=receipt['jobId'],sourceOnly=True,testsPassed=20)),flush=True)
if __name__=='__main__':main()
