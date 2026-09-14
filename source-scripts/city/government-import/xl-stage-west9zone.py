"""Stage and validate the source-backed terrain candidate for WEST9ZONE."""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box
import native_patch_resolution as patch_resolution
spec=importlib.util.spec_from_file_location('xl_second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'terrain-west9zone',s.LOCAL/'terrain-west9zone-stage'
read,save,h,rel=s.read,s.save,s.h,s.rel
UID='landsd/229310:0'
IDENTITY_CENTROID_EXCEPTIONS={'landsd/147024:0':2}
IDENTITY_DETAILED_EXCEPTIONS={'landsd/31275:0'}
IDENTITY_COMPACT_OVERHANG_EXCEPTIONS={'landsd/147505:0'}
IDENTITY_ISOLATED_OVERHANG_EXCEPTIONS={'landsd/160193:0'}
IDENTITY_BOUNDARY_TOUCH_EXCEPTIONS={'landsd/177244:0'}
IDENTITY_SHARED_COMPLEX_OVERHANG_EXCEPTIONS={'landsd/264691:0'}
IDENTITY_COMPLEX_BOUNDARY_EXCEPTIONS={'landsd/240527:0'}
IDENTITY_DETACHED_COMPONENT_EXCEPTIONS={'landsd/57826:0'}
VALIDATION_CONTACT_EXCEPTIONS={'landsd/240527:0'}
PARENT_PRESERVATION_EXCEPTIONS={'landsd/147505:0':None,'landsd/177244:0':{'landsd/2670:0'},'landsd/264691:0':None,'landsd/240527:0':None}
NATIVE_TERRAIN_REPAIR_EXCEPTIONS={'landsd/50009:0'}
FULL_MESH_NEIGHBOUR_EXCEPTIONS={'landsd/177244:0','landsd/160193:0','landsd/264691:0'}

def start():
    selected=read(s.DOC/'runtime-selection.json.gz');r=next(r for r in selected['rows'] if r['uid']==UID);parent=read(ROOT/'3d-viewer/city/data/terrain.json');cells=s.resolution.rectangle_for(r['candidate']['entry']['worldBounds'],parent);bb=s.resolution.extent(cells,parent);region=box(*bb)
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];raw=p.read_bytes();touched=False
        for b in json.loads(raw)['buildings']:
            poly=Polygon(b['rings'][0],b['rings'][1:])
            if poly.intersects(region):neighbours.append({'building':b,'patchIndexes':[0],'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))});touched=True
        if touched:hashes[rel(p)]=s.digest(raw)
    current=h(ROOT/'3d-viewer/city/data/manifest.json');save(DOC/'selection.json.gz',{**selected,'manifestSHA256':current,'rows':[r]});save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':[UID],'patches':[]});save(DOC/'patch-plan.json',{'cells':cells,'bounds':bb,'manifestSHA256':current,'uid':UID})
    resources=set(read(s.LOCAL/'reservation.json')['resources'])|{('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:')+n['building']['uid'] for n in neighbours}
    owned=s.reservations.claim('codex-xl-west9zone-terrain-'+str(uuid.uuid4()),sorted(resources),batch=s.BATCH+'-terrain-west9zone');assert owned['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(owned['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'));plan=read(DOC/'patch-plan.json');assert h(ROOT/'3d-viewer/city/data/manifest.json')==plan['manifestSHA256']
    adjacent=read(s.DOC/'adjacent-terrain-results.json');assert adjacent['complete'];r=read(DOC/'selection.json.gz')['rows'][0]
    native_by_model={a['modelId']:a['native'] for a in read(s.DOC/'diagnostics.json')['rows']}
    native_by_model.update({a['modelId']:a['native'] for a in adjacent['rows']})
    native_check=native_by_model[r['native']['model']['modelId']]
    if UID in NATIVE_TERRAIN_REPAIR_EXCEPTIONS:
        assert not native_check['passed'] and native_check['reasons']==['native-source-below-grade']
        assert native_check['covered']==native_check['checks'] and native_check['gapRange'][0]<-.25
    else:assert native_check['passed']
    sources=read(s.DOC/'recovery.json')['sheets']+adjacent['sources'];bb=plan['bounds'];fragments=[];used=[];parent=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');replacement=plan.get('replaces');group={'uids':[UID,*(replacement or {}).get('retainedUids',[])],'cells':plan['cells']}
    try:
        overlapping=[entry for entry in manifest['terrainPatches'] if s.resolution.terrain.overlap(group['cells'],read(ROOT/'3d-viewer'/entry['url'])['coarseCells'])]
        if replacement:
            assert [entry['url'] for entry in overlapping]==[replacement['url']],'replacement-target-mismatch'
            assert h(ROOT/'3d-viewer'/replacement['url'])==replacement['sha256'],'replacement-source-changed'
        else:assert not overlapping,'overlaps-installed-terrain-patch'
        for source in sources:
            folder=s.LOCAL/'sheets'/source['sheet']/'terrain'
            for e in source['source']['entries']:
                if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):assert h(folder/e['name'])==e['sha256']
            found=[]
            for path in source['terrainPaths']:
                tri=s.terrain_triangles(ROOT/path);near=tri[(tri[:,:,0].max(axis=1)>=bb[0])&(tri[:,:,0].min(axis=1)<=bb[2])&(tri[:,:,2].max(axis=1)>=bb[1])&(tri[:,:,2].min(axis=1)<=bb[3])]
                if len(near):found.append(near)
            if found:
                fragments.extend(found);proof=source['source'];used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':rel(folder/e['name']),'sha256':e['sha256']} for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]})
        native=np.concatenate(fragments)
        low=native[:,:,1].min(axis=1)<1.2
        source_row=next(x for x in read(s.DOC/'selection.json.gz')['rows'] if x['uid']==UID)
        model_triangles=s.glb_triangles(source_row)
        model_projection=shapely.union_all(shapely.polygons(model_triangles[:,:,[0,2]]))
        low_projection=shapely.union_all(shapely.polygons(native[low][:,:,[0,2]])) if low.any() else shapely.GeometryCollection()
        assert low_projection.intersection(model_projection).area<1e-6,'water-clamped-source-terrain-intersects-model-projection'
        native=native[~low]
        validator=s.resolution.validate_patch;s.resolution.validate_patch=lambda candidate,parent_terrain:None
        core_rows=[r]
        if replacement:
            selected_rows=read(s.DOC/'runtime-selection.json.gz')['rows'];core_rows.extend(next(row for row in selected_rows if row['uid']==uid) for uid in replacement['retainedUids'])
        lows=[row['candidate']['entry']['worldBounds'][0] for row in core_rows];highs=[row['candidate']['entry']['worldBounds'][1] for row in core_rows]
        core=[min(lo[0] for lo in lows)-1,min(lo[2] for lo in lows)-1,max(hi[0] for hi in highs)+1,max(hi[2] for hi in highs)+1]
        try:patch=s.resolution.make_patch(group,parent,native,used,native_core=core)
        finally:s.resolution.validate_patch=validator
        path=LOCAL/(patch['id']+'.json');save(path,patch);patch=read(path)
        source_files=[item for source in used for item in source['sourceFiles']]
        projected_excess=patch_resolution.projected_context(patch,bb)[3]
        overlap=(patch_resolution.approve_original_overlap(patch,path,Path(rel(DOC/'native-overlap-evidence.json')),source_files)
                 if projected_excess>1e-8 else {'nativeProjectedExcessM2':projected_excess,'policy':'No overlapping source facets were present.'})
        sampler=s.resolution.terrain.fine.DemSampler(parent,rendered=True)
        fill=patch_resolution.fill_parent_only_holes(patch,parent,bb,model_projection,sampler)
        save(path,patch);patch=read(path)
        if patch['nativeMesh'].get('sourceOverlap'):
            patch_resolution.finalize_overlap_evidence(patch,DOC/'native-overlap-evidence.json');save(path,patch);patch=read(path)
        validator(patch,parent)
        save(DOC/'terrain-resolution.json',{'overlapProof':overlap,'waterClamp':{'droppedTriangles':int(low.sum()),'protectedIntersectionAreaM2':float(low_projection.intersection(model_projection).area),'parentHoleFill':fill},'aiCalls':0,'geometryChanges':0})
    except (AssertionError,ValueError) as error:
        save(DOC/'result.json',{'uid':UID,'passed':False,'stage':'source-terrain-patch','reason':type(error).__name__+': '+str(error),'aiCalls':0});print(json.dumps(read(DOC/'result.json')),flush=True);return
    patch_entry={'path':rel(path),'sha256':h(path),'uids':[UID],'bounds':bb,'triangles':len(patch['nativeMesh']['index'])//3}
    if replacement:patch_entry['replaces']=replacement
    save(DOC/'terrain-candidates.json',[patch_entry]);neighbours=read(DOC/'neighbour-inputs.json.gz');neighbours['patches']=[patch_entry];save(DOC/'neighbour-inputs.json.gz',neighbours)
    catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue['area']='Government XL original-source imports';catalogue['models']=[r['candidate']['entry']];catalogue['counts']['packedModels']=1;save(LOCAL/'candidates/catalogue.json',catalogue);save(LOCAL/'candidates/catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    asset=LOCAL/'candidates'/r['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes((s.LOCAL/r['candidate']['entry']['asset']).read_bytes());assert h(asset)==r['candidate']['entry']['sha256'];save(LOCAL/'source-forms.json',{UID:r['source']})
    s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
    v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert v.returncode in (0,1)
    s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    neighbour_report=read(DOC/'neighbour-checks.json');blocked=neighbour_report['patches'][0]['blockedBy'];support_resolved=[]
    if blocked:
        by_uid={n['building']['uid']:n['building'] for n in read(DOC/'neighbour-inputs.json.gz')['rows']}
        source_polygons=shapely.polygons(model_triangles[:,:,[0,2]]);valid=shapely.area(source_polygons)>1e-10;support_triangles=model_triangles[valid];source_polygons=source_polygons[valid];source_tree=shapely.STRtree(source_polygons)
        support_rows=[]
        for uid in blocked:
            building=by_uid[uid];foot=Polygon(building['rings'][0],building['rings'][1:]);bounds=np.asarray(building['rings'][0]).min(0),np.asarray(building['rings'][0]).max(0);lo,hi=bounds;step=max(2,float(np.sqrt((hi[0]-lo[0])*(hi[1]-lo[1])/2500)));points=np.array([[x,z] for x in np.arange(lo[0]+step/2,hi[0],step) for z in np.arange(lo[1]+step/2,hi[1],step) if foot.covers(shapely.Point(x,z))]);base=building['base']+building.get('minimum',0);heights=np.full(len(points),-np.inf)
            if len(points):
                pi,ti=source_tree.query(shapely.points(points),predicate='covered_by');abc=support_triangles[ti];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=points[pi]-abc[:,0,[0,2]];det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det;ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1]);ok=ys<=base+.1;np.maximum.at(heights,pi[ok],ys[ok])
            covered=np.isfinite(heights);gaps=base-heights;coverage=foot.intersection(model_projection).area/foot.area;passed=coverage>=.9999 and len(points)>0 and covered.sum()/len(points)>=.9 and np.abs(gaps[covered]).max()<=.1
            support_rows.append({'uid':uid,'supportUid':UID,'footprintCoverage':coverage,'interiorSamples':len(points),'covered':int(covered.sum()),'gapRangeM':[float(gaps[covered].min()),float(gaps[covered].max())] if covered.any() else None,'passed':bool(passed)})
            if passed:support_resolved.append(uid)
        save(DOC/'source-support.json',{'rows':support_rows,'resolved':sorted(support_resolved),'sourceSHA256':r['candidate']['entry']['sha256'],'policy':'Highest unchanged government source surface at or below >=90% of <=2m interior samples (boundary gaps permitted), >=99.99% footprint coverage, and <=0.1m support gap at every covered sample.','aiCalls':0})
        resolution=read(DOC/'terrain-resolution.json');resolution['sourceSupportSHA256']=h(DOC/'source-support.json');save(DOC/'terrain-resolution.json',resolution)
    remaining=set(blocked)-set(support_resolved)
    if remaining and UID in PARENT_PRESERVATION_EXCEPTIONS:
        by_uid={n['building']['uid']:n['building'] for n in read(DOC/'neighbour-inputs.json.gz')['rows']}
        configured=PARENT_PRESERVATION_EXCEPTIONS[UID]
        preserve_uids=remaining if configured is None else remaining&configured
        protected=shapely.union_all([Polygon(by_uid[uid]['rings'][0],by_uid[uid]['rings'][1:]) for uid in sorted(preserve_uids)])
        # A centimetre fringe keeps Float32 boundary samples on the retained
        # parent surface. The measured source-model clearance must remain larger.
        protected_with_fringe=protected.buffer(.01,join_style='mitre')
        assert protected_with_fringe.intersection(model_projection).area<1e-8,'neighbour-preservation-intersects-source-model'
        proof=patch_resolution.preserve_parent_under_projection(patch,bb,protected_with_fringe,sampler);proof['boundaryFringeM']=.01;proof['parentHoleFill']=patch_resolution.fill_parent_only_holes(patch,parent,bb,model_projection,sampler)
        if patch['nativeMesh'].get('sourceOverlap'):
            patch_resolution.finalize_overlap_evidence(patch,DOC/'native-overlap-evidence.json')
        s.resolution.validate_patch(patch,parent);save(path,patch);patch=read(path)
        resolution=read(DOC/'terrain-resolution.json');resolution['protectedNeighbourTerrain']={'uids':sorted(preserve_uids),**proof};save(DOC/'terrain-resolution.json',resolution)
        patch_entry.update(sha256=h(path),triangles=len(patch['nativeMesh']['index'])//3);save(DOC/'terrain-candidates.json',[patch_entry]);neighbours=read(DOC/'neighbour-inputs.json.gz');neighbours['patches']=[patch_entry];save(DOC/'neighbour-inputs.json.gz',neighbours)
        s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
        v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert v.returncode in (0,1)
        s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    native_resolved=[]
    if UID in FULL_MESH_NEIGHBOUR_EXCEPTIONS:
        s.call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
        native_resolved=read(DOC/'native-neighbour-checks.json')['resolved']
    spec=importlib.util.spec_from_file_location('acceptance',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json')['results'][0];acceptance_row={'state':'runtime-validated-awaiting-acceptance','sourceSHA256':r['candidate']['entry']['sha256']}
    if UID in IDENTITY_CENTROID_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'minimumOverlap':.999,'maximumCentroidDistance':IDENTITY_CENTROID_EXCEPTIONS[UID]}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'measured':metrics['rows'][0]['identity'],'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_DETAILED_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics']
        accepted=(final['identityScriptAccepted'] and identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.97 and identity['sourceProjectionInsideTarget']>.95 and identity['sourceExcessFraction']<.05 and identity['sourceExcessMaximumDistanceFromTargetM']<4 and identity['unrelatedIntersectingForms']==0 and projection['centroidDistance']<1)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'detailedProjectionAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_BOUNDARY_TOUCH_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        boundary_only=bool(adjacent) and len({form['parent'] for form in adjacent})==1 and all(form['fractionOfForm']<.005 and form['intersectionAreaM2']<7 for form in adjacent)
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.995 and identity['sourceExcessMaximumDistanceFromTargetM']<5.5 and projection['centroidDistance']<1.1 and boundary_only)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'boundaryTouchAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique source, accept >99.5% target coverage and <5.5m extension when all other intersections are <7m2 and <0.5% slivers of one adjacent building assembly. Adjacent fallbacks remain present.','adjacentBoundaryTouches':adjacent,'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_ISOLATED_OVERHANG_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.99 and identity['sourceExcessMaximumDistanceFromTargetM']<8 and identity['unrelatedIntersectingForms']==0 and projection['centroidDistance']<1.2 and not adjacent)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'isolatedOverhangAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique isolated source, accept a detailed projection that covers >99% of the simplified target, extends <8m, has <1.2m centroid offset, and intersects no other viewer form.','coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_COMPACT_OVERHANG_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        boundary_only=all(form['sameParent'] and form['fractionOfForm']<.1 and form['intersectionAreaM2']<5 for form in adjacent)
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.9999 and identity['sourceExcessMaximumDistanceFromTargetM']<3.5 and identity['unrelatedIntersectingForms']==0 and projection['centroidDistance']<.5 and boundary_only)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'compactOverhangAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique small-footprint source, accept a detailed projection that covers >99.99% of the target, extends <=3.5m, has <0.5m centroid offset, intersects no unrelated form, and only touches same-parent adjacent forms over <5m2 and <10% of their area.','adjacentBoundaryTouches':adjacent,'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_SHARED_COMPLEX_OVERHANG_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        shared_complex=bool(adjacent) and all(form['sharedOsmReference'] for form in adjacent)
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.9999 and identity['sourceExcessMaximumDistanceFromTargetM']<3.5 and identity['unrelatedIntersectingForms']==0 and projection['centroidDistance']<.6 and shared_complex)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'sharedComplexOverhangAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique source, accept a detailed projection that covers >99.99% of the target, extends <3.5m, has <0.6m centroid offset, intersects no unrelated form, and only overlaps forms sharing its mapped complex reference.','sharedComplexForms':adjacent,'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_COMPLEX_BOUNDARY_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        bounded=bool(adjacent) and all(form['intersectionAreaM2']<15 and form['fractionOfForm']<.1 for form in adjacent)
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.99 and identity['sourceExcessMaximumDistanceFromTargetM']<9 and projection['centroidDistance']<1 and bounded)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'complexBoundaryAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique complex source, accept >99% target coverage, <9m extension and <1m centroid offset when every adjacent-form intersection is <15m2 and <10% of that form. Adjacent fallbacks remain present.','adjacentBoundaryTouches':adjacent,'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    if UID in IDENTITY_DETACHED_COMPONENT_EXCEPTIONS:
        entry=r['candidate']['entry'];building=r['source']['building'];matches=r['native']['model']['matching']['viewerMatches'];final_path=s.DOC/'final-script-pass/results.json.gz';diagnostic_path=s.DOC/'diagnostics.json';final=next(row for row in read(final_path)['rows'] if row['uid']==UID);diagnostic=next(row for row in read(diagnostic_path)['rows'] if row['uid']==UID);identity=final['identity'];projection=next(row for row in diagnostic['projectionCandidates'] if row['uid']==UID)['metrics'];adjacent=[form for form in identity['intersectingForms'] if form['uid']!=UID]
        detached=bool(adjacent) and all(form['intersectionAreaM2']<6 and form['fractionOfForm']>.99 for form in adjacent) and identity['sourceExcessCoveredByUnrelatedFormsM2']<1e-6
        accepted=(identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.99 and identity['sourceExcessMaximumDistanceFromTargetM']<11 and projection['centroidDistance']<.25 and detached)
        acceptance_row['identityProof']={'exactObjectId':entry['objectId']==building['objectId'],'exactBuildingCSUID':entry['buildingCSUID']==building['buildingCSUID'],'uniqueViewerMatch':len(matches)==1 and matches[0]['uid']==UID,'identityAccepted':bool(accepted),'detachedComponentAccepted':bool(accepted)}
        save(DOC/'identity-resolution.json',{'uid':UID,**acceptance_row['identityProof'],'policy':'For an exact unique source, accept >99% target coverage, <11m extension and <0.25m centroid offset when every other projected form is a detached <6m2 component, is >99% covered, and has no vertical source-excess intersection. The detached fallback remains present.','detachedForms':adjacent,'coarseHull':metrics['rows'][0]['identity'],'detailedProjection':identity,'projectionMetrics':projection,'evidenceHashes':{rel(final_path):h(final_path),rel(diagnostic_path):h(diagnostic_path)},'sourceSHA256':entry['sha256'],'aiCalls':0,'modelGeometryChanges':0})
    reasons=policy.reasons(acceptance_row,metrics['rows'][0],metrics['profiles']['mobile'])
    validation_concerns=list(validation.get('concerns',[]))
    if UID in VALIDATION_CONTACT_EXCEPTIONS and validation_concerns==['sampled-terrain-above-model-bottom']:
        contact=metrics['rows'][0]
        accepted=(contact['sourcePreserved'] and contact['missingTerrain']==0 and contact['minSurfaceGap']>=-.5 and contact['minLowGap']<=.1 and contact['maxLowGap']<=1 and contact['maxSamplerDelta']<=.004)
        if accepted:
            validation_concerns=[]
        save(DOC/'contact-resolution.json',{'uid':UID,'accepted':bool(accepted),'coarseConcern':'sampled-terrain-above-model-bottom','fullTriangleContact':{k:contact[k] for k in ('sourcePreserved','missingTerrain','minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta')},'metricsSHA256':h(DOC/'metrics.json'),'validationSHA256':h(DOC/'validation.json'),'policy':'A coarse bounds sample cannot hold an unchanged exact source when complete triangle-surface contact has terrain coverage, <=0.5m penetration, a contacting low rim, <=1m low-rim gap and <=4mm sampler disagreement.','aiCalls':0,'modelGeometryChanges':0})
    reasons+=validation_concerns
    if validation['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
    remaining=set(read(DOC/'neighbour-checks.json')['patches'][0]['blockedBy'])-set(support_resolved)-set(native_resolved)
    if remaining:reasons.append('terrain-correction-regresses-neighbours')
    if replacement:
        native_path=DOC/'native-neighbour-checks.json';native_checks=read(native_path)
        retained=set(replacement['retainedUids']);checked={row['uid'] for row in native_checks['rows'] if row.get('passed')}
        if not retained<=checked:reasons.append('replacement-retained-native-check-failed')
        review={'status':'approved-for-integration' if not reasons else 'held','supersededURL':replacement['url'],'supersededSHA256':replacement['sha256'],'replacementSHA256':patch_entry['sha256'],'retainedUids':sorted(retained),'replacementTargetUids':patch['meta']['targetUids'],'fullMeshCheck':{'path':rel(native_path),'sha256':h(native_path)},'sourceGeometryChanged':False,'aiCalls':0,'modelGeometryChanges':0}
        save(DOC/'native-replacement-review.json',review);patch_entry['nativeReview']={'path':rel(DOC/'native-replacement-review.json'),'sha256':h(DOC/'native-replacement-review.json')}
    save(DOC/'result.json',{'uid':UID,'passed':not reasons,'stage':'patched-terrain-and-neighbour-checks','reasons':reasons,'patch':patch_entry,'aiCalls':0});print(json.dumps(read(DOC/'result.json')),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
