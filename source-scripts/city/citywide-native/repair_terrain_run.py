"""Repair failed native terrain only, after a completed frozen preparation run."""
import argparse
import concurrent.futures
from collections import Counter
import datetime
import gzip
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import threading
import time
import uuid
import zipfile
import numpy as np
from dotenv import dotenv_values
import store
from source_cache import restore_original
from terrain_repair import repair_model,safe_uri
from r2_snapshot import R2Store,digest,key_for,verify_object

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]


def repair_inputs(original_run):
    status=store.report(original_run)
    if status['pending']:raise ValueError('Original frozen run must complete before terrain repair')
    paths=[Path(__file__),HERE/'terrain_repair.py',HERE/'source_cache.py',HERE/'store.py',HERE.parent/'landmark-resume/r2_snapshot.py']
    code={str(p.relative_to(ROOT)):digest(p)for p in paths}
    pipeline=store.digest({'code':code,'numpy':np.__version__,'python':list(sys.version_info[:2]),'version':1})
    with store.connect()as con:
        con.execute('SET TRANSACTION READ ONLY')
        rows=con.execute('''SELECT i.cache_key,i.sheet,i.source_sha,i.footprint_sha,
            r.result->'terrain',r.result->'artifacts' FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            WHERE m.run_id=%s ORDER BY i.sheet''',(original_run,)).fetchall()
    items=[]
    for key,sheet,source,footprint,terrain,artifacts in rows:
        selected=sorted({r['sourceEntry']for r in terrain or[]if r['state']=='failed'})
        if not selected:continue
        candidates=[a for a in artifacts if a['kind']=='original-and-prepared-sheet']
        if len(candidates)!=1:raise ValueError('Original source bundle is not unique')
        items.append({'sheet':sheet,'stage':'native-terrain-repair','sourceSha256':source,'pipelineSha256':pipeline,'footprintSha256':footprint,'terrainSha256':None,
            'inputs':{'originalCacheKey':key,'originalArtifact':candidates[0],'sourceEntries':selected,'code':code,'geometryOnly':True,'version':1}})
    return items


