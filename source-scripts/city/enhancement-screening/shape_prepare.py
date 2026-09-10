"""Bounded recovery of exact cached source assets for shape screening; no publication."""
import argparse
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import time
import zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'shared-modelling'))
from db import connect
import reservations
sys.path.insert(0,str(HERE.parent/'citywide-source'))
from discover import scan
sys.path.insert(0,str(HERE.parent/'citywide-native'))
from download import acquire
from convert import _convert_one
from source_cache import validate_artifact
sys.path.insert(0,str(HERE.parent/'landmark-resume'))
from r2_snapshot import R2Store, verify_object


def read(p):return json.loads(Path(p).read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2,default=str)+'\n');t.replace(p)


def canonical_bytes(raw,expected):
    if sha(raw)==expected:return raw
    # Python/platform gzip header differences do not change the packed GLB.
    if raw[:3]==b'\x1f\x8b\x08':
        for os_byte in (3,255):
            candidate=raw[:9]+bytes([os_byte])+raw[10:]
            if sha(candidate)==expected and gzip.decompress(candidate)==gzip.decompress(raw):return candidate
    raise ValueError('Recovered asset differs from the pinned native-stage SHA')


def entry(outcome,building):
    m=outcome['model'];matches=[v for v in m['matching']['viewerMatches'] if v['uid']==building['uid']]
    if len(matches)!=1:raise ValueError('Ambiguous source UID')
    return {**m['asset'],**matches[0],'modelId':m['modelId'],'triangles':m['triangles'],
            'worldBounds':m['worldBounds'],'sourceTile':outcome['sheet'],
            'rootTranslation':[-834500,0,816500],'priority':'unreviewed'}


