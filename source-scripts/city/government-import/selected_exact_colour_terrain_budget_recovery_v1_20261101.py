"""Recover an over-budget PRIVATE terrain candidate with exact existing methods.

Building assets are never inputs. All source, physical, neighbour, browser and
publication checks remain separate. Existing triangle budget is unchanged.
"""
import argparse,copy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from constant_colour_terrain_consolidation_v1 import consolidate_patch
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','prior','lease-file']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 lease=read(Path(a.lease_file));assert reservations.owns(lease)
 receipt,pins=authenticate(BASE/a.prior);assert receipt['reason']=='terrain-runtime-budget'and not receipt['installationApproved']and not receipt['publication']
 assert {'building:'+u for u in receipt['uids']}|{'terrain:city/data/terrain.json'}<=set(lease['resources'])
 doc=BASE/a.batch;local=HERE/'local'/a.batch;assert not doc.exists()and not local.exists();refs=[Path(__file__),BASE/a.prior/'result.json']
 def take(name):
  path=BASE/a.prior/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 patch=take('unapproved-terrain.json');context=take('terrain-source-context.json');scope=take('scope.json');low=take('unchanged-low-parent-proof.json')
 # Existing exact low-parent multiplicity obligations must not be retriangulated.
 assert low['unchangedLowParentFaces']==0,'This adapter requires a separate low-parent-preserving route'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==context['currentRendererManifestSHA256'];refs.append(manifest)
 output,proof=consolidate_patch(patch)
 assert proof['allOriginalFacesAccounted']and proof['mixedColourFacesRetainedUnchanged']and proof['flatNormalsAndFinitePlaneSurfacesPreserved']and proof['sourceVerticesOnly']
 assert len(output)<=25000 and np.isfinite(output).all()and output[:,:,1].min()>=1.2
 candidate=copy.deepcopy(patch);candidate['nativeMesh']['position']=output.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(output.size//3));candidate['nativeMesh'].pop('sourceOverlap',None)
 candidate['nativeMesh'].get('source',{}).pop('numericalCoverageGap',None)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';assert digest(parentpath.read_bytes())==patch['meta']['parentSha256'];refs.append(parentpath);parent=read(parentpath)
 helper=module('exact_colour_budget_existing_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bounds=helper.extent(candidate['coarseCells'],parent);assert bounds==scope['bounds']
 from native_patch_resolution import projected_context
 from float32_coverage import approve_roundoff
 _,polygons,_,_=projected_context(candidate,bounds)
 if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(doc/'numerical-coverage.json',approve_roundoff(candidate,bounds))
 overlap=module('exact_colour_budget_existing_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc;overlap.overlap_proof(candidate,refs)
 helper.validate_patch(candidate,parent)
 assert reservations.owns(lease)and digest(manifest.read_bytes())==context['currentRendererManifestSHA256']
 path=local/'candidate-terrain.json';save(path,candidate);refs.append(path);save(doc/'exact-colour-surface-proof.json.gz',proof);save(doc/'scope.json',scope);save(doc/'terrain-source-context.json',context)
 result=dict(uids=receipt['uids'],sourceSHA256ByUid=receipt['sourceSHA256ByUid'],status='private-terrain-validator-passed',candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),terrainTriangles=len(output),originalTerrainFaces=proof['originalFaces'],savedTerrainFaces=proof['savedFaces'],replacedNativeTerrain=receipt['replacedNativeTerrain'],retainedNativeTerrainTargets=receipt['retainedNativeTerrainTargets'],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification=proof['qualification'])
 save(doc/'summary.json',result)
 for name in ['constant_colour_terrain_consolidation_v1.py','exact_runtime_coplanar_consolidation_20261010.py','exact_runtime_coplanar_groups_20261010.py','exact_coplanar_boundary_census_20261010.py','resolve_pass_indexed_parent_clipping_v2.py','native_patch_resolution.py','float32_coverage.py','sham_shui_po_pool_shared_terrain_v2_20261016.py']:refs.append(HERE/name)
 module('exact_colour_budget_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-exact-constant-colour-terrain-budget-recovery',refs,result);print(result,flush=True)
if __name__=='__main__':main()
