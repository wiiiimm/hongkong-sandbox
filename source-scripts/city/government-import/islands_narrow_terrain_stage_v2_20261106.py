"""Test three smaller domains after the broad terrain proposal failed neighbours.

Private diagnostics only. Original building bytes/poses remain unchanged. Current
native/BASIC neighbours, renderer contacts, browser and publisher remain separate.
"""
from collections import Counter
import json
from pathlib import Path
import sys
import numpy as np
import shapely
from shapely.geometry import box
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
from run import reservations

BATCH='government-islands-peng-chau-narrow-terrain-20261106-v2'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
STAGE=HERE/'accepted'/BATCH


def main():
    receipts=read(LOCAL/'reservations.json');assert all(reservations.owns(r)for r in receipts)
    source_doc=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-source-terrain-20261106'
    source_local=HERE/'local/government-islands-peng-chau-source-terrain-20261106'
    context_path=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-context-20261106-v1/context.json.gz'
    identity_path=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-identity-20261106-v1/identities.json.gz'
    contexts={r['uid']:r for r in read(context_path)['rows']};identities={r['uid']:r for r in read(identity_path)['rows']}
    selected={r['uid']:r for r in read(source_doc/'check-selection.json.gz')['rows'] if r['uid']in contexts}
    selected={u:r for u,r in selected.items() if u in {'landsd/191603:0','landsd/192071:0','landsd/56226:0'}}
    assert len(selected)==3
    geometry=read(source_local/'geometry.json.gz');geometries={r['uid']:r for r in geometry['rows']}
    for p,digest in geometry['inputHashes'].items():assert sha(ROOT/p)==digest,p
    old=module('islands_existing_terrain_stage',HERE/'tai-o-terrain-pass.py');resolve=old.resolve
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
    installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    pins={rel(p):sha(p)for p in [Path(__file__),HERE/'tai-o-terrain-pass.py',HERE/'resolve-pass.py',context_path,identity_path,parent_path,manifest_path,source_doc/'source-terrain.json']}
    proofs={r['sheet']:r for r in read(source_doc/'source-terrain.json')['sheets']};terrains={}
    for sheet,proof in proofs.items():
        for p in proof['members']:assert sha(ROOT/p['path'])==p['sha256'];pins[p['path']]=p['sha256']
        terrains[sheet]=np.concatenate([resolve.context.triangles(p)for p in sorted((source_local/'source-terrain'/sheet/'decoded').rglob('*.gltf'))])
    all_terrain=np.concatenate(list(terrains.values()))
    reasons={};eligible=[];native_audits={}
    for uid,row in selected.items():
        assert uid not in installed
        entry=row['candidate']['entry'];strict=entry['overlapOfSmallerFootprint']>=.98 and entry['footprintCentroidDistanceMetres']<=1
        if not strict and not identities[uid]['passed']:reasons[uid]=['exact-source-identity-unresolved'];continue
        points,bottom=resolve.sample_points(geometries[uid]);lo,hi=np.array(entry['worldBounds'])
        tri=all_terrain[(all_terrain[:,:,0].max(axis=1)>=lo[0]-1)&(all_terrain[:,:,0].min(axis=1)<=hi[0]+1)&(all_terrain[:,:,2].max(axis=1)>=lo[2]-1)&(all_terrain[:,:,2].min(axis=1)<=hi[2]+1)]
        audit=resolve.audit_native(points,bottom,tri);native_audits[uid]=audit
        if not audit['passed']:reasons[uid]=audit['reasons'];continue
        eligible.append(row)
    groups=[{'uids':[r['uid']],'cells':resolve.rectangle_for(r['candidate']['entry']['worldBounds'],parent),'parentURL':'city/data/terrain.json'}for r in eligible]
    groups=old.merge(groups);top=[];patches=[];retained=set();stage_rows=[]
    installed_patches=[read(ROOT/'3d-viewer'/r['url'])for r in manifest['terrainPatches']]
    for number,group in enumerate(groups,1):
        try:
            assert not any(old.terrain_helpers.overlap(group['cells'],p['coarseCells'])for p in installed_patches),'existing-terrain-overlap-requires-complete-retention-route'
            bounds=resolve.extent(group['cells'],parent);pieces=[];sources=[]
            for sheet,tri in terrains.items():
                hit=tri[(tri[:,:,0].max(axis=1)>=bounds[0])&(tri[:,:,0].min(axis=1)<=bounds[2])&(tri[:,:,2].max(axis=1)>=bounds[1])&(tri[:,:,2].min(axis=1)<=bounds[3])]
                if not len(hit):continue
                pieces.append(hit);sources.append({**{k:proofs[sheet][k]for k in ('sheet','revisionDate','sourceETag','directorySHA256','compactArchiveSHA256')},'sourceFiles':proofs[sheet]['members']})
            assert pieces,'missing-original-terrain'
            patch_id=f'islands-peng-chau-narrow-{number:03d}-20261106'
            fine=min(5,abs(parent['meta']['georef']['aE'])/5);points=(round((bounds[2]-bounds[0])/fine)+1)*(round((bounds[3]-bounds[1])/fine)+1)
            if points>100000 or len(group['uids'])>50:
                patch=old.sampled_patch(group,parent,pieces,sources,'city/data/terrain.json',sha(parent_path),patch_id)
            else:
                try:patch=resolve.make_patch(group,parent,np.concatenate(pieces),sources,parent_sha256=sha(parent_path),allow_native_below_clamp=True,terrain_triangle_budget=50000)
                except (ValueError,AssertionError):patch=old.sampled_patch(group,parent,pieces,sources,'city/data/terrain.json',sha(parent_path),patch_id)
            patch['id']=patch_id;p=STAGE/'terrain'/(patch_id+'.json');save(p,patch)
            top.append({'source':rel(p),'sha256':sha(p),'destination':'city/data/'+patch_id+'.json','resolution':patch['cell'],'area':'Peng Chau original-source terrain candidates'})
            patches.append({'path':rel(p),'sha256':sha(p),'uids':group['uids'],'bounds':bounds,'triangles':len(patch.get('nativeMesh',{}).get('index',[]))//3})
            retained.update(group['uids'])
        except (ValueError,AssertionError)as error:
            for uid in group['uids']:reasons[uid]=['terrain-construction:'+str(error)]
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


if __name__=='__main__':main()
