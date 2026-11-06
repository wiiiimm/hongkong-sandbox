"""Combine disjoint private clear groups for fresh checks in one current context.

This copies unchanged assets and terrain references only. Each parent runtime
job is read back, and the combined proposal still needs complete fresh scope,
runtime, browser review and guarded publication. No acceptance transfers.
"""
import argparse
import copy
from pathlib import Path
import shapely
from shapely.geometry import Polygon, box
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import connect


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',action='append',required=True)
    parser.add_argument('--batch',required=True)
    args=parser.parse_args()
    assert len(args.source)>=2 and len(set(args.source))==len(args.source)
    assert all(b.startswith('government-islands-') and '/' not in b for b in [args.batch,*args.source])
    doc=ROOT/'docs/astra-city/government-import'/args.batch
    stage=HERE/'accepted'/args.batch
    assert not doc.exists() and not stage.exists()
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json'
    manifest=read(manifest_path);manifest_sha=sha(manifest_path)
    pins={rel(manifest_path):manifest_sha,rel(Path(__file__)):sha(Path(__file__))}
    models={};rows={};identities={};top=[];patches=[];cells=[];sources=[];catalogue=None
    overlap=module('islands_combined_terrain_helpers',HERE/'tai-o-terrain-pass.py').terrain_helpers.overlap
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    installed_cells=[read(ROOT/'3d-viewer'/p['url'])['coarseCells'] for p in manifest.get('terrainPatches',[])]
    for batch in args.source:
        base=ROOT/'docs/astra-city/government-import'/batch;source_stage=HERE/'accepted'/batch
        proof=read(base/'stage.json');selected=read(base/'selection.json.gz')
        assert selected['manifestSHA256']==manifest_sha
        assert sha(source_stage/'catalogue.json')==proof['catalogueSHA256']
        assert sha(source_stage/'plan.json')==proof['planSHA256']
        for p,h in proof['inputHashes'].items():assert sha(ROOT/p)==h,p;pins[p]=h
        runtime_paths=[ROOT/p for p in proof['inputHashes'] if p.endswith('/runtime-current/results.json.gz')]
        assert len(runtime_paths)==1
        runtime=runtime_paths[0];result=read(runtime);receipt_path=runtime.parent/'neon-sync.json';receipt=read(receipt_path)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            status,stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()
        assert receipt['exactResultMatch'] and status=='complete'
        assert stored['evidence']=={'path':rel(runtime),'sha256':sha(runtime)}
        assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==result
        clear={r['uid'] for r in result['rows'] if not r['reasons']}
        assert set(proof['uids'])<=clear
        source_catalogue=read(source_stage/'catalogue.json');catalogue=catalogue or copy.deepcopy(source_catalogue)
        assert {m['uid'] for m in source_catalogue['models']}==set(proof['uids'])=={r['uid'] for r in selected['rows']}
        for m in source_catalogue['models']:
            assert m['uid'] not in models and m['uid'] not in installed
            assert m['placementReviewed'] is False and m['publicationApproved'] is False
            asset=source_stage/m['asset'];assert sha(asset)==m['sha256']
            models[m['uid']]=(copy.deepcopy(m),asset);pins[rel(asset)]=sha(asset)
        for r in selected['rows']:rows[r['uid']]=copy.deepcopy(r)
        identity_path=ROOT/proof['identityEvidencePath']
        for r in read(identity_path)['rows']:
            if r['uid'] in proof['uids']:
                if r['uid'] in identities:assert identities[r['uid']]==r
                identities[r['uid']]=r
        plan=read(source_stage/'plan.json')
        for p in plan['topLevelTerrainPatches']:
            path=ROOT/p['source'];assert sha(path)==p['sha256'];terrain=read(path)
            target=set(terrain['meta']['targetUids']);assert target<=set(proof['uids']) and target
            c=terrain['coarseCells'];assert not any(overlap(c,old) for old in [*cells,*installed_cells])
            cells.append(c);top.append(p);g=terrain['meta']['georef']
            x=g['bE']-834500;z=816500-g['bN'];hx=x+(terrain['w']-1)*g['aE'];hz=z-(terrain['h']-1)*g['aN']
            patches.append({'path':p['source'],'sha256':p['sha256'],'uids':sorted(target),'bounds':[min(x,hx),min(z,hz),max(x,hx),max(z,hz)]})
            pins[rel(path)]=sha(path)
        for p in [base/'stage.json',base/'selection.json.gz',source_stage/'catalogue.json',source_stage/'plan.json',identity_path,receipt_path]:pins[rel(p)]=sha(p)
        sources.append({'batch':batch,'runtimeJob':receipt['jobId'],'sources':len(proof['uids'])})
    assert 0<len(models)==len(rows)<=50
    assert set().union(*(set(p['uids']) for p in patches))==set(models)
    for uid,r in rows.items():
        if r.get('identityProof'):assert identities[uid]['passed'] and identities[uid]['proof']==r['identityProof']
    # Independently enumerate all GIS actors in the union; full native bounds
    # are added by islands_tin_current_scope before any runtime admission.
    tree=shapely.STRtree([box(*p['bounds']) for p in patches]);affected=[]
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];pins[rel(path)]=sha(path)
        for form in read(path)['buildings']:
            if not form.get('rings'):continue
            hits=tree.query(Polygon(form['rings'][0],form['rings'][1:]))
            if len(hits):affected.append({'building':form,'patchIndexes':[int(i) for i in hits],'existingNative':form['uid'] in installed})
    for p,h in pins.items():assert sha(ROOT/p)==h,p
    assert sha(manifest_path)==manifest_sha
    catalogue.update(area='Peng Chau and Cheung Chau unchanged original government candidates',models=[models[u][0] for u in sorted(models)],counts={'packedModels':len(models)})
    for m,source in models.values():
        target=stage/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());assert sha(target)==m['sha256']
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
    save(stage/'source-forms.json',[{**r['source']['building'],'tile':Path(r['source']['tile']).stem} for r in rows.values()])
    save(stage/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(stage/'catalogue.json'),'destination':f'city/data/official-models/{args.batch}/catalogue.json','terrain':[]}],'topLevelTerrainPatches':top})
    save(doc/'selection.json.gz',{'batch':args.batch,'manifestSHA256':manifest_sha,'rows':list(rows.values())})
    save(doc/'identity-evidence.json.gz',{'rows':list(identities.values()),'sourceGroups':sources,'publication':False})
    save(doc/'terrain-candidates.json',[{'path':p['path'],'sha256':p['sha256']} for p in patches])
    save(doc/'neighbour-inputs.json.gz',{'rows':affected,'candidateIds':sorted(models),'patches':patches,'inputHashes':pins})
    save(doc/'terrain-stage.json',{'batch':args.batch,'sources':len(models),'groups':sources,'inputHashes':pins,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'publication':False,'qualification':'Exact disjoint private proposals only; complete fresh scope/runtime/browser/publication still required.'})
    print({'sources':len(models),'disjointTerrainGroups':len(patches),'affectedForms':len(affected),'publication':False},flush=True)


if __name__=='__main__':main()
