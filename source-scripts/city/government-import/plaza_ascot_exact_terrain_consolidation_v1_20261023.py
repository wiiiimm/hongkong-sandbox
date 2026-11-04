"""Measure exact terrain-only consolidation of Plaza Ascot's oversized private patch."""
from pathlib import Path
import copy
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_runtime_coplanar_consolidation_20261010 import consolidate


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-plaza-ascot-258411-exact-terrain-consolidation-v1-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists()
    prior='government-xl-rest-recovered-current-supervisor-v1-20261022-chunk-01-candidates-258411-0-terrain';receipt,pins=authenticate(base/prior)
    assert receipt['status']=='bounded-inset-investigation'and receipt['reason']=='terrain-runtime-budget'
    path=base/prior/'unapproved-terrain.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    patch=read(path);mesh=patch['nativeMesh'];original=np.asarray(mesh['position'],dtype=np.float32).astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
    assert len(original)==34961
    output,certificate=consolidate(original)
    assert certificate['allOriginalFacesAccounted']and certificate['allDegenerateOriginalsRetained']and certificate['outputFaces']==len(output)
    candidate=copy.deepcopy(patch);candidate['nativeMesh']['position']=output.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(output.size//3));candidate['nativeMesh'].pop('sourceOverlap',None)
    cp=local/'unapproved-terrain.json';save(cp,candidate);save(out/'exact-terrain-certificate.json.gz',certificate)
    result=dict(uids=['landsd/258411:0'],originalTerrainFaces=len(original),outputTerrainFaces=len(output),savedTerrainFaces=len(original)-len(output),withinExisting25000FaceBudget=len(output)<=25000,allOriginalTerrainSurfaceAccounted=True,sourceBuildingGeometryInputs=0,sourceGeometryChanges=0,installationApproved=False,publication=False,status='historical-private-terrain-exact-consolidation-feasibility',candidate=dict(path=str(cp.relative_to(ROOT)),sha256=digest(cp.read_bytes())),qualification='Only the historical terrain patch was input. Exact integer coplanar boundary/area/ear certificates preserve its finite surface with unchanged Float32 vertices; every unproved or degenerate region remains unchanged. Historical scene acceptance does not transfer: fresh current-source terrain construction, whole-source/world, parent, neighbour, identity and browser checks remain required.')
    save(out/'summary.json',result)
    refs=[Path(__file__),base/prior/'result.json',path,cp,HERE/'exact_runtime_coplanar_consolidation_20261010.py',HERE/'exact_coplanar_boundary_census_20261010.py']
    module('plaza_ascot_exact_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-historical-exact-terrain-consolidation-feasibility',refs,result)
    print({k:result[k]for k in ['originalTerrainFaces','outputTerrainFaces','savedTerrainFaces','withinExisting25000FaceBudget']},flush=True)

if __name__=='__main__':main()
