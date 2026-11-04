"""Build two private adjacent source-TIN insets without waiving publication guards."""
from pathlib import Path
import copy,traceback
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from bounded_original_inset_faces_v1_20261023 import inset_faces
from retained_native_template_v3_20261023 import verify_existing_low_faces,exact_rendered_face_multiset
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-paired-inset-diagnostic-v1-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists()
    refs=[Path(__file__)]
    def bound(batch):
        _,pins=authenticate(base/batch);refs.append(base/batch/'result.json');return pins
    capture='government-xl-island-industrial-three-original-current-capture-v1-20261023';cp=bound(capture)
    terrain_check='government-xl-island-industrial-three-original-terrain-check-v1-20261023';tp=bound(terrain_check)
    extension='government-xl-island-industrial-boundary-extension-context-v1-20261023';ep=bound(extension)
    def take(path,pins):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows=take(base/capture/'selection.json.gz',cp)['rows'];assert {r['uid']for r in rows}=={'landsd/20270:0','landsd/159422:0','landsd/269430:0'}
    geometry=take(HERE/'local'/capture/'runtime-geometry.json.gz',cp)['rows'];source=[]
    for row in rows:
        g=next(r for r in geometry if r['uid']==row['uid']);assert g['sourceSHA256']==row['sourceSHA256']
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
        source.append(np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for tri in source for f in tri])
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath,cp);manifest=ROOT/'3d-viewer/city/data/manifest.json';take(manifest,cp)
    southpath=ROOT/'3d-viewer/city/data/government-native-225173-0.json';northpath=ROOT/'3d-viewer/city/data/government-native-fu-tor-loy-original-v1-20261023.json'
    south=take(southpath,cp);north=take(northpath,cp)
    ext=take(HERE/'local'/extension/'parent.json',ep)
    for name,sha in ext['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    southfaces=np.asarray(ext['triangles']);v=np.asarray(north['nativeMesh']['position']).reshape(-1,3);northfaces=v[np.asarray(north['nativeMesh']['index']).reshape(-1,3)]
    v=np.asarray(south['nativeMesh']['position']).reshape(-1,3);originalsouth=v[np.asarray(south['nativeMesh']['index']).reshape(-1,3)]
    assert len(southfaces)==len(originalsouth)+8==32118
    expected=take(base/extension/'summary.json',ep);assert expected['exactOriginalFaces']['retainedNativeFaceMultisetPreserved']and expected['missingAreaInExtensionM2']==0
    from retained_rendered_union_template_v1_20261023 import verify_retained_faces
    builder=module('paired_inset_builder',HERE/'validated_parent_roundoff_template_v2.py')
    verify_retained_faces(southfaces,[originalsouth],shapely.box(*expected['bounds']))
    baseline=np.concatenate([southfaces,northfaces]);split=len(southfaces)
    checks=take(base/terrain_check/'summary.json',tp)['rows'];assert {r['uid']for r in checks}=={r['uid']for r in rows}
    paths={tuple(r['sourceTerrainPaths'])for r in checks};assert len(paths)==1
    decoder=module('paired_source_tin',HERE/'xl-second-pass.py');decoder.LOCAL=local;terrain=[];terrainrefs=[]
    for name in next(iter(paths)):
        path=ROOT/name;gltf=take(path,tp)
        for b in gltf.get('buffers',[]):take(path.parent/b['uri'],tp)if (path.parent/b['uri']).suffix=='.json'else refs.append(path.parent/b['uri'])
        for b in gltf.get('buffers',[]):assert digest((path.parent/b['uri']).read_bytes())==tp[str((path.parent/b['uri']).relative_to(ROOT))]
        terrain.append(decoder.terrain_triangles(path));terrainrefs.append(dict(path=name,sha256=digest(path.read_bytes())))
    combined_domain=shapely.union_all([shapely.box(*expected['bounds']),shapely.box(*builder.extent(north['coarseCells'],parent))])
    outer=projection.buffer(1,join_style='mitre').buffer(3,join_style='mitre')
    assert combined_domain.covers(outer)and outer.distance(combined_domain.boundary)>0
    print(dict(currentFaces=len(baseline),sourceFaces=sum(map(len,source)),projectionAreaM2=projection.area),flush=True)
    generated=inset_faces(baseline,np.concatenate(terrain),projection)
    save(out/'unchanged-low-faces.json',verify_existing_low_faces(baseline,generated['output'],generated['lineage'],outer))
    # Extend regular metadata by precisely one already-rendered parent column.
    south=copy.deepcopy(south);oldw=south['w'];neww=oldw+14;assert south['cell']==5
    sample=builder.terrain.fine.DemSampler(parent,rendered=True);rawsample=builder.terrain.fine.DemSampler(parent);pg=parent['meta']['georef'];sg=south['meta']['georef']
    oldarrays={k:south[k]for k in ['elev','vegetation','renderedElev']if k in south};newarrays={k:[]for k in oldarrays}
    for r in range(south['h']):
        for key,values in oldarrays.items():newarrays[key].extend(values[r*oldw:(r+1)*oldw])
        z=816500-sg['bN']-r*sg['aN']
        for c in range(oldw,neww):
            x=sg['bE']+c*sg['aE']-834500;before=rawsample.ground(x,z);after=sample.ground(x,z)
            newarrays['elev'].append(float(before)if before<=0 or after<=0 else float(after))
            if 'renderedElev'in newarrays:newarrays['renderedElev'].append(float(after))
            pc=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/pg['aE'])));pr=min(parent['h']-1,max(0,round((816500-z-pg['bN'])/pg['aN'])))
            newarrays['vegetation'].append(parent['vegetation'][pr*parent['w']+pc])
    south.update(newarrays);south['w']=neww;south['meta']['georef']['W']=neww;south['coarseCells']=expected['coarseCells']
    templates=[south,copy.deepcopy(north)];parts=[];memberreports=[]
    for which,template in enumerate(templates):
        selected=[i for i,line in enumerate(generated['lineage'])if(line['parentFace']<split)==(which==0)]
        faces=generated['output'][selected];parts.append(faces)
        template['nativeMesh']['position']=faces.reshape(-1).tolist();template['nativeMesh']['index']=list(range(faces.size//3));template['nativeMesh'].pop('sourceOverlap',None)
        template['nativeMesh']['source'].pop('numericalCoverageGap',None)
        template['meta']['targetUids']=sorted(set(template['meta']['targetUids'])|{r['uid']for r in rows})
        for meta in [template['meta']['source'],template['nativeMesh']['source']]:meta['pairedInsetDiagnostic']=dict(originalTerrain=terrainrefs,coreWKT=generated['core'].wkt,outerWKT=outer.wkt,publicationApproved=False)
        label=['south','north'][which];bounds=builder.extent(template['coarseCells'],parent)
        from float32_coverage import approve_roundoff
        from native_patch_resolution import projected_context
        _,polygons,_,_=projected_context(template,bounds)
        if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(out/(label+'-roundoff.json'),approve_roundoff(template,bounds))
        proof=module('paired_overlap_'+label,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=out/(label+'-overlap');proof.DOC.mkdir()
        proof.overlap_proof(template,[southpath,northpath,HERE/'local'/extension/'parent.json',Path(__file__)])
        path=local/(label+'-candidate.json');save(path,template);refs.append(path)
        error=None
        try:builder.validate_patch(template,parent)
        except AssertionError as e:error=str(e)
        memberreports.append(dict(member=label,candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),faces=len(faces),ordinaryValidatorPassed=error is None,ordinaryValidatorFailure=error))
        print(memberreports[-1],flush=True)
    shared=shapely.LineString([(-27.5,-4027.5),(462.5,-4027.5)]);edited=shared.intersection(outer);seams=[]
    for line in shapely.get_parts(edited):
        assert line.geom_type=='LineString'and line.length>0
        left,right=sorted([p[0]for p in line.coords]);curves=[seam_segments(t,2,-4027.5,left,right)for t in parts]
        seams.append(dict(range=[left,right],report=seam_comparison_report(*curves,left,right)))
    save(out/'lineage.json.gz',dict(changedParentFaces=generated['changedParentFaces'],outputLineage=generated['lineage'],highestOriginalFaces=generated['highestOriginalFaces'].tolist(),coreWKT=generated['core'].wkt,outerWKT=outer.wkt,removedAreaM2=generated['removedAreaM2'],insertedAreaM2=generated['insertedAreaM2']))
    result=dict(uids=[r['uid']for r in rows],members=memberreports,editedSeams=seams,sourceGeometryChanges=0,installationApproved=False,status='paired-boundary-contract-investigation',qualification='Private two-envelope candidate and complete local finite-seam measurements only. Existing ordinary validators remain authoritative; no coordinated-boundary exception exists in production. Full original identity/support/fourworld/native/base/runtime/browser and publication review remain required.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['bounded_original_inset_faces_v1_20261023.py','coordinated_native_boundary_v1_20261023.py','retained_native_template_v3_20261023.py','retained_rendered_union_template_v1_20261023.py','validated_parent_roundoff_template_v2.py','float32_coverage.py','native_patch_resolution.py','sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    module('paired_inset_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-paired-original-terrain-inset-diagnostic',refs,result)
    print(dict(editedSeams=seams,installationApproved=False),flush=True)


if __name__=='__main__':main()
