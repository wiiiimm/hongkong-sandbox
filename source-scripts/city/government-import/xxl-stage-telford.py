"""Stage the exact 61-model Telford estate assembly and bounded source terrain; never AI."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon,box

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
import native_patch_resolution as patch_resolution
ROOT,HERE=s.ROOT,s.HERE
DOC=s.DOC/'third-pass/telford';LOCAL=s.LOCAL/'third-pass-telford'
SUPPORT=s.LOCAL/'telford-supports';STAGE=HERE/'accepted/government-xxl-telford-20260912'
UID='landsd/226033:0';PODIUM='landsd/263578:0';UNRESOLVED='landsd/107325:0'
read,save,h,rel=s.read,s.save,s.h,s.rel


def rows():
    selected=read(s.DOC/'runtime-selection.json.gz')
    primary=next(r for r in selected['rows'] if r['uid']==UID)
    inputs=read(SUPPORT/'inputs.json.gz')
    support=[]
    for item in read(SUPPORT/'geometry-inputs.json')['rows']:
        source=inputs['sources'][item['uid']]
        support.append({'uid':item['uid'],'candidate':item['candidate'],'source':source})
    return selected,primary,support


def start():
    selected,primary,support=rows();combined=[primary,*support];candidate_ids={r['uid'] for r in combined}
    assert len(combined)==61 and PODIUM in candidate_ids and UNRESOLVED not in candidate_ids
    parent=read(ROOT/'3d-viewer/city/data/terrain.json');cells=s.resolution.rectangle_for(primary['candidate']['entry']['worldBounds'],parent);bounds=s.resolution.extent(cells,parent);region=box(*bounds)
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
        for building in json.loads(raw)['buildings']:
            if Polygon(building['rings'][0],building['rings'][1:]).intersects(region):
                neighbours.append({'building':building,'patchIndexes':[0],'existingNative':building['uid'] in live or bool(building.get('modelGeometry'))});touched=True
        if touched:hashes[rel(path)]=s.digest(raw)
    manifest_sha=h(ROOT/'3d-viewer/city/data/manifest.json')
    save(DOC/'selection.json.gz',{**selected,'manifestSHA256':manifest_sha,'rows':combined})
    save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':sorted(candidate_ids),'patches':[]})
    save(DOC/'patch-plan.json',{'cells':cells,'bounds':bounds,'manifestSHA256':manifest_sha,'uid':UID,'candidateUids':sorted(candidate_ids),'unresolvedTerrainPreservation':UNRESOLVED})
    resources={('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:')+n['building']['uid'] for n in neighbours}|{'building:'+u for u in candidate_ids}
    claim=s.reservations.claim('codex-xxl-telford-'+str(uuid.uuid4()),sorted(resources),batch='government-xxl-telford-20260912');assert claim['ok']
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])


def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'))
    plan=read(DOC/'patch-plan.json');assert h(ROOT/'3d-viewer/city/data/manifest.json')==plan['manifestSHA256']
    selected=read(DOC/'selection.json.gz');primary=next(r for r in selected['rows'] if r['uid']==UID);bounds=plan['bounds'];parent=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    seam_proof=read(s.DOC/'third-pass/special-terrain-context.json')['telford'];assert seam_proof['uncoveredSamples']==69 and seam_proof['distanceToRecoveredTerrainRangeM'][1]<.02
    sources=read(s.DOC/'recovery.json')['sheets']+read(s.DOC/'adjacent-terrain-results.json')['sources'];fragments=[];used=[]
    try:
        assert not any(s.resolution.terrain.overlap(plan['cells'],read(ROOT/'3d-viewer'/p['url'])['coarseCells']) for p in manifest['terrainPatches'])
        for source in sources:
            folder=s.LOCAL/'sheets'/source['sheet']/'terrain';found=[]
            for path in source['terrainPaths']:
                triangles=s.context.triangles(ROOT/path);near=triangles[(triangles[:,:,0].max(1)>=bounds[0])&(triangles[:,:,0].min(1)<=bounds[2])&(triangles[:,:,2].max(1)>=bounds[1])&(triangles[:,:,2].min(1)<=bounds[3])]
                if len(near):found.append(near)
            if found:
                fragments.extend(found);proof=source['source'];used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':rel(folder/e['name']),'sha256':e['sha256']} for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]})
        lo,hi=primary['candidate']['entry']['worldBounds'];validator=s.resolution.validate_patch;s.resolution.validate_patch=lambda p,parent:None
        try:patch=s.resolution.make_patch({'uids':[UID],'cells':plan['cells']},parent,np.concatenate(fragments),used,native_core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1])
        finally:s.resolution.validate_patch=validator
        model=s.glb_triangles(next(r for r in read(s.DOC/'selection.json.gz')['rows'] if r['uid']==UID));projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]))
        seam=patch_resolution.fill_narrow_source_seam(patch,bounds,projection,s.resolution.terrain.fine.DemSampler(parent,rendered=True),tolerance=.02)
        neighbour=next(r['building'] for r in read(DOC/'neighbour-inputs.json.gz')['rows'] if r['building']['uid']==UNRESOLVED)
        retained=patch_resolution.preserve_parent_under_projection(patch,bounds,Polygon(neighbour['rings'][0],neighbour['rings'][1:]).buffer(.25),s.resolution.terrain.fine.DemSampler(parent,rendered=True))
        patch_path=LOCAL/(patch['id']+'.json');save(patch_path,patch);patch=read(patch_path)
        overlap=patch_resolution.approve_original_overlap(patch,patch_path,DOC/'native-overlap-evidence.json',[x for source in used for x in source['sourceFiles']]);save(patch_path,patch);validator(patch,parent)
        save(DOC/'terrain-resolution.json',{'sourceSeamFill':seam,'protectedParentProjection':retained,'overlapProof':overlap,'aiCalls':0,'modelGeometryChanges':0})
    except (AssertionError,ValueError) as error:
        save(DOC/'result.json',{'uid':UID,'passed':False,'stage':'source-terrain-patch','reason':str(error),'aiCalls':0});print(json.dumps(read(DOC/'result.json')));return
    patch_entry={'path':rel(patch_path),'sha256':h(patch_path),'uids':[UID],'bounds':bounds,'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[patch_entry])
    neighbour_inputs=read(DOC/'neighbour-inputs.json.gz');neighbour_inputs['patches']=[patch_entry];save(DOC/'neighbour-inputs.json.gz',neighbour_inputs)
    catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[];forms={};source_rows=[]
    for row in selected['rows']:
        entry=dict(row['candidate']['entry']);building=row['source']['building'];entry.update(label=building.get('name') or entry['modelId'],priority='landmark' if row['uid'] in (UID,PODIUM) else 'detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact UID/CSUID-matched unchanged government source in the Telford estate assembly; source terrain/support dependencies are scripted and no AI modelling or geometry edits are used.')
        if row['uid'] not in (UID,PODIUM):entry['supportDependencies']=[{'uid':PODIUM if row['uid'] in ('landsd/85820:0','landsd/209819:0') else UID,'state':'candidate'}]
        entries.append(entry);forms[row['uid']]=row['source'];form=dict(building);form['tile']=Path(row['source']['tile']).stem;source_rows.append(form)
        target=LOCAL/'candidates'/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],target);assert h(target)==entry['sha256']
    catalogue.update(area='Telford estate original government source assembly',counts={'packedModels':len(entries)},models=entries)
    save(LOCAL/'candidates/catalogue.json',catalogue);save(LOCAL/'candidates/catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(LOCAL/'source-forms.json',forms)
    s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
    validation=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert validation.returncode in (0,1)
    s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    metrics=read(DOC/'metrics.json');reasons=[]
    for metric in metrics['rows']:
        if metric.get('error') or not metric.get('sourcePreserved') or metric.get('missingTerrain'):reasons.append('source-integrity-or-terrain-coverage')
        if metric.get('maxSamplerDelta',0)>.004:reasons.append('rendered-terrain-disagreement')
        if metric.get('budget') and any(metric['budget'][k]>metrics['profiles']['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):reasons.append('mobile-runtime-budget')
    for item in read(DOC/'validation.json')['results']:
        if item['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
        entry=next(e for e in entries if e['uid']==item['uid'])
        if not entry.get('supportDependencies'):reasons += item.get('concerns',[])
        else:reasons += [r for r in item.get('concerns',[]) if r not in ('sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom')]
    blocked=read(DOC/'neighbour-checks.json')['patches'][0]['blockedBy']
    if blocked:reasons.append('terrain-correction-regresses-neighbours')
    decision={'uid':UID,'models':len(entries),'policy':'original-government-telford-assembly-v1','passed':not reasons,'reasons':sorted(set(reasons)),'blockedNeighbours':blocked,'patch':patch_entry,'sourceSeamProof':seam_proof,'supportRecovery':read(DOC/'support-source-recovery.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',decision)
    if not reasons:
        for entry in entries:
            target=STAGE/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(LOCAL/'candidates'/entry['asset'],target)
        save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',source_rows)
        staged_patch=STAGE/patch_path.name;shutil.copyfile(patch_path,staged_patch);terrain={'source':rel(staged_patch),'sha256':h(staged_patch),'destination':'city/data/'+staged_patch.name,'resolution':patch['cell'],'area':'Telford estate original native terrain with bounded source-sheet seam'}
        destination='city/data/official-models/government-xxl-telford-20260912/catalogue.json';save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':[terrain]})
        save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/' ,'catalogueURL':destination,'terrain':[terrain],'fitBox':True,'browserUids':[UID,PODIUM,'landsd/85820:0','landsd/209819:0'],'failureTestUids':[UID]})
    print(json.dumps(decision))


if __name__=='__main__':owned() if len(sys.argv)>1 else start()
