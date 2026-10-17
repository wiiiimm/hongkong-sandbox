"""Unpublished terrain proposal preserving two separate current basic actors.

The pavilion and Jubilee College are independent sources, not mandatory Man
Fuk support. Keep their current terrain under their complete current footprints
and a one metre margin, then require every candidate/current physical gate.
No government model geometry or current actor is altered or omitted.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as patches
from rendered_patch_sampler import RenderedPatchSampler

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-man-fuk-ten-two-basic-parent-preservation-proposal-v1-20261010'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-man-fuk-twelve-original-coupled-physical-v2-20261010'
SEPARATE={'landsd/89100:0','landsd/98139:0'}
TERRAIN_SHA='ffa22a005631b7d9623202ddd33d32355535a65b979944c18dbe1fc8a4923d99'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert not DOC.exists() and not LOCAL.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
    selected=read(PRIOR/'selection.json.gz');assert selected['manifestSHA256']==start['sha256']
    candidate=read(PRIOR/'terrain-candidates.json')[0]
    path=ROOT/candidate['path'];assert ref(path)['sha256']==candidate['sha256']==TERRAIN_SHA
    patch=read(path);old_ref=candidate['replaces'];old_path=ROOT/'3d-viewer'/old_ref['url']
    assert ref(old_path)['sha256']==old_ref['sha256']
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
    assert any(r['url']==old_ref['url'] for r in read(manifest)['terrainPatches'])
    final=module('man_fuk_preserve_two_current_forms','xl-final-script-pass.py')
    forms=final.load_forms(candidate['bounds']);by_uid={f['uid']:(f,t) for f,_,t in forms}
    assert SEPARATE<=set(by_uid)
    own=[];source_refs=[]
    for row in selected['rows']:
        asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']
        source_refs.append(ref(asset))
        if row['uid'] not in SEPARATE:own.append(decode_original_world_triangles(asset.read_bytes()))
    assert len(own)==10
    own_projection=shapely.union_all(shapely.polygons(np.concatenate(own)[:,:,[0,2]]))
    regions=[];actors=[]
    for uid in sorted(SEPARATE):
        f,t=by_uid[uid];row=next(r for r in selected['rows'] if r['uid']==uid)
        assert f==row['source']['building']
        assert ref(ROOT/'3d-viewer'/t)['sha256']==row['source']['tileSHA256']
        region=shapely.Polygon(f['rings'][0],f['rings'][1:]).buffer(1,join_style='mitre')
        assert region.intersection(own_projection).area==0,'Preservation region intersects another candidate source; investigate separately'
        regions.append(region);actors.append(dict(uid=uid,currentSource=f,tile=ref(ROOT/'3d-viewer'/t),protectedRegionGeoJSON=shapely.to_geojson(region)))
    protected=shapely.union_all(regions)
    second=module('man_fuk_preserve_two_terrain_sampler','xl-second-pass.py')
    fallback=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    old=read(old_path)
    sampler=RenderedPatchSampler(old,fallback,second.resolution.terrain.fine.DemSampler(old,rendered=True))
    before=patches._faces(patch)
    nonheight=before[np.cross(before[:,1]-before[:,0],before[:,2]-before[:,0])[:,1]==0]
    proof=patches.preserve_parent_under_projection(patch,candidate['bounds'],protected,sampler,edge_sampler=fallback)
    after=patches._faces(patch)
    after_records={tuple(t.reshape(-1)) for t in after}
    assert all(tuple(t.reshape(-1)) in after_records for t in nonheight),'Original non-height terrain face changed'
    assert len(after)<100000
    output=LOCAL/'government-native-266062-0.json';save(output,patch)
    save(DOC/'terrain-candidates.json',[{**candidate,'path':str(output.relative_to(ROOT)),'sha256':ref(output)['sha256']}])
    diagnostic=dict(actors=actors,completeTenOriginalFaces=sum(len(t) for t in own),
        protectedProjectionM2=float(protected.area),candidateSourceProjectionIntersectionM2=0.0,
        literalOriginalNonheightTerrainFacesPreserved=len(nonheight),
        oldTerrain=ref(old_path),priorCandidateTerrain=ref(path),proposedTerrain=ref(output),
        completeCandidateTerrainFaces=len(after),parentPlanePreservation=proof,
        modelGeometryChanges=0,foreignActorsRemoved=False,currentAcceptancePassed=False,
        publication=False,qualification='Candidate only; existing clipped parent planes under two independent basic actors. Full actual source/runtime/terrain/neighbour/support/facet/identity gates must be repeated. No sampled plane equivalence or support credit.')
    save(DOC/'diagnostic.json',diagnostic)
    assert ref(manifest)==start
    refs=[Path(__file__),manifest,path,old_path,parent_path,output,PRIOR/'selection.json.gz',
          HERE/'native_patch_resolution.py',HERE/'rendered_patch_sampler.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']
    refs.extend(ROOT/r['path'] for r in source_refs)
    refs.extend(ROOT/a['tile']['path'] for a in actors)
    module('man_fuk_two_parent_proposal_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'ten-original-source-two-independent-basic-parent-plane-preservation-proposal-v1',refs,
        {**diagnostic,'uids':sorted(r['uid'] for r in selected['rows'] if r['uid'] not in SEPARATE),
         'manifestSHA256':start['sha256'],'humanStatus':'held-for-compute','humanDecisionRequired':False,'aiGeometryModellingRequired':False})
    print(dict(proposal=True,triangles=len(after),completeTenOriginalFaces=diagnostic['completeTenOriginalFaces'],publication=False),flush=True)

if __name__=='__main__':main()
