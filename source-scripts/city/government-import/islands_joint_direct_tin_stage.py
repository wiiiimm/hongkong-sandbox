"""Compose current direct originals with a disjoint verified private TIN group.

No approval transfers. Complete unused source positions in four coordinate
streams prove the direct sources cannot touch the TIN domains. Fresh joint
metrics, actual browser review and the unchanged guarded publisher still follow.
"""
import argparse
import copy
from pathlib import Path
import subprocess
import sys
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from run import connect


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--tin-source',required=True);p.add_argument('--direct-check',action='append',required=True);a=p.parse_args()
    assert all(b.startswith('government-islands-') and '/' not in b for b in [a.batch,a.tin_source,*a.direct_check])
    doc=ROOT/'docs/astra-city/government-import'/a.batch;stage=HERE/'accepted'/a.batch
    assert not doc.exists() and not stage.exists()
    base=ROOT/'docs/astra-city/government-import';manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifest_sha=sha(manifest_path)
    pins={rel(manifest_path):manifest_sha,rel(Path(__file__)):sha(Path(__file__))};rows={};models={};identities={};direct=set();proofs=[]
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    def pin(path):
        path=Path(path);h=sha(path);key=rel(path);assert key not in pins or pins[key]==h; pins[key]=h
    def check_job(result_path):
        sync_path=result_path.parent/'neon-sync.json';sync=read(sync_path);result=read(result_path)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY');state,stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(sync['jobId'],)).fetchone()
        assert sync['exactResultMatch'] and state=='complete' and stored['evidence']=={'path':rel(result_path),'sha256':sha(result_path)}
        assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==result
        pin(result_path);pin(sync_path);proofs.append({'jobId':sync['jobId'],'path':rel(result_path),'sha256':sha(result_path)})
        return result
    def take(batch,source_rows,source_models,identity_path,wanted):
        by_row={r['uid']:r for r in source_rows};by_model={m['uid']:m for m in source_models}
        for uid in wanted:
            assert uid not in rows and uid not in installed and uid in by_row and uid in by_model
            row=copy.deepcopy(by_row[uid]);entry=copy.deepcopy(by_model[uid]);asset=HERE/'accepted'/batch/entry['asset']
            assert sha(asset)==entry['sha256']==row['candidate']['entry']['sha256']
            assert entry['publicationApproved'] is False and entry['placementReviewed'] is False
            rows[uid]=row;models[uid]=(entry,asset);pin(asset)
        pin(identity_path)
        for r in read(identity_path)['rows']:
            if r['uid'] in wanted:
                assert r['uid'] not in identities or identities[r['uid']]==r;identities[r['uid']]=r
    tin_doc=base/a.tin_source;tin_stage=HERE/'accepted'/a.tin_source;tin=read(tin_doc/'stage.json');selection=read(tin_doc/'selection.json.gz')
    assert selection['manifestSHA256']==manifest_sha and sha(tin_stage/'catalogue.json')==tin['catalogueSHA256'] and sha(tin_stage/'plan.json')==tin['planSHA256']
    for path,h in tin['inputHashes'].items():assert sha(ROOT/path)==h,path;pin(ROOT/path)
    results=[ROOT/path for path in tin['inputHashes'] if path.endswith('/runtime-current/results.json.gz')];assert len(results)==1
    checked=check_job(results[0]);assert set(tin['uids'])<={r['uid'] for r in checked['rows'] if not r['reasons']}
    catalogue=read(tin_stage/'catalogue.json');take(a.tin_source,selection['rows'],catalogue['models'],ROOT/tin['identityEvidencePath'],set(tin['uids']))
    plan=read(tin_stage/'plan.json');top=plan['topLevelTerrainPatches'];assert top and len(plan['areas'])==1
    domains=[]
    for patch in top:
        path=ROOT/patch['source'];assert sha(path)==patch['sha256'];pin(path);terrain=read(path);assert set(terrain['meta']['targetUids'])<=set(tin['uids'])
        g=terrain['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];hx=x+(terrain['w']-1)*g['aE'];hz=z-(terrain['h']-1)*g['aN'];domains.append([min(x,hx),min(z,hz),max(x,hx),max(z,hz)])
    for path in (tin_doc/'stage.json',tin_doc/'selection.json.gz',tin_stage/'catalogue.json',tin_stage/'plan.json'):pin(path)
    for batch in a.direct_check:
        source_doc=base/batch;selected=read(source_doc/'selection.json.gz');assert selected['manifestSHA256']==manifest_sha
        result=check_job(source_doc/'results.json.gz');wanted={r['uid'] for r in result['rows'] if not r['reasons']}
        for path,h in result['inputHashes'].items():assert sha(ROOT/path)==h,path;pin(ROOT/path)
        for path,h in read(source_doc/'metrics.json')['inputHashes'].items():assert sha(ROOT/path)==h,path;pin(ROOT/path)
        take(batch,selected['rows'],read(HERE/'accepted'/batch/'catalogue.json')['models'],ROOT/selected['identityEvidencePath'],wanted);direct.update(wanted)
        for path in (source_doc/'selection.json.gz',source_doc/'metrics.json',source_doc/'validation.json',source_doc/'dependency-preflight.json'):pin(path)
    assert direct and 0<len(rows)<=40
    for uid,row in rows.items():
        if row.get('identityProof'):assert identities[uid]['passed'] and identities[uid]['proof']==row['identityProof']
    refs=[{'path':'3d-viewer/'+url,'sha256':sha(ROOT/'3d-viewer'/url)} for url in manifest['officialModelCatalogues']]
    capture_input=doc/'complete-source-input.json.gz';capture_output=doc/'complete-source-attributes.json.gz'
    save(capture_input,{'currentManifest':{'path':rel(manifest_path),'sha256':manifest_sha},'currentCatalogueRefs':refs,'evidenceRefs':proofs,
        'expectedSourceByUid':{u:[models[u][0]['sha256'],models[u][0]['triangles']] for u in rows},
        'rows':[{'uid':u,'entry':models[u][0],'path':rel(models[u][1]),'building':rows[u]['source']['building']} for u in rows]})
    subprocess.run(['node',HERE/'selected_original_render_attributes_v1.mjs',rel(capture_input),rel(capture_output)],cwd=ROOT,check=True)
    capture=read(capture_output);assert capture['startEndAllInputsVerified'] and len(capture['rows'])==len(rows)
    bounds_proof=[]
    for r in capture['rows']:
        if r['uid'] not in direct:continue
        raw=packed_world_bounds(models[r['uid']][1].read_bytes());assert raw['completeOriginalTriangles']==models[r['uid']][0]['triangles']
        bounds=[raw['originalWholeSourceBounds'],r['completeLiteralWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
        for lo,hi in bounds:
            assert all(hi[0]<x0 or lo[0]>x1 or hi[2]<z0 or lo[2]>z1 for x0,z0,x1,z1 in domains),'Direct source may touch proposed TIN; fresh joint terrain scope required'
        bounds_proof.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'completeFourWorldBounds':bounds})
    for path,h in capture['inputHashes'].items():assert sha(ROOT/path)==h,path;pin(ROOT/path)
    pin(capture_input);pin(capture_output)
    save(doc/'disjoint-direct-source-proof.json',{'rows':bounds_proof,'tinDomains':domains,'sourceGeometryChanges':0,'publication':False});pin(doc/'disjoint-direct-source-proof.json')
    catalogue.update(area='Joint unchanged Peng Chau and Cheung Chau originals',models=[models[u][0] for u in sorted(models)],counts={'packedModels':len(models)})
    for entry,source in models.values():
        target=stage/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());assert sha(target)==entry['sha256']
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
    save(stage/'source-forms.json',[{**r['source']['building'],'tile':Path(r['source']['tile']).stem} for r in rows.values()])
    save(doc/'selection.json.gz',{'batch':a.batch,'manifestSHA256':manifest_sha,'rows':list(rows.values()),'directSourceUids':sorted(direct)})
    identity_path=doc/'identity-evidence.json.gz';save(identity_path,{'rows':list(identities.values()),'sourceEvidence':proofs,'publication':False});pin(identity_path)
    destination=f'city/data/official-models/{a.batch}/catalogue.json';plan['areas'][0].update(area=catalogue['area'],catalogue=rel(stage/'catalogue.json'),destination=destination)
    save(stage/'plan.json',plan);terrain_candidates=doc/'terrain-candidates.json';save(terrain_candidates,[{'path':p['source'],'sha256':p['sha256']} for p in top])
    save(stage/'browser-config.json',{'stage':rel(stage)+'/','doc':rel(doc)+'/','catalogueURL':destination,'terrain':[{'source':p['source'],'destination':p['destination'],'resolution':p['resolution'],'area':p['area']} for p in top],
        'fitBox':True,'browserUids':sorted(rows),'failureTestUids':sorted(rows),'visibilitySupplementUids':[],'captureDirectionByModel':{u:[.2,4,.2] for u in rows},'viewQualification':'High oblique source/retained-neighbour views; no every-facade/as-built/device-performance claim.'})
    for path,h in pins.items():assert sha(ROOT/path)==h,path
    save(doc/'stage.json',{'batch':a.batch,'uids':sorted(rows),'sources':len(rows),'inputHashes':pins,'identityEvidencePath':rel(identity_path),'terrainCandidates':rel(terrain_candidates),
        'additionalLeaseResources':tin['additionalLeaseResources'],'catalogueSHA256':sha(stage/'catalogue.json'),'planSHA256':sha(stage/'plan.json'),'sourceGeometryChanges':0,'publication':False,
        'qualification':'Current full TIN-neighbour checks plus complete four-world disjoint direct sources; fresh joint metrics/browser/guarded/live acceptance still mandatory.'})
    print({'privateOriginals':len(rows),'directSources':len(direct),'tinSources':len(tin['uids']),'terrainPatches':len(top),'publication':False},flush=True)


if __name__=='__main__':main()
