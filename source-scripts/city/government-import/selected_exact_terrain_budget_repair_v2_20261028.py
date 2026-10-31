"""Recover a terrain-budget failure by authorised exact render-equivalent consolidation."""
import argparse,copy,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from constant_colour_terrain_consolidation_v1 import consolidate_patch
from float32_coverage import approve_roundoff

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','terrain']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';old=base/a.terrain;doc=base/a.batch;local=HERE/'local'/a.batch;assert not doc.exists()and not local.exists()
 r,pins=authenticate(old);assert r['reason']=='terrain-runtime-budget'and not r['installationApproved'];source=old/'unapproved-terrain.json';scope=old/'scope.json'
 for p in [source,scope]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 patch=read(source);bounds=read(scope)['bounds'];assert set(patch['meta']['targetUids'])==set(r['uids'])|set(r.get('retainedNativeTerrainTargets',[]));before=copy.deepcopy(patch);refs=[Path(__file__),old/'result.json',source,scope]
 faces,proof=consolidate_patch(patch);doc.mkdir();save(doc/'exact-consolidation-certificate.json.gz',proof)
 patch['nativeMesh']['position']=faces.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(faces.size//3));patch['nativeMesh'].pop('sourceOverlap',None)
 for key in ['numericalCoverageGap','numericalProjectionOverlap']:patch['nativeMesh']['source'].pop(key,None)
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 patch['nativeMesh']['source']['exactRenderedTerrainConsolidation']=dict(source=ref(source),certificate=ref(doc/'exact-consolidation-certificate.json.gz'),sourceBuildingGeometryChanged=False,constantColourFieldsPreserved=True,flatNormalsPreserved=True)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';assert digest(parentpath.read_bytes())==pins[str(parentpath.relative_to(ROOT))];parent=read(parentpath);builder=module('budget_repair_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');error=None
 try:
  save(doc/'numerical-coverage.json',approve_roundoff(patch,bounds))
  overlap=module('budget_repair_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc;overlap.overlap_proof(patch,[source,doc/'exact-consolidation-certificate.json.gz',Path(__file__)])
  builder.validate_patch(patch,parent)
  assert len(faces)<=25000,'terrain-runtime-budget'
 except Exception as exc:error=dict(errorType=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(doc/'failure.json',error)
 out=local/'candidate-terrain.json';save(out,patch);save(doc/'scope.json',read(scope))
 result=dict(uids=r['uids'],status='private-terrain-validator-passed'if error is None else'exact-terrain-budget-investigation',candidate=ref(out),originalTerrainFaces=proof['originalFaces'],terrainTriangles=proof['outputFaces'],savedTerrainFaces=proof['savedFaces'],sourceBuildingMeshesUsed=False,sourceSHA256ByUid=r['sourceSHA256ByUid'],replacedNativeTerrain=r.get('replacedNativeTerrain',[]),retainedNativeTerrainTargets=r.get('retainedNativeTerrainTargets',[]),terrainTriangulationChanged=True,sourceGeometryChanges=0,installationApproved=False,publication=False,newlyInstalled=0,scriptExternalAICalls=0,error=error,qualification='Exact rendered Float32 terrain plane/area/edge certificates, constant vertex-colour fields and flat normals retained. No original building mesh changes, simplification error, optimisation registration or approval transfer; runtime/current-neighbour/browser checks remain.')
 save(doc/'summary.json',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([out,parentpath,HERE/'constant_colour_terrain_consolidation_v1.py',HERE/'exact_runtime_coplanar_consolidation_20261010.py',HERE/'exact_coplanar_boundary_census_20261010.py',HERE/'exact_runtime_coplanar_groups_20261010.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'float32_coverage.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
 module('exact_budget_repair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-colour-preserving-original-terrain-budget-recovery',list(set(refs)),result)
 print(dict(uids=r['uids'],status=result['status'],before=proof['originalFaces'],after=len(faces),saved=proof['savedFaces'],error=error),flush=True)
if __name__=='__main__':main()
