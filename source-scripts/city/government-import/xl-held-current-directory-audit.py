"""Audit exact held XL source revisions using official ZIP directories only.

Four bounded network workers inspect metadata; no model payload, geometry,
review, progress credit or publication. Pin old selection/native receipts and
new directory hashes separately, including unchanged IDs with changed members.
"""
import argparse, json, subprocess, sys, uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
sys.path.insert(0, str(HERE.parent/'citywide-source'))
from discover import scan


def ref(p): return {'path':str(p.relative_to(ROOT)), 'sha256':digest(p.read_bytes())}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--uids-file',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--owned',action='store_true')
    a=p.parse_args();assert 1<=a.workers<=4
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    uidfile=(ROOT/a.uids_file).resolve();assert uidfile.is_relative_to(HERE/'local')
    uids=read(uidfile)['uids'];assert 1<=len(uids)<=352 and len(set(uids))==len(uids)
    macro=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz'
    wanted=set(uids);rows=[r for r in read(macro)['rows'] if r['uid'] in wanted]
    assert {r['uid'] for r in rows}==wanted
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    if not a.owned:
        assert not doc.exists(), 'Fresh immutable audit only'
        claim=reservations.claim('codex-xl-directory-audit-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=a.batch)
        assert claim['ok'],claim
        save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
        subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
        return
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not wanted&installed, 'Installed sources are outside this audit'
    sheets=sorted({r['native']['sheet'] for r in rows})
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        historical=dict(con.execute('SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC',(sheets,)).fetchall())
        for r in rows:
            n=r['native']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,n['cacheKey'])).fetchone()==(n['resultSha'],)
    assert set(historical)==set(sheets)
    save(doc/'audit-inputs.json',{'uids':uids,'selection':ref(macro),'manifestAtStart':ref(manifest),
        'nativeRun':NATIVE_RUN,'sources':[{'uid':r['uid'],'modelId':r['modelId'],'sourceSHA256':r['sourceSHA256'],'cacheKey':r['native']['cacheKey'],'resultSha':r['native']['resultSha'],'sheet':r['native']['sheet']} for r in rows],
        'oldDirectories':historical,'runner':ref(Path(__file__))})
    directories={};errors={}
    def inspect(sheet):
        old=historical[sheet]
        fresh,_=scan({'SHEETNO':sheet,'Format_glTF':old['sourceURL'],'REVISIONDATE':old['revision']},local/'sheets'/sheet/'directory',refresh=True)
        return sheet,fresh
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        pending={pool.submit(inspect,s):s for s in sheets}
        for f in as_completed(pending):
            assert reservations.owns(lease)
            s=pending[f]
            try:_,directories[s]=f.result()
            except Exception as e:errors[s]=type(e).__name__+': '+str(e)[:200]
            print(json.dumps({'sheetsDone':len(directories)+len(errors),'sheets':len(sheets),'errors':len(errors)}),flush=True)
    outcomes=[]
    for r in rows:
        sheet=r['native']['sheet'];old=historical[sheet];fresh=directories.get(sheet)
        out={'uid':r['uid'],'name':r['name'],'sheet':sheet,'previousModelId':r['modelId'],'previousSourceSHA256':r['sourceSHA256']}
        if fresh is None:out.update(status='directory-unavailable',reason=errors[sheet])
        else:
            matches=[m for m in fresh['models'] if m['modelId'][:-1]==r['modelId'][:-1]]
            if len(matches)!=1:out.update(status='missing-or-ambiguous',matches=len(matches))
            else:
                current=matches[0];prior=next((m for m in old['models'] if m['modelId']==r['modelId']),None)
                def members(m):return sorted((x['name'],x['crc32'],x['decodedBytes']) for x in m['members'])
                unchanged=prior is not None and current['modelId']==r['modelId'] and members(current)==members(prior)
                out.update(status='unchanged-members' if unchanged else 'changed-original-members',currentModelId=current['modelId'],memberMetadata=current,
                    previousETag=old['etag'],currentETag=fresh['etag'],currentDirectorySHA256=fresh['directorySHA256'])
        outcomes.append(out)
    save(doc/'directory-audit.json',{'rows':outcomes,'errors':errors,'downloadedModelPayloads':0,'publication':False})
    refs=[ref(doc/'audit-inputs.json'),ref(doc/'directory-audit.json'),ref(Path(__file__)),ref(HERE.parent/'citywide-source/discover.py'),ref(HERE.parent/'landmark-acquisition/acquire.py')]
    refs += [ref(local/'sheets'/s/'directory'/n) for s in directories for n in ['result.json','zip-directory.bin','transfer.json']]
    payload={'uids':uids,'evidenceRefs':refs};stage='held-xl-current-original-directory-audit-v1'
    jid=jobs.enqueue(a.batch,stage,payload);job=jobs.claim(a.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':a.batch,'rows':outcomes,'errors':errors,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'downloadedModelPayloads':0,
        'qualification':'Exact bounded original directory audit only; changed members require fresh acquisition, identity, placement, full runtime and publication acceptance. No remodelling or skip credit.'}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
        for r in refs:assert ref(ROOT/r['path'])==r
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
    save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True})
    from collections import Counter
    print(json.dumps({'jobId':jid,'counts':dict(Counter(r['status'] for r in outcomes)),'newlyInstalled':0}),flush=True)

if __name__=='__main__':main()
