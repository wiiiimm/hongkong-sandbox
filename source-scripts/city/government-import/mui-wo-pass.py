"""Resume the 23 uninstalled Mui Wo government models; exact source, no AI."""
import argparse,collections,importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH='government-mui-wo-23-20260914'
UIDS=tuple('landsd/'+v+':0' for v in ('121912 172460 179822 192816 195736 201705 '
 '206975 207849 207855 207859 207860 208036 208958 254783 257154 262466 299366 '
 '299367 299369 299375 299376 299383 299384').split())
spec=importlib.util.spec_from_file_location('xl_pass',HERE/'xl-pass.py');xl=importlib.util.module_from_spec(spec);spec.loader.exec_module(xl)
xl.BATCH=BATCH;xl.LIMIT=len(UIDS);xl.LOCAL=HERE/'local'/BATCH;xl.DOC=ROOT/'docs/astra-city/government-import'/BATCH

def current(manifest):
    sources={}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes()
        for b in json.loads(raw)['buildings']:
            if b['uid'] in UIDS:sources[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':xl.digest(raw)}
    assert set(sources)==set(UIDS),sorted(set(UIDS)-set(sources));return sources

def installed(manifest):
    result={}
    for url in manifest.get('officialModelCatalogues',[]):
        for e in xl.read(ROOT/'3d-viewer'/url)['models']:result[e['uid']]=e
    return result

def prepare():
    if xl.LOCAL.exists():raise ValueError('Frozen batch exists; resume with recover or check')
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=xl.read(manifest_path);sources=current(manifest)
    assert not set(UIDS)&set(installed(manifest)),'Queued model is already installed'
    with xl.connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        inventory=c.execute('SELECT cache_key,model_id,viewer_uid FROM astra_modelling.native_model_sizes WHERE run_id=%s AND viewer_uid=ANY(%s) ORDER BY viewer_uid',(xl.NATIVE_RUN,list(UIDS))).fetchall()
        assert len(inventory)==len(UIDS) and {r[2] for r in inventory}==set(UIDS)
        native_rows=c.execute("SELECT r.cache_key,r.result_sha,i.sheet,x FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE r.cache_key=ANY(%s) AND x->>'modelId'=ANY(%s)",([r[0] for r in inventory],[r[1] for r in inventory])).fetchall()
        reviews=dict(c.execute("SELECT DISTINCT ON(uid) uid,jsonb_build_object('state',review_state,'sha',source_sha256) FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC",(list(UIDS),)))
    native={(k,m['modelId']):{'cacheKey':k,'resultSha':sha,'sheet':sheet,'model':m} for k,sha,sheet,m in native_rows}
    assert set(native)=={(k,m) for k,m,_ in inventory};rows=[]
    for key,model_id,uid in inventory:
        outcome=native[key,model_id];m=outcome['model'];e=m.get('candidate');b=sources[uid]['building']
        assert m['state']=='packed-needs-placement-review' and e and e['uid']==uid
        assert e['buildingCSUID']==b.get('buildingCSUID') and e['objectId']==b.get('objectId')
        assert e['recordedBaseHeight']==b.get('baseHeightHKPD') and e['recordedTopHeight']==b.get('topHeightHKPD')
        concerns=(['strict-identity-overlap'] if e['overlapOfSmallerFootprint']<.98 else [])+(['strict-identity-centroid'] if e['footprintCentroidDistanceMetres']>1 else [])
        previous=reviews.get(uid)
        if previous and previous['state'] in ('held','source-unavailable','identity-unresolved'):concerns.append('existing-review-requires-resolution')
        rows.append({'modelId':model_id,'uid':uid,'native':outcome,'source':sources[uid],'previousReview':previous,'installedProof':None,'humanStatus':'in-process','reasons':[],'selectionConcerns':sorted(set(concerns)),'name':b.get('name'),'sourceSHA256':m['asset']['sha256'],'triangles':m['triangles']})
    order={uid:i for i,uid in enumerate(UIDS)};rows.sort(key=lambda r:order[r['uid']])
    frozen={'batch':BATCH,'nativeRun':xl.NATIVE_RUN,'rows':rows,'manifestSHA256':xl.h(manifest_path),'selectionPolicy':'Exact 23-model Mui Wo remainder from committed Lantau inventory','sizeGroups':dict(collections.Counter('small' if r['triangles']>=100 else 'xs' for r in rows)),'selectionLimit':len(UIDS),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'aiCalls':0}
    xl.save(xl.LOCAL/'selection.json.gz',frozen);xl.save(xl.DOC/'selection.json.gz',frozen)
    xl.save(xl.LOCAL/'recovery-inputs.json.gz',{'nativeRun':xl.NATIVE_RUN,'rows':list(UIDS),'sources':{r['uid']:r['source'] for r in rows},'native':[r['native'] for r in rows]})
    cache=xl.LOCAL/'recovered/assets';cache.mkdir(parents=True,exist_ok=True);old=HERE.parent/'mui-wo-detail-completion/compact/models';reused=0
    for r in rows:
        source=old/(r['modelId']+'.glb.gz');destination=cache/(r['sourceSHA256']+'.glb.gz')
        if source.exists() and xl.h(source)==r['sourceSHA256']:shutil.copyfile(source,destination);reused+=1
    print(json.dumps({'scope':len(rows),'preseededExactAssets':reused,'selectionConcerns':dict(collections.Counter(x for r in rows for x in r['selectionConcerns'])),'aiCalls':0}),flush=True)


def check():
    frozen=xl.read(xl.LOCAL/'selection.json.gz')
    receipt=xl.reservations.claim('codex-mui-wo-23-'+str(uuid.uuid4()),['building:'+r['uid'] for r in frozen['rows']],batch=BATCH)
    assert receipt['ok'],'Existing source owner; no takeover'
    xl.save(xl.LOCAL/'reservation.json',json.loads(json.dumps(receipt['reservation'],default=str)))
    xl.command([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(xl.LOCAL/'reservation.json'),'--',sys.executable,__file__,'check-owned'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=('prepare','recover','check','check-owned'));phase=p.parse_args().phase
    {'prepare':prepare,'recover':xl.recover,'check':check,'check-owned':xl.check_owned}[phase]()
if __name__=='__main__':main()
