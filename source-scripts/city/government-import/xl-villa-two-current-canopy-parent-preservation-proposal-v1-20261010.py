"""Candidate terrain retaining the two independent current canopy footprints.

Exact original sources remain unchanged; all projection overlaps stay explicit.
No unknown canopy height, common ownership or support/collision exemption.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as patches
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-villa-two-current-canopy-parent-preservation-proposal-v1-20261010'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-villa-five-original-coupled-physical-v1-20261010'
SEPARATE={'landsd/278808:0','landsd/325786:0'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not DOC.exists()and not LOCAL.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
 selected=read(PRIOR/'selection.json.gz');assert selected['manifestSHA256']==start['sha256']
 candidate=read(PRIOR/'terrain-candidates.json')[0];path=ROOT/candidate['path'];assert ref(path)['sha256']==candidate['sha256']
 patch=read(path);assert not candidate.get('replaces')
 parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
 final=module('villa_canopy_forms','xl-final-script-pass.py');forms=final.load_forms(candidate['bounds']);by_uid={f['uid']:(f,t)for f,_,t in forms};assert SEPARATE<=set(by_uid)
 original=[];source_refs=[]
 for row in selected['rows']:
  asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256'];source_refs.append(ref(asset));original.append(decode_original_world_triangles(asset.read_bytes()))
 assert len(original)==5
 projection=shapely.union_all(shapely.polygons(np.concatenate(original)[:,:,[0,2]]));regions=[];actors=[]
 for uid in sorted(SEPARATE):
  f,t=by_uid[uid];assert f['structureType']=='Open-sided Structure'and f['baseSource']=='terrain-estimated'and f['heightSource']=='estimated'
  footprint=shapely.Polygon(f['rings'][0],f['rings'][1:]);region=footprint.buffer(1,join_style='mitre');regions.append(region)
  actors.append(dict(uid=uid,currentSource=f,tile=ref(ROOT/'3d-viewer'/t),fullCurrentFootprint=shapely.to_geojson(footprint),protectedRegionGeoJSON=shapely.to_geojson(region),originalSourceProjectionOverlapM2=projection.intersection(footprint).area,protectedRegionOriginalProjectionOverlapM2=projection.intersection(region).area,estimatedProxyHeightsOnly=True))
 protected=shapely.union_all(regions)
 # Actual prior ground is the root grid only here; reject any installed patch,
 # including nested native terrain, rather than substituting its coarse grid.
 prior_patches=[]
 for entry in read(manifest)['terrainPatches']:
  p=ROOT/'3d-viewer'/entry['url'];terrain=read(p);g=terrain['meta']['georef'];x,z=g['bE']-834500,816500-g['bN'];extent=shapely.box(x,z,x+(terrain['w']-1)*g['aE'],z-(terrain['h']-1)*g['aN'])
  assert extent.intersection(protected).area==0,'Existing actual patch requires native parent binding'
  prior_patches.append(ref(p))
 second=module('villa_actual_root_grid','xl-second-pass.py');sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
 before=patches._faces(patch);nonheight=before[np.cross(before[:,1]-before[:,0],before[:,2]-before[:,0])[:,1]==0]
 proof=patches.preserve_parent_under_projection(patch,candidate['bounds'],protected,sampler,edge_sampler=sampler)
 after=patches._faces(patch);records={tuple(t.reshape(-1))for t in after};assert all(tuple(t.reshape(-1))in records for t in nonheight),'Original nonheight terrain record omitted'
 assert len(after)<100000
 output=LOCAL/'government-native-89917-0.json';save(output,patch)
 save(DOC/'terrain-candidates.json',[{**candidate,'path':str(output.relative_to(ROOT)),'sha256':ref(output)['sha256']}])
 diagnostic=dict(uids=selected['rows']and[r['uid']for r in selected['rows']],actors=actors,completeFiveOriginalFaces=sum(len(t)for t in original),protectedProjectionM2=protected.area,candidateSourceProtectedProjectionIntersectionM2=projection.intersection(protected).area,literalOriginalNonheightTerrainFacesPreserved=len(nonheight),priorCandidateTerrain=ref(path),proposedTerrain=ref(output),actualRootGrid=ref(parent_path),allExistingPatchBindings=prior_patches,completeCandidateTerrainFaces=len(after),parentPlanePreservation=proof,modelGeometryChanges=0,foreignActorsRemoved=False,currentAcceptancePassed=False,publication=False,qualification='Unpublished terrain proposal only. Full current canopy footprints and one metre margin retain prior root-grid surface, with source overlaps explicit. Rendered Float32 planes/domain/seams, every original/literal finite facet, component root, foundation, foreign/current/runtime/neighbour gate require fresh checks. Estimated canopy heights provide no surveyed silhouette, identity, ownership or support credit.')
 save(DOC/'diagnostic.json',diagnostic);assert ref(manifest)==start
 refs=[Path(__file__),manifest,path,parent_path,output,PRIOR/'selection.json.gz',PRIOR/'result.json',HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',*[ROOT/r['path']for r in source_refs],*[ROOT/a['tile']['path']for a in actors],*[ROOT/r['path']for r in prior_patches]]
 module('villa_canopy_candidate_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-source-two-current-canopy-parent-preservation-proposal-v1',refs,{**diagnostic,'manifestSHA256':start['sha256'],'humanStatus':'held-for-compute','humanDecisionRequired':False,'aiGeometryModellingRequired':False})
 print(dict(proposal=True,triangles=len(after),sourceProjectionProtectedOverlapM2=diagnostic['candidateSourceProtectedProjectionIntersectionM2'],publication=False),flush=True)
if __name__=='__main__':main()
