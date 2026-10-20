"""Validate unchanged shaped terrain using the existing numerical coverage policy."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-terrain-validation-v3-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SOURCE=BASE/'government-xl-plaza-ascot-shaped-terrain-v4-20261020'
def main():
 assert not DOC.exists()
 receipt=read(SOURCE/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[Path(__file__),SOURCE/'result.json']
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 row=read(SOURCE/'terrain-candidates.json')[0];patch=read(ROOT/row['path']);before=geometry_sha(patch)
 proof=approve_roundoff(patch,row['bounds']);save(DOC/'numerical-coverage.json',proof)
 builder=module('ascot_final_terrain_validator',HERE/'resolve-pass-indexed-parent-clipping.py');parent=ROOT/'3d-viewer/city/data/terrain.json'
 patch['nativeMesh'].pop('sourceOverlap',None)
 overlap=module('ascot_coverage_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(patch,[ROOT/row['path'],Path(__file__),HERE/'float32_coverage.py'])
 builder.validate_patch(patch,read(parent));assert geometry_sha(patch)==before
 out=LOCAL/'candidate-terrain.json';save(out,patch);save(DOC/'terrain-candidates.json',[dict(row,path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()))])
 summary=dict(uids=row['uids'],terrainValidationPassed=True,geometryUnchanged=True,triangles=row['triangles'],installationApproved=False,productionTerrainChanges=0)
 save(DOC/'summary.json',summary);refs.extend([out,parent,HERE/'float32_coverage.py'])
 module('ascot_validation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-policy-terrain-validation',list(dict.fromkeys(refs)),summary)
 print(summary,flush=True)
if __name__=='__main__':main()
