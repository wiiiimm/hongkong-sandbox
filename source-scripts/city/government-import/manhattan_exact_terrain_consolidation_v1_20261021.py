"""Exact runtime terrain-only consolidation, no acceptance or publication."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_runtime_coplanar_consolidation_20261010 import consolidate
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-exact-terrain-consolidation-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=BASE/'government-xl-manhattan-regional-ground-v1-20261021'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']};p=HERE/'local'/PRIOR.name/'diagnostic-height-surfaces.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);tri=np.asarray(read(p)['triangles'])
 output,proof=consolidate(tri);assert proof['allOriginalFacesAccounted']and proof['allDegenerateOriginalsRetained']
 proof.update(inputPath=str(p.relative_to(ROOT)),inputSHA256=digest(p.read_bytes()),inputRuntimeFacesSHA256=digest(tri.astype('<f4').astype('<f8').tobytes()),outputFacesSHA256=digest(output.astype('<f8').tobytes()))
 save(DOC/'exact-certificates.json.gz',proof);out=LOCAL/'consolidated-terrain-faces.json.gz';save(out,dict(position=output.reshape(-1).tolist(),index=list(range(output.size//3)),accepted=False));refs.append(out)
 for name in ['exact_runtime_coplanar_consolidation_20261010.py','exact_coplanar_boundary_census_20261010.py','exact_runtime_coplanar_groups_20261010.py']:refs.append(HERE/name)
 summary=dict(uids=['landsd/276331:0'],originalFaces=proof['originalFaces'],outputFaces=proof['outputFaces'],savedFaces=proof['savedFaces'],withinExistingTriangleBudget=proof['outputFaces']<=25000,allOriginalFacesAccounted=True,sourceGeometryChanges=0,terrainPublished=False,installationApproved=False)
 save(DOC/'summary.json',summary);module('ascot_exact_consolidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-runtime-terrain-surface-consolidation-diagnostic',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
