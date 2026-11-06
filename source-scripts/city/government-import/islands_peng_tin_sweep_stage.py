"""Test up to 50 disjoint source-TIN domains after broad groups failed neighbours.

Private diagnostics only. Original building bytes/poses remain unchanged. Current
native/BASIC neighbours, renderer contacts, browser and publisher remain separate.
"""
from collections import Counter
import json
from pathlib import Path
import sys
import hashlib
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from source_triangle_windows import TriangleWindows
import numpy as np
import shapely
from shapely.geometry import box
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
from run import reservations

BATCH=None
DOC=None
LOCAL=None
STAGE=None



CONSTRUCTION={}

def construct_group(task):
    number,group=task
    old=CONSTRUCTION['old'];resolve=old.resolve;parent=CONSTRUCTION['parent'];proofs=CONSTRUCTION['proofs']
    try:
        assert not any(old.terrain_helpers.overlap(group['cells'],p['coarseCells']) for p in CONSTRUCTION['installed_patches']),'existing-terrain-overlap-requires-complete-retention-route'
        bounds=resolve.extent(group['cells'],parent);pieces=[];sources=[]
        for sheet,window in CONSTRUCTION['windows'].items():
            hit=window.select(bounds)
            if not len(hit):continue
            pieces.append(hit);sources.append({**{k:proofs[sheet][k] for k in ('sheet','revisionDate','sourceETag','directorySHA256','compactArchiveSHA256')},'sourceFiles':proofs[sheet]['members']})
        assert pieces,'missing-original-terrain'
        patch_id=f'{BATCH.removeprefix("government-")}-{number:03d}'
        fine=min(5,abs(parent['meta']['georef']['aE'])/5);points=(round((bounds[2]-bounds[0])/fine)+1)*(round((bounds[3]-bounds[1])/fine)+1)
        if points>100000 or len(group['uids'])>50:
            patch=old.sampled_patch(group,parent,pieces,sources,'city/data/terrain.json',CONSTRUCTION['parentSHA256'],patch_id)
        else:
            try:patch=resolve.make_patch(group,parent,np.concatenate(pieces),sources,parent_sha256=CONSTRUCTION['parentSHA256'],allow_native_below_clamp=True,terrain_triangle_budget=50000)
            except (ValueError,AssertionError):patch=old.sampled_patch(group,parent,pieces,sources,'city/data/terrain.json',CONSTRUCTION['parentSHA256'],patch_id)
        patch['id']=patch_id
        return number,group,patch,bounds,None
    except (ValueError,AssertionError) as error:
        return number,group,None,None,str(error)


