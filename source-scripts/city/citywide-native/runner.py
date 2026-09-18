"""HKS-222 unattended native preparation, bounded disk/workers and shared fenced results."""
import argparse,concurrent.futures,gzip,hashlib,json,multiprocessing,os,pathlib,shutil,sys,tarfile,tempfile,threading,time,uuid
from collections import Counter
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
import store
from source_cache import previous_source_artifacts,restore_original
from download import ac,acquire
sys.path.insert(0,str(HERE.parent/'landmark-resume'))
from r2_snapshot import R2Store,digest,key_for,verify_object
from dotenv import dotenv_values

def code_inputs():
 from convert import converter_dependencies
 return sorted(set(converter_dependencies()+[HERE/'download.py',HERE/'runner.py',HERE/'store.py',HERE/'source_cache.py']))
def fingerprints():
 import numpy,shapely,pyproj
 code={str(p.relative_to(ROOT)):digest(p) for p in code_inputs()}
 versions={'python':list(sys.version_info[:2]),'numpy':numpy.__version__,'shapely':shapely.__version__,'pyproj':pyproj.__version__}
 pipeline=ac.sha(json.dumps([code,versions],sort_keys=True).encode())
 manifest=ac.read(ROOT/'3d-viewer/city/data/manifest.json');paths=[ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/terrain.json']+[ROOT/'3d-viewer'/p['url'] for p in manifest.get('terrainPatches',[])]
 terrain=ac.sha(json.dumps([[str(p.relative_to(ROOT)),digest(p)] for p in paths],sort_keys=True).encode())
 return pipeline,terrain,code,versions,{str(p.relative_to(ROOT)):digest(p) for p in paths}

_worker=None

def initialise(source_artifacts):
 global _worker
 from convert import convert_sheet
 _worker={'convert':convert_sheet,'r2':R2Store('hk-sandbox-assets'),'retained':ac.retained_caches(),'checkedInputs':{},'sourceArtifacts':source_artifacts}

def process(item,token):
 uuid.UUID(token)
 key=store.cache_key(item);folder=HERE/'local/work'/key/token;folder.mkdir(parents=True,exist_ok=True)
 for rel,expected in item['inputs']['code'].items():
  if digest(ROOT/rel)!=expected:raise ValueError('Processing code changed during frozen run')
 for rel,expected in item['inputs']['terrainFiles'].items():
  path=ROOT/rel;stamp=(path.stat().st_size,path.stat().st_mtime_ns)
  if _worker['checkedInputs'].get(rel)!=(stamp,expected):
   assert digest(path)==expected,'Frozen terrain changed';_worker['checkedInputs'][rel]=(stamp,expected)
 row=item['inputs']['plan'];assert digest(ROOT/row['directory'])==item['inputs']['directoryJSONSha256'];directory=ac.read(ROOT/row['directory']);assert digest(ROOT/row['official'])==item['footprintSha256']
 assert ac.sha(json.dumps([directory['sourceURL'],directory['etag'],directory['directorySHA256']],separators=(',',':')).encode())==item['sourceSha256']
 retained=list(_worker['retained'].get(item['sheet'],[]))
 for p in folder.parent.glob('*/original/download.json'):
  try:retained.append((p,ac.read(p)))
  except (OSError,ValueError):pass
 restored_bytes=0
 if not retained and item['sourceSha256'] in _worker['sourceArtifacts']:
  artifact=_worker['sourceArtifacts'][item['sourceSha256']]
  retained.append(restore_original(_worker['r2'],artifact,item['sheet'],folder/'restored-source'))
  restored_bytes=artifact['bytes']
 transfer=folder/'original/transfer.json';before=ac.read(transfer).get('receivedBytes',0) if transfer.exists() else 0
 record=acquire(directory,ROOT/row['rawDirectory'],folder/'original',retained,include_terrain=True)
 transferred=(ac.read(transfer).get('receivedBytes',0) if transfer.exists() else 0)-before
 archive=folder/'original'/(item['sheet']+'.zip');summary=_worker['convert'](archive,record,ROOT/row['official'],folder/'converted')
 if not summary['modelCountMatchesExpected'] or summary['sourceModels']!=row['models']:raise ValueError('Native model count differs from frozen catalogue')
 if ac.read(folder/'converted/terrain-check.json').get('hashes')!=item['inputs']['terrainFiles']:raise RuntimeError('Sampler inputs differ from frozen terrain manifest')
 if summary['terrainStatus']=='unavailable':raise RuntimeError('Runtime terrain sampler unavailable; retry/repair rather than cache success')
 # Keep full outcomes in the artifact and compact queryable records in Neon.
 models=[]
 with (folder/'converted/outcomes.jsonl').open() as stream:
  for line in stream:
   r=json.loads(line);models.append({k:r[k] for k in ('modelId','sourceEntry','state','holdReason','error','worldBounds','vertices','triangles','asset','candidate','matching','terrainCheck') if k in r})
 terrain=ac.read(folder/'converted/terrain-outcomes.json')
 files=[(archive,'original/'+archive.name),(folder/'original/download.json','original/download.json'),(ROOT/row['official'],'official.json.gz'),(ROOT/row['directory'],'directory.json'),(ROOT/row['rawDirectory'],'zip-directory.bin')]
 files += [(p,'converted/'+p.relative_to(folder/'converted').as_posix()) for p in sorted((folder/'converted').rglob('*')) if p.is_file()]
 bundle=folder/'bundle.tar.gz'
 with bundle.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
  for p,name in files:
   info=tarfile.TarInfo(name);info.size=p.stat().st_size;info.mode=0o644
   with p.open('rb') as source:tar.addfile(info,source)
 sha=digest(bundle);remote_key=key_for(sha);_worker['r2'].put(remote_key,bundle)
 with tempfile.TemporaryDirectory(dir=folder) as temp:verify_object(_worker['r2'],remote_key,sha,bundle.stat().st_size,pathlib.Path(temp)/'verified')
 exceptional=sum(n for state,n in summary['outcomes'].items() if state!='packed-needs-placement-review')+sum(n for state,n in summary['terrainOutcomes'].items() if state!='prepared-geometry-only')
 counts={'sourceModels':summary['sourceModels'],'packedAssets':summary['packedAssets'],'candidateModels':summary['candidateModels'],'sourceTerrainModels':summary['sourceTerrainModels'],'sourceBytes':record['bytes'],'transferredBytes':transferred,'restoredR2Bytes':restored_bytes,'artifactBytes':bundle.stat().st_size}
 result={'status':'exceptions' if exceptional else 'prepared','counts':counts,'outcomes':summary['outcomes'],'terrainOutcomes':summary['terrainOutcomes'],'models':models,'terrain':terrain['rows'],'artifacts':[{'key':remote_key,'sha256':sha,'bytes':bundle.stat().st_size,'kind':'original-and-prepared-sheet'}],'qualification':store.QUALIFICATION,'published':False,'placementApproved':False}
 ac.write(folder/'result.json',result);return {'result':result,'folder':str(folder)}

def write_report(run_id,output):
 report=store.report(run_id);results=store.cached_results(run_id);counts=Counter();outcomes=Counter();terrain=Counter()
 # Store API returns validated cache records; retain one bounded complete ledger in R2 later.
 values=results.values() if isinstance(results,dict) else results
 for record in values:
  result=record.get('result',record);counts.update(result.get('counts',{}));outcomes.update(result.get('outcomes',{}));terrain.update(result.get('terrainOutcomes',{}))
 report['sheetOutcomes']=report.pop('outcomes',{})
 report.update(issue='HKS-222',counts=dict(counts),outcomes=dict(outcomes),terrainOutcomes=dict(terrain),aiCalls=0,qualification=store.QUALIFICATION)
 ac.write(output/'summary.json',report)
 (output/'shared-results.json.gz').write_bytes(gzip.compress(json.dumps(results,separators=(',',':')).encode(),mtime=0))
 print(json.dumps(report),flush=True);return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--sheets');p.add_argument('--env-file',type=pathlib.Path,required=True);p.add_argument('--keep-local',action='store_true');p.add_argument('--report-only',action='store_true');a=p.parse_args();assert 1<=a.workers<=8
 for k,v in dotenv_values(a.env_file).items():
  if k.startswith('R2_') and v:os.environ[k]=v
 os.environ.setdefault('CITYWIDE_NODE',shutil.which('node') or 'node');os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
 plan=ac.read(HERE/'local/plan.json');selected=[r for r in plan['sheets'] if not a.sheets or r['sheet'] in a.sheets.split(',')]
 if a.sheets:assert len(selected)==len(set(a.sheets.split(','))),'Unknown/repeated sheet'
 pipeline,terrain,code,versions,terrain_files=fingerprints();items=[{'sheet':r['sheet'],'stage':'native-prepare','sourceSha256':r['sourceSha256'],'pipelineSha256':pipeline,'footprintSha256':r['footprintSha256'],'terrainSha256':terrain,'inputs':{'plan':r,'code':code,'runtime':versions,'terrainFiles':terrain_files,'directoryJSONSha256':digest(ROOT/r['directory']),'terrainGeometry':True,'terrainPhotographs':False}} for r in selected]
 registered=store.register(a.batch,items);run_id=registered['runId'];output=HERE/'local/runs'/run_id;output.mkdir(parents=True,exist_ok=True);ac.write(output/'registration.json',registered);ac.write(output/'inputs.json',items)
 if a.report_only:write_report(run_id,output);return
 source_artifacts=previous_source_artifacts()
 owner='native-'+uuid.uuid4().hex;active={};lock=threading.RLock();stop=threading.Event();lost=threading.Event();failures=Counter();accepted=0
 def renew():
  while not stop.wait(30):
   try:
    with lock:store.heartbeat_many(list(active.values()),lease_seconds=300)
   except Exception:lost.set();return
 pulse=threading.Thread(target=renew,daemon=True);pulse.start()
 try:
  with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('spawn'),initializer=initialise,initargs=(source_artifacts,)) as pool:
   pending={};finished=[]
   while True:
    if lost.is_set():raise RuntimeError('Lease heartbeat lost; no further shared results accepted')
    available=a.workers-len(pending)
    if available:
     if shutil.disk_usage(HERE).free<8*1024**3:raise RuntimeError('Disk floor reached; preserve verified outputs and resume after cleanup')
     with lock:claimed=store.claim_many(run_id,owner,available,lease_seconds=300)
     for job in claimed:
      with lock:active[job['id']]=job
      pending[pool.submit(process,job['item'],str(job['token']))]=job
    if not pending:
     state=store.report(run_id)
     if state['jobs'].get('pending',0) or state['jobs'].get('running',0):
      if stop.wait(15):break
      continue
     break
    done,_=concurrent.futures.wait(pending,timeout=10,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     job=pending.pop(future)
     try:
      value=future.result();finished.append({'job':job,'result':value['result'],'folder':value['folder']})
     except Exception as e:
      failures[job['id']]+=1
      error=type(e).__name__+': '+str(e)[:300];ac.write(output/('failure-'+job['id']+'.json'),{'sheet':job['item']['sheet'],'error':error,'attemptsThisRun':failures[job['id']]})
      with lock:store.fail(job,type(e).__name__.lower(),retry=failures[job['id']]<3);active.pop(job['id'],None)
      print(json.dumps({'failedSheet':job['item']['sheet'],'error':error,'attempt':failures[job['id']]}),flush=True)
    if finished and (len(finished)>=a.workers or not pending):
     with lock:
      store.finish_group([{'job':v['job'],'result':v['result']} for v in finished])
      for v in finished:active.pop(v['job']['id'],None)
     for v in finished:
      receipt={'sheet':v['job']['item']['sheet'],'cacheKey':store.cache_key(v['job']['item']),'artifacts':v['result']['artifacts'],'counts':v['result']['counts']};ac.write(output/'receipts'/(receipt['sheet']+'.json'),receipt)
      if not a.keep_local:shutil.rmtree(v['folder'])
     accepted+=len(finished);print(json.dumps({'acceptedSheetsThisRun':accepted,'registeredSheets':len(items),'lastSheets':[v['job']['item']['sheet'] for v in finished]}),flush=True);finished=[]
 finally:stop.set();pulse.join(timeout=35)
 report=write_report(run_id,output)
 if report['pending']:raise SystemExit('Mechanical preparation incomplete; investigate explicit remaining jobs')
if __name__=='__main__':main()