def prepare(evidence,out,allow_source=False,workers=4,env_file=None):
    """Immutable local caches plus read-only source metadata; reserve acquisition scope."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    if not 1<=workers<=8:raise ValueError('workers must be 1..8')
    e=json.loads(gzip.decompress(Path(evidence).read_bytes()))
    outcomes=defaultdict(list)
    for o in e['native']:
        for v in o['model'].get('matching',{}).get('viewerMatches',[]):outcomes[v['uid']].append(o)
    chosen={uid:rows[0] for uid,rows in outcomes.items() if uid in e['rows'] and len(rows)==1 and rows[0]['model'].get('asset')}
    if len(chosen)>1000:raise ValueError('Use batches of at most 1000 source forms')
    # Snapshot all source geometry used; existing native models are loaded from the real manifest.
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');current={};local={}
    for url in manifest.get('officialModelCatalogues',[]):
        cat=read(ROOT/'3d-viewer'/url)
        for m in cat['models']:
            p=(ROOT/'3d-viewer'/url).parent/m['asset'];local[m['sha256']]=p
            current[m['uid']]={'path':str(p),'entry':{**m,'rootTranslation':cat['rootTranslation']}}
    for p in (HERE.parent/'kai-tak-port/staged/assets').glob('*.glb.gz'):local[p.name.removesuffix('.glb.gz')]=p
    cache=out/'assets';cache.mkdir(exist_ok=True)
    recovered={};errors={};methods=Counter();missing=defaultdict(list)
    for uid,o in chosen.items():
        h=o['model']['asset']['sha256'];dest=cache/(h+'.glb.gz');p=dest if dest.exists() else local.get(h)
        try:
            if p:
                raw=canonical_bytes(p.read_bytes(),h)
                if len(raw)!=o['model']['asset']['bytes']:raise ValueError('Cached asset byte count mismatch')
                if p!=dest:dest.write_bytes(raw)
                recovered[uid]=dest;methods['local-exact-cache']+=1
            else:missing[o['sheet']].append((uid,o))
        except Exception as ex:errors[uid]=type(ex).__name__+': '+str(ex)
    r2=None;r2_status='not-configured'
    if env_file:
        from dotenv import dotenv_values
        for k,v in dotenv_values(env_file).items():
            if k.startswith('R2_') and v and v!='[SENSITIVE]':os.environ.setdefault(k,v)
    try:r2=R2Store('hk-sandbox-assets');r2_status='configured'
    except (ValueError,ImportError):pass
    metadata=out/'source-metadata.json'
    if missing:
        meta=read(metadata) if metadata.exists() else {'directories':{},'stages':{}}
        needed_sheets=sorted(set(missing)-set(meta['directories']))
        needed_keys=sorted({o['cacheKey'] for items in missing.values() for _,o in items}-set(meta['stages']))
        if needed_sheets or needed_keys:
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                if needed_sheets:meta['directories'].update(dict(con.execute("SELECT DISTINCT ON(sheet) sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC",(needed_sheets,)).fetchall()))
                if needed_keys:meta['stages'].update(dict(con.execute("SELECT cache_key,jsonb_build_object('artifacts',result->'artifacts') FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)",(needed_keys,)).fetchall()))
        # Directory offsets are fetched/validated by the existing scanner, not duplicated here.
        for d in meta['directories'].values():d.pop('models',None)
        for d in meta['stages'].values():d.pop('download',None)
        save(metadata,meta)
        owned=reservations.claim('codex-shape-screening-'+str(os.getpid()),['building:'+uid for items in missing.values() for uid,_ in items],ttl=3600,batch='shape-screening-pilot')
        if not owned['ok']:raise ValueError('Source reservation conflict; acquisition not started')
        receipt=json.loads(json.dumps(owned['reservation'],default=str))
        def sheet_work(sheet,items):
            folder=out/'sheets'/sheet;folder.mkdir(parents=True,exist_ok=True);results=[]
            # Prefer exact prepared bytes in the shared bundle. Source fallback is explicit.
            restore_error=None
            if r2:
                try:
                    artifacts={a['sha256']:a for _,o in items for a in meta['stages'][o['cacheKey']].get('artifacts',[]) if a.get('kind')=='original-and-prepared-sheet'}
                    needed={o['model']['asset']['sha256']:(uid,o) for uid,o in items}
                    for artifact in artifacts.values():
                        validate_artifact(artifact);bundle=folder/(artifact['sha256']+'.tar.gz')
                        if not bundle.exists() or sha(bundle.read_bytes())!=artifact['sha256']:verify_object(r2,artifact['key'],artifact['sha256'],artifact['bytes'],bundle)
                        with tarfile.open(bundle,'r:gz') as tar:
                            for member in tar:
                                h=Path(member.name).name.removesuffix('.glb.gz')
                                if h not in needed:continue
                                uid,o=needed[h]
                                if not member.isfile() or member.size!=o['model']['asset']['bytes']:raise ValueError('Unexpected prepared bundle member')
                                raw=canonical_bytes(tar.extractfile(member).read(),h);(cache/(h+'.glb.gz')).write_bytes(raw)
                    if all((cache/(o['model']['asset']['sha256']+'.glb.gz')).exists() for _,o in items):return [(uid,'r2-exact-cache',None) for uid,o in items]
                except Exception as ex:restore_error=type(ex).__name__ # no endpoints/credentials in evidence
            if not allow_source:return [(uid,None,'native-cache-unavailable'+(':'+restore_error if restore_error else '')) for uid,_ in items]
            prior=meta['directories'].get(sheet)
            if not prior:return [(uid,None,'source-directory-unavailable') for uid,_ in items]
            try:
                row,_=scan({'SHEETNO':sheet,'Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},folder/'directory')
                if row['etag']!=prior['etag'] or row['directorySHA256']!=prior['directorySHA256']:raise ValueError('Source revision changed')
                wanted={o['model']['modelId'] for _,o in items};row['models']=[m for m in row['models'] if m['modelId'] in wanted]
                if {m['modelId'] for m in row['models']}!=wanted:raise ValueError('Source model missing from pinned directory')
                acquired=acquire(row,folder/'directory/zip-directory.bin',folder/'original')
                packed=folder/'packed';packed.mkdir(exist_ok=True)
                with zipfile.ZipFile(folder/'original'/f'{sheet}.zip') as z:
                    for uid,o in items:
                        try:
                            m=o['model'];h=m['asset']['sha256'];dest=cache/(h+'.glb.gz')
                            if not dest.exists():
                                r=_convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',packed,{}, {'modelId':m['modelId']})
                                raw=canonical_bytes((packed/r['asset']['asset']).read_bytes(),h)
                                if len(raw)!=m['asset']['bytes']:raise ValueError('Recovered byte count mismatch')
                                dest.write_bytes(raw)
                            results.append((uid,'verified-government-recovery',None))
                        except Exception as ex:results.append((uid,None,type(ex).__name__+': '+str(ex)[:160]))
                save(folder/'recovery.json',{'download':acquired,'results':results})
                return results
            except Exception as ex:return [(uid,None,type(ex).__name__+': '+str(ex)[:160]) for uid,_ in items]
        try:
            save(out/'reservation.json',receipt)
            done=0;last_heartbeat=time.monotonic()
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures=[pool.submit(sheet_work,s,items) for s,items in missing.items()]
                for f in as_completed(futures):
                    if time.monotonic()-last_heartbeat>240:
                        if not reservations.heartbeat(receipt,ttl=3600)['ok']:raise ValueError('Source ownership lost')
                        last_heartbeat=time.monotonic()
                    for uid,method,error in f.result():
                        if error:errors[uid]=error
                        else:recovered[uid]=cache/(chosen[uid]['model']['asset']['sha256']+'.glb.gz');methods[method]+=1
                    done+=1
                    if done%25==0:print(json.dumps({'sheetsDone':done,'sheets':len(missing),'assets':len(recovered),'errors':len(errors)}),flush=True)
        finally:reservations.release(receipt)
    rows=[]
    for uid,p in sorted(recovered.items()):
        b=e['sources'][uid]['building'];rows.append({'uid':uid,'building':b,'candidate':{'path':str(p.resolve()),'entry':entry(chosen[uid],b)},'currentNative':current.get(uid)})
    result={'rows':rows,'errors':errors,'methods':dict(methods),'r2':r2_status,'sourceFallbackEnabled':allow_source,'seconds':round(time.perf_counter()-start,3),'aiCalls':0,'publication':False}
    save(out/'geometry-inputs.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','errors')},sort_keys=True),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,default=HERE/'local/shape-inputs.json.gz');p.add_argument('--out',type=Path,default=HERE/'local/shapes');p.add_argument('--allow-source-download',action='store_true');p.add_argument('--workers',type=int,default=4);p.add_argument('--env-file',type=Path)
    a=p.parse_args();prepare(a.evidence,a.out,a.allow_source_download,a.workers,a.env_file)