def process(item,token,r2):
    uuid.UUID(token);folder=HERE/'local/terrain-repair/work'/store.cache_key(item)/token;folder.mkdir(parents=True,exist_ok=True)
    for rel,expected in item['inputs']['code'].items():
        if digest(ROOT/rel)!=expected:raise ValueError('Frozen repair pipeline changed')
    record_path,record=restore_original(r2,item['inputs']['originalArtifact'],item['sheet'],folder/'original')
    expected_source=store.digest([record['source'],record['sourceETag'],record['directorySHA256']])
    if expected_source!=item['sourceSha256']:raise ValueError('Restored source revision differs from repair input')
    output=folder/'repaired';output.mkdir(exist_ok=True);rows=[]
    with zipfile.ZipFile(record_path.parent/(item['sheet']+'.zip'))as z:
        names=Counter(z.namelist())
        for source_entry in item['inputs']['sourceEntries']:
            safe_uri(source_entry);model_id=Path(source_entry).stem;relative=Path(store.digest(source_entry)[:24]);dest=output/relative;dest.mkdir(exist_ok=True)
            row={'sourceEntry':source_entry,'modelId':model_id,'state':'failed','published':False,'placementApproved':False}
            try:
                if names[source_entry]!=1:raise ValueError('Missing or duplicate original terrain entry')
                raw=z.read(source_entry);source_folder=Path(source_entry).parent
                def read_buffer(uri):
                    name=(source_folder/str(safe_uri(uri))).as_posix()
                    if names[name]!=1:raise ValueError('Missing or duplicate terrain binary')
                    return z.read(name)
                result=repair_model(raw,read_buffer)
                (dest/'original.gltf').write_bytes(raw)
                for uri,value in result.pop('files').items():
                    path=dest/str(safe_uri(uri));path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
                row.update(result)
                row['sourceHashes']={(source_entry if k=='source.gltf'else(source_folder/k).as_posix()):v for k,v in row['sourceHashes'].items()}
                row['preparedFiles']=[{'path':p.relative_to(output).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size}for p in sorted(dest.rglob('*'))if p.is_file()]
            except (ValueError,KeyError,IndexError,TypeError,AssertionError)as error:
                row['error']=type(error).__name__+': '+str(error)
            rows.append(row)
    result={'status':'exceptions'if any(r['state']=='failed'for r in rows)else'source-empty'if all(r['state']=='source-empty'for r in rows)else'prepared',
        'counts':{'sourceTerrainModels':len(rows),'preparedTerrainModels':sum(r['state']=='prepared-geometry-only'for r in rows),'emptyTerrainModels':sum(r['state']=='source-empty'for r in rows),'failedTerrainModels':sum(r['state']=='failed'for r in rows)},
        'models':[],'terrain':rows,'qualification':store.QUALIFICATION,'originalCacheKey':item['inputs']['originalCacheKey'],'originalSourceArtifact':item['inputs']['originalArtifact'],'published':False,'placementApproved':False}
    (output/'outcomes.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    bundle=folder/'terrain-repair.tar.gz'
    with bundle.open('wb')as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='')as gz,tarfile.open(fileobj=gz,mode='w|')as tar:
        for path in sorted(output.rglob('*')):
            if not path.is_file():continue
            info=tarfile.TarInfo(path.relative_to(output).as_posix());info.size=path.stat().st_size;info.mode=0o644
            with path.open('rb')as source:tar.addfile(info,source)
    sha=digest(bundle);key=key_for(sha);r2.put(key,bundle)
    with tempfile.TemporaryDirectory(dir=folder)as temp:verify_object(r2,key,sha,bundle.stat().st_size,Path(temp)/'verified')
    result['artifacts']=[{'key':key,'sha256':sha,'bytes':bundle.stat().st_size,'kind':'terrain-repair-sheet'}]
    return result,folder


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--original-run',required=True);parser.add_argument('--batch',required=True);parser.add_argument('--env-file',type=Path,required=True);parser.add_argument('--workers',type=int,default=6);parser.add_argument('--report-only',action='store_true');args=parser.parse_args()
    if not 1<=args.workers<=8:raise ValueError('Workers must be 1..8')
    for key,value in dotenv_values(args.env_file).items():
        if key.startswith('R2_')and value:os.environ[key]=value
    items=repair_inputs(args.original_run)
    if not items:print(json.dumps({'originalRunId':args.original_run,'failedTerrainSheets':0}));return
    registration=store.register(args.batch,items);run_id=registration['runId'];out=HERE/'local/terrain-repair/runs'/run_id;out.mkdir(parents=True,exist_ok=True)
    (out/'inputs.json').write_text(json.dumps(items,separators=(',',':'))+'\n')
    print(json.dumps({'repairRunId':run_id,'originalRunId':args.original_run,**registration}),flush=True)
    if not args.report_only:
        owner='terrain-repair-'+uuid.uuid4().hex;active={};lock=threading.RLock();stop=threading.Event();lost=threading.Event()
        def renew():
            while not stop.wait(30):
                try:
                    with lock:store.heartbeat_many(list(active.values()))
                except Exception:lost.set();return
        pulse=threading.Thread(target=renew,daemon=True);pulse.start();r2=R2Store('hk-sandbox-assets')
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)as pool:
                while True:
                    if lost.is_set():raise RuntimeError('Repair lease ownership lost')
                    with lock:
                        jobs=store.claim_many(run_id,owner,args.workers)
                        active.update({j['id']:j for j in jobs})
                    if not jobs:
                        state=store.report(run_id)
                        if state['jobs'].get('pending',0)or state['jobs'].get('running',0):stop.wait(10);continue
                        break
                    futures={pool.submit(process,j['item'],str(j['token']),r2):j for j in jobs};completed=[]
                    for future in concurrent.futures.as_completed(futures):
                        job=futures[future]
                        try:
                            result,folder=future.result();completed.append({'job':job,'result':result,'folder':folder})
                        except Exception as error:
                            with lock:store.fail(job,type(error).__name__.lower(),retry=True);active.pop(job['id'],None)
                            print(json.dumps({'sheet':job['item']['sheet'],'retryableErrorType':type(error).__name__}),flush=True)
                    if lost.is_set():raise RuntimeError('Repair lease ownership lost before completion')
                    if completed:
                        with lock:
                            store.finish_group([{'job':v['job'],'result':v['result']}for v in completed])
                            for v in completed:active.pop(v['job']['id'],None)
                        for v in completed:shutil.rmtree(v['folder'])
                        print(json.dumps({'completedSheets':[v['job']['item']['sheet']for v in completed]}),flush=True)
        finally:stop.set();pulse.join(timeout=35)
    report=store.report(run_id);results=store.cached_results(run_id);counts=Counter()
    for row in results:counts.update(row['result']['counts'])
    report.update(issue='HKS-222',originalRunId=args.original_run,repairRunId=run_id,counts=dict(counts),aiCalls=0,published=False,qualification=store.QUALIFICATION,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');(out/'results.json.gz').write_bytes(gzip.compress(json.dumps(results,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(report),flush=True)
    if report['pending']:raise SystemExit('Repair incomplete; explicit retries or failed jobs remain')
if __name__=='__main__':main()