def main():
    receipts=read(LOCAL/'reservations.json');assert all(reservations.owns(r)for r in receipts)
    source_doc=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-source-terrain-20261106'
    source_local=HERE/'local/government-islands-peng-chau-source-terrain-20261106'
    context_path=DOC/'context-evidence.json.gz'
    identity_path=DOC/'identity-evidence.json.gz'
    contexts={r['uid']:r for r in read(context_path)['rows']};identities={r['uid']:r for r in read(identity_path)['rows']}
    selected={r['uid']:r for r in read(source_doc/'check-selection.json.gz')['rows'] if r['uid']in contexts}
    nominated=read(DOC/'nomination.json')
    assert 0<len(nominated['uids'])==len(set(nominated['uids']))<=50
    selected={r['uid']:r for r in nominated['rows']}
    assert set(selected)==set(nominated['uids'])
    assert sha(ROOT/'3d-viewer/city/data/manifest.json')==nominated['manifestSHA256']
    geometry=read(source_local/'geometry.json.gz');geometries={r['uid']:r for r in geometry['rows']}
    for p,digest in geometry['inputHashes'].items():assert sha(ROOT/p)==digest,p
    old=module('islands_existing_terrain_stage',HERE/'tai-o-terrain-pass.py');resolve=old.resolve
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
    installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    pins={rel(p):sha(p)for p in [Path(__file__),HERE/'tai-o-terrain-pass.py',HERE/'resolve-pass.py',context_path,identity_path,parent_path,manifest_path,source_doc/'source-terrain.json',DOC/'nomination.json',HERE/'source_triangle_windows.py']}
    proofs={r['sheet']:r for r in read(source_doc/'source-terrain.json')['sheets']};terrains={}
    rejected_terrain=read(context_path)['terrainValidationExceptions']
    assert not any(r['native']['sheet'] in rejected_terrain for r in selected.values())
    for sheet,proof in proofs.items():
        if sheet in rejected_terrain:
            assert rejected_terrain[sheet]['sourceFiles']==proof['members']
            continue
        for p in proof['members']:assert sha(ROOT/p['path'])==p['sha256'];pins[p['path']]=p['sha256']
        terrains[sheet]=np.concatenate([resolve.context.triangles(p)for p in sorted((source_local/'source-terrain'/sheet/'decoded').rglob('*.gltf'))])
    windows={sheet:TriangleWindows(tri) for sheet,tri in terrains.items()}
    reasons={};eligible=[];native_audits={}
    for uid,row in selected.items():
        assert uid not in installed
        entry=row['candidate']['entry'];strict=entry['overlapOfSmallerFootprint']>=.98 and entry['footprintCentroidDistanceMetres']<=1
        if not strict and not identities[uid]['passed']:reasons[uid]=['exact-source-identity-unresolved'];continue
        points,bottom=resolve.sample_points(geometries[uid]);lo,hi=np.array(entry['worldBounds'])
        tri=np.concatenate([window.select([lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1]) for window in windows.values()])
        audit=resolve.audit_native(points,bottom,tri);native_audits[uid]=audit
        if not audit['passed']:reasons[uid]=audit['reasons'];continue
        eligible.append(row)
    groups=[{'uids':[r['uid']],'cells':resolve.rectangle_for(r['candidate']['entry']['worldBounds'],parent),'parentURL':'city/data/terrain.json'}for r in eligible]
    assert not any(old.terrain_helpers.overlap(a['cells'], b['cells']) for i,a in enumerate(groups) for b in groups[i+1:]);top=[];patches=[];retained=set();stage_rows=[]
    installed_patches=[read(ROOT/'3d-viewer'/r['url'])for r in manifest['terrainPatches']]
    CONSTRUCTION.update(old=old,parent=parent,proofs=proofs,windows=windows,installed_patches=installed_patches,parentSHA256=sha(parent_path))
    binding=hashlib.sha256(json.dumps(pins,sort_keys=True).encode()).hexdigest()
    # Fork shares immutable source arrays; children construct independent domains.
    # The lease supervisor stops this entire process group if ownership is lost.
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
        for number,group,patch,bounds,error in pool.map(construct_group,enumerate(groups,1)):
            if error:
                for uid in group['uids']:reasons[uid]=['terrain-construction:'+error]
            else:
                p=STAGE/'terrain'/(patch['id']+'.json')
                if p.exists():assert read(p)==patch,'Interrupted artifact differs from exact recomputation'
                else:save(p,patch)
                resolve.validate_patch(patch,parent)
                top.append({'source':rel(p),'sha256':sha(p),'destination':'city/data/'+patch['id']+'.json','resolution':patch['cell'],'area':'Peng Chau original-source terrain candidates'})
                patches.append({'path':rel(p),'sha256':sha(p),'uids':group['uids'],'bounds':bounds,'triangles':len(patch.get('nativeMesh',{}).get('index',[]))//3})
                retained.update(group['uids'])
                save(DOC/'partial-terrain'/f'{number:03d}.json',{'inputBindingSHA256':binding,'group':group,'artifact':{'path':rel(p),'sha256':sha(p)},'recomputedExactly':True,'publication':False})
            print(json.dumps({'terrainGroups':number,'totalGroups':len(groups),'stagedSourceCandidates':len(retained)}),flush=True)
    for uid in sorted(retained):
        row=selected[uid];entry=dict(row['candidate']['entry']);entry.update(proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)
        p=STAGE/entry['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['candidate']['path']).read_bytes());assert sha(p)==entry['sha256'];stage_rows.append(row)
    base=read(HERE.parent/'kai-tak-port/staged/catalogue.json');catalogue={k:v for k,v in base.items()if k not in ('area','models','counts')}
    catalogue.update(area='Peng Chau original source/terrain private candidates',models=[{**r['candidate']['entry'],'proceduralWindows':False,'publicationApproved':False,'placementReviewed':False,'identityReviewApproved':False,'sourceIdentityReviewed':False}for r in stage_rows],counts={'packedModels':len(stage_rows)})
    save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(stage_rows),'catalogues':['catalogue.json']})
    save(STAGE/'source-forms.json',[{**r['source']['building'],'tile':Path(r['source']['tile']).stem}for r in stage_rows])
    save(DOC/'selection.json.gz',{'batch':BATCH,'manifestSHA256':sha(manifest_path),'rows':stage_rows})
    save(DOC/'terrain-candidates.json',[{'path':p['path'],'sha256':p['sha256']}for p in patches])
    save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':f'city/data/official-models/{BATCH}/catalogue.json','terrain':[]}],'topLevelTerrainPatches':top})
    # Full current forms touching every complete parent-cell rectangle, not only targets.
    affected=[];tree=shapely.STRtree([box(*p['bounds'])for p in patches])
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];raw=read(p)
        for b in raw['buildings']:
            if not b.get('rings'):continue
            shape=old.resolve.shapely.Polygon(b['rings'][0],b['rings'][1:]);ids=tree.query(shape)
            if len(ids):affected.append({'building':b,'patchIndexes':[int(i)for i in ids],'existingNative':b['uid']in installed});pins[rel(p)]=sha(p)
    save(DOC/'neighbour-inputs.json.gz',{'rows':affected,'candidateIds':sorted(retained),'patches':patches,'inputHashes':pins})
    for p,digest in pins.items():assert sha(ROOT/p)==digest,p
    save(DOC/'terrain-stage.json',{'batch':BATCH,'modelsExamined':len(selected),'nativeAudits':native_audits,'eligibleOriginalTIN':len(eligible),'stagedSourceCandidates':len(retained),
        'sourceUids':sorted(retained),'reasons':reasons,'reasonCounts':dict(Counter(x for rs in reasons.values()for x in rs)),
        'patches':patches,'affectedCurrentForms':len(affected),'inputHashes':pins,'sourceGeometryChanges':0,'publication':False,
        'qualification':'Private source-terrain construction only; full current renderer/contact/neighbour/native/browser and guarded publication still required.'})
    print(json.dumps({'terrainStageComplete':True,'candidates':len(retained),'affectedCurrentForms':len(affected),'publication':False}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);args=parser.parse_args()
    assert args.batch.startswith('government-islands-peng-chau-sweep-') and '/' not in args.batch
    BATCH=args.batch;DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;STAGE=HERE/'accepted'/BATCH
    main()
