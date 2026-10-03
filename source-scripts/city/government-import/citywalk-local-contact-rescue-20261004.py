"""Test restoring accepted source TIN only beneath remaining failed source faces."""
import importlib.util
import shutil
import subprocess
import sys
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from rendered_patch_sampler import RenderedPatchSampler,clip_native_against_retained_facets,remove_coplanar_duplicates
spec=importlib.util.spec_from_file_location('resolution',HERE/'sol-hold-resolution-20261004.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);c=r.c


def run(fringe=.01):
    c.owns();patches=c.module('local_rescue_patches','native_patch_resolution.py')
    final=c.module('local_rescue_foundation','xl-final-script-pass.py')
    source=c.DOC/'citywalk';original=read(source/'result.json')
    protected=read(c.DOC/'citywalk-protected-options.json')['rows'][0]
    row=read(source/'selection.json.gz')['rows'][0];entry=row['candidate']['entry']
    final.s.LOCAL=c.LOCAL/'citywalk-checks'
    model=final.s.glb_triangles({**row['native']['model'],'sourceSHA256':entry['sha256'],
        'modelId':entry['modelId'],'triangles':entry['triangles'],'native':row['native']})
    inputs=[original['patchPath'],protected['candidatePatch']['path']]
    patches_in=[read(ROOT/p) for p in inputs]
    points=np.concatenate([model,model.mean(axis=1)[:,None,:]],axis=1)
    gaps=[]
    for patch in patches_in:
        faces=patches._faces(patch);polys=shapely.polygons(faces[:,:,[0,2]])
        valid=shapely.area(polys)>1e-10
        heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),faces[valid],shapely.STRtree(polys[valid])).reshape(-1,4)
        assert np.isfinite(heights).all();gaps.append(points[:,:,1]-heights)
    repair=(gaps[1]<-.5).any(axis=1)
    assert repair.any() and (gaps[0][repair]>=-.5).all()
    assert 0<fringe<=.02
    projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in model[repair]]).buffer(fringe,join_style='mitre')
    parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    edge=final.s.resolution.terrain.fine.DemSampler(parent,rendered=True);edge.parent_height_floor=1.2
    sampler=RenderedPatchSampler(patches_in[0],edge,final.s.resolution.terrain.fine.DemSampler(patches_in[0],rendered=True))
    candidate=patches_in[1];bounds=patches._patch_bounds(candidate)
    proof=patches.preserve_parent_under_projection(candidate,bounds,projection,sampler,edge_sampler=edge)
    proof['float32RetainedSeam']=clip_native_against_retained_facets(candidate,proof['parentTriangles'])
    proof['coplanarCleanup']=remove_coplanar_duplicates(candidate)
    folder=c.LOCAL/'citywalk-contact-rescue';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'government-native-134332-0.json';save(path,candidate)
    overlap=source/'native-overlap.json';evidence=c.DOC/'citywalk-contact-rescue-overlap.json'
    _,_,missing,excess=patches.projected_context(candidate,bounds)
    assert missing.area<=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3)
    if excess>protected['originalProjectedOverlapM2']+.25:
        save(c.DOC/'citywalk-contact-rescue-error.json',{'reason':'source-overlap-budget',
            'projectedOverlapM2':excess,'maximumM2':protected['originalProjectedOverlapM2']+.25,
            'projectionM2':projection.area,'boundaryFringeM':fringe,'sourceFacesRestored':np.flatnonzero(repair).tolist(),
            'preservation':proof,'publication':False})
        raise AssertionError(('source-overlap-budget',excess,protected['originalProjectedOverlapM2']+.25))
    candidate['nativeMesh']['source']['numericalCoverageGap']['measuredAreaM2']=missing.area
    candidate['nativeMesh'].pop('sourceOverlap',None)
    patches.approve_original_overlap(candidate,path,evidence,read(overlap)['source']['files'])
    candidate['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT))
    patches.finalize_overlap_evidence(candidate,evidence)
    c.module('local_rescue_validator','../island-detail-integration/publish.py').validate_patch(candidate,parent)
    save(path,candidate)
    foundation=final.foundation_context(model,patches._faces(candidate),shapely.Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]))
    save(c.DOC/'citywalk-contact-rescue-foundation.json',{'uid':row['uid'],'foundation':foundation,
        'sourceSHA256':entry['sha256'],'candidate':c.ref(path),'restoredSourceFaces':np.flatnonzero(repair).tolist(),
        'sourceProjectionM2':projection.area,'boundaryFringeM':fringe,'preservation':proof,'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False})
    doc=c.DOC/'citywalk-contact-rescue';shutil.copytree(source,doc,dirs_exist_ok=True)
    terrain=[{**read(source/'terrain-candidates.json')[0],**c.ref(path)}]
    terrain[0]['replaces']['retainedUids']=['landsd/305615:0','landsd/273839:0']
    save(doc/'terrain-candidates.json',terrain);neighbours=read(source/'neighbour-inputs.json.gz');neighbours['patches']=terrain
    save(doc/'neighbour-inputs.json.gz',neighbours)
    for args in (
        ['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((doc/'selection.json.gz').relative_to(ROOT)),
         '--candidates',str((c.LOCAL/'citywalk-checks/candidates').relative_to(ROOT)),'--terrain-candidates',str((doc/'terrain-candidates.json').relative_to(ROOT)),'--out',str((doc/'metrics.json').relative_to(ROOT))],
        ['node',str(HERE/'check-neighbours.mjs'),str(doc.relative_to(ROOT))+'/'],
        ['node',str(HERE/'check-native-neighbours.mjs'),str(doc.relative_to(ROOT))+'/']):
        subprocess.run(args,cwd=ROOT,check=True)
    print({'sourceFacesRestored':int(repair.sum()),'buriedUpward':foundation['fullyBuriedUpwardTriangles'],'maskM2':projection.area},flush=True)


if __name__=='__main__':run(float(sys.argv[1]) if len(sys.argv)>1 else .01)
