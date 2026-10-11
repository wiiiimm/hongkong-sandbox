"""HKS-221: inspect government ZIP directories, without downloading model payloads or calling AI."""
import argparse,concurrent.futures,gzip,hashlib,importlib.util,json,os,re,struct,sys,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'))
from db import connect
import reservations
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
spec=importlib.util.spec_from_file_location('existing_acquisition',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');ac=importlib.util.module_from_spec(spec);spec.loader.exec_module(ac)
def sha(value):return hashlib.sha256(value).hexdigest()
def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def cache_key(index_sha,pipeline,r):return sha(encode([r.get('sourceURL'),r.get('revision'),r['sheet'],r['etag'],r['directorySHA256'],pipeline]))
def models(infos):
 result={};by_folder={}
 for entry in infos:by_folder.setdefault(str(Path(entry.filename).parent),[]).append(entry)
 for e in infos:
  match=re.fullmatch(r'BUILDING/(B(\d{10})(01|02)06[0-9A-Z]{3})/\1\.gltf',e.filename,re.I)
  if not match:continue
  model=match[1];prefix='BUILDING/'+model+'/'
  members=[x for x in by_folder.get(prefix.rstrip('/'),[]) if x.filename.endswith(('.gltf','.bin'))]
  result[model]={'modelId':model,'geoRefNo':match[2],'subtype':match[3],'compressedBytes':sum(x.compress_size for x in members),'decodedBytes':sum(x.file_size for x in members),'members':[{'name':x.filename,'crc32':x.CRC,'compressedBytes':x.compress_size,'decodedBytes':x.file_size,'headerOffset':x.header_offset} for x in members]}
 return list(result.values())
def scan(attrs,folder,refresh=False):
 folder.mkdir(parents=True,exist_ok=True);out=folder/'result.json';url=attrs['Format_glTF'];revision=attrs['REVISIONDATE']
 assert url.startswith('https://download.map.gov.hk/'),'Unexpected government archive host'
 if out.exists() and not refresh:
  r=ac.read(out)
  if r.get('status')=='directory-verified' and r['revision']==revision and r['sourceURL']==url:
   raw=(folder/'zip-directory.bin').read_bytes();assert sha(raw)==r['directorySHA256'];infos,check=ac.parse_directory(raw)
   r['models']=models(infos);return r,True
 net=ac.Network(folder/'transfer.json',cap=8_000_000)
 _,headers=net.get(url,0,method='HEAD');etag=headers.get('ETag');size=int(headers['Content-Length']);assert etag
 raw=None
 # Reuse a prior exact revision/ETag directory without fetching native payloads.
 for old in RETAINED.get(attrs['SHEETNO'],[]):
  p,record=old
  if record.get('source')==url and record.get('sourceETag')==etag and record.get('revisionDate')==ac.datetime.datetime.fromtimestamp(revision/1000,ac.datetime.timezone.utc).isoformat():
   q=p.parent/'zip-directory.bin'
   if q.exists():raw=q.read_bytes();ac.parse_directory(raw);break
 if raw is None:
  tail,h=net.get(url,65536,'-65536',etag);end=tail.rfind(b'PK\x05\x06');assert end>=0
  fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(h['Content-Range'].split()[1].split('-')[0]);assert int(h['Content-Range'].split('/')[-1])==size
  if offset<start:
   prefix,_=net.get(url,start-offset,f'{offset}-{start-1}',etag);raw=prefix+tail
  else:raw=tail[offset-start:]
 infos,check=ac.parse_directory(raw);(folder/'zip-directory.bin').write_bytes(raw)
 r={'sheet':attrs['SHEETNO'],'sourceURL':url,'revision':revision,'etag':etag,'archiveBytes':size,'status':'directory-verified',**check,'models':models(infos),'receivedBytes':net.data['receivedBytes'],'checkedAt':ac.now()}
 ac.write(out,r);return r,False
RETAINED={}
SCHEMA='''CREATE TABLE IF NOT EXISTS astra_modelling.city_source_directories (
 cache_key text PRIMARY KEY,index_sha text NOT NULL,sheet text NOT NULL,result jsonb NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE astra_modelling.city_source_directories ADD COLUMN IF NOT EXISTS pipeline_sha text;
CREATE INDEX IF NOT EXISTS city_source_directory_pipeline ON astra_modelling.city_source_directories(pipeline_sha);
CREATE TABLE IF NOT EXISTS astra_modelling.city_source_discovery_runs (
 id text PRIMARY KEY,index_sha text NOT NULL,pipeline_sha text NOT NULL,status text NOT NULL,summary jsonb NOT NULL,updated_at timestamptz NOT NULL DEFAULT now());'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--limit',type=int);p.add_argument('--refresh-head',action='store_true');p.add_argument('--max-mb',type=int,default=512);a=p.parse_args()
 assert 1<=a.workers<=8 and a.max_mb>0
 index_path=ROOT/a.index;raw=index_path.read_bytes();data=json.loads(gzip.decompress(raw) if index_path.suffix=='.gz' else raw);features=data['features'];assert data['completePagination'] and len({x['attributes']['OBJECTID'] for x in features})==len(features)
 pipeline=sha(Path(__file__).read_bytes()+(ROOT/'source-scripts/city/landmark-acquisition/acquire.py').read_bytes());index_sha=sha(raw);run=sha(encode([index_sha,pipeline]));cache=HERE/'cache'/index_sha[:16];cache.mkdir(parents=True,exist_ok=True)
 claim=reservations.claim('city-source-'+str(os.getpid()),['source-directory-index:'+index_sha],ttl=1800,batch='HKS-221-source-discovery');assert claim['ok'],'Source discovery owned by another session';receipt=claim['reservation'];stop=threading.Event();lost=threading.Event()
 def renew():
  while not stop.wait(240):
   try:
    if not reservations.heartbeat(receipt,1800).get('ok'):lost.set();return
   except Exception:lost.set();return
 thread=threading.Thread(target=renew,daemon=True);thread.start()
 global RETAINED;RETAINED=ac.retained_caches();results=[];reused=0;errors=[]
 with connect() as con:
  con.execute(SCHEMA)
  prior=con.execute('SELECT cache_key,result FROM astra_modelling.city_source_directories WHERE pipeline_sha=%s',(pipeline,)).fetchall()
 shared={r['sheet']:r for key,r in prior if key==cache_key(index_sha,pipeline,r)}

 def save(status):
  summary={'sourceSheets':len(features),'checkedSheets':len(results),'reusedSheets':reused,'failedSheets':errors,'directoryListedModels':sum(len(r['models']) for r in results),'nativeModelMemberRequests':0,'nativeModelsAcquired':0,'aiCalls':0,'qualification':'Directory listing only. Geometry, exact footprint matching, terrain placement and visual acceptance not performed. Not-found is not source-unavailable while any sheet remains unchecked.'}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert not lost.is_set() and reservations._current(con,receipt),'Lost source discovery ownership'
   with con.cursor() as cur:
    cur.executemany('INSERT INTO astra_modelling.city_source_directories(cache_key,index_sha,sheet,pipeline_sha,result) VALUES(%s,%s,%s,%s,%s) ON CONFLICT(cache_key) DO NOTHING',[(cache_key(index_sha,pipeline,r),index_sha,r['sheet'],pipeline,Jsonb(r)) for r in results[-100:]])
   con.execute('INSERT INTO astra_modelling.city_source_discovery_runs(id,index_sha,pipeline_sha,status,summary) VALUES(%s,%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET status=EXCLUDED.status,summary=EXCLUDED.summary,updated_at=now()',(run,index_sha,pipeline,status,Jsonb(summary)))
  return summary
 # Reserve conservative per-sheet directory allowance; never fetch full ZIPs when ranges fail.
 allowance=a.max_mb*1_000_000;selected=features[:a.limit] if a.limit else features
 def work(f):
  attrs=f['attributes'];sheet=attrs['SHEETNO'];assert re.fullmatch(r'[0-9A-Za-z-]+',sheet)
  if lost.is_set():raise RuntimeError('Lease lost')
  if not a.refresh_head and sheet in shared and shared[sheet]['revision']==attrs['REVISIONDATE'] and shared[sheet]['sourceURL']==attrs['Format_glTF']:return shared[sheet],True
  return scan(attrs,cache/sheet,a.refresh_head)
 try:
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
   pending={};iterator=iter(selected);charges={q.parent.name:ac.read(q).get('chargedBytes',0) for q in cache.glob('*/transfer.json')};charged=sum(charges.values());reserved=0
   while True:
    while len(pending)<a.workers and charged+reserved+8_000_000<=allowance and not lost.is_set():
     f=next(iterator,None)
     if f is None:break
     future=pool.submit(work,f);pending[future]=f['attributes']['SHEETNO'];reserved+=8_000_000
    if not pending:break
    done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     sheet=pending.pop(future);reserved-=8_000_000
     try:r,hit=future.result();results.append(r);reused+=hit
     except Exception as e:errors.append({'sheet':sheet,'error':type(e).__name__+': '+str(e)[:180]})
     q=cache/sheet/'transfer.json';new_charge=ac.read(q).get('chargedBytes',0) if q.exists() else 0;charged+=new_charge-charges.get(sheet,0);charges[sheet]=new_charge
     if (len(results)+len(errors))%100==0:print(json.dumps({k:v for k,v in save('running').items() if k not in ('failedSheets','qualification')}),flush=True)
  status='complete' if len(results)==len(features) and not errors else 'partial'
  summary=save(status);summary.update(runId=run,status=status,receivedBytes=sum(ac.read(q).get('receivedBytes',0) for q in cache.glob('*/transfer.json')),chargedBytes=charged,indexSHA256=index_sha,pipelineSHA256=pipeline,indexCheckedAt=data.get('checkedAt'))
  doc=ROOT/'docs/astra-city/citywide-source';doc.mkdir(parents=True,exist_ok=True);ac.write(doc/'summary.json',summary);(doc/'directories.json.gz').write_bytes(gzip.compress(encode({'summary':summary,'directories':results}),mtime=0));print(json.dumps(summary),flush=True)
 finally:stop.set();thread.join(timeout=1);reservations.release(receipt)
if __name__=='__main__':main()
