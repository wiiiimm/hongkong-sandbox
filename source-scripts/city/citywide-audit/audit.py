#!/usr/bin/env python3
"""Bulk territory audit with immutable shared cache; no acquisition or model publication."""
import argparse,gzip,json,os,pathlib,shutil,subprocess,sys,tempfile,threading,time,uuid
from collections import defaultdict
import store
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read_rows(path):
 with gzip.open(path,'rt')as f:return[json.loads(line)for line in f if line.strip()]
def write_rows(path,rows):
 with open(path,'wb')as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as gz:
   for row in rows:gz.write((json.dumps(row,separators=(',',':'))+'\n').encode())
def run(batch,output,node,chunk_size=8192):
 output=pathlib.Path(output).resolve();output.mkdir(parents=True,exist_ok=True);start=time.monotonic();owner='city-audit-'+uuid.uuid4().hex
 with tempfile.TemporaryDirectory(prefix='audit-',dir=output)as tmp:
  tmp=pathlib.Path(tmp);plan=tmp/'plan.jsonl.gz';meta_path=tmp/'plan.json';subprocess.run([node,str(HERE/'engine.mjs'),'plan',str(plan),str(meta_path)],cwd=ROOT,check=True);meta=json.loads(meta_path.read_text());rows=read_rows(plan)
  canonical=output/meta['runId'];canonical.mkdir(exist_ok=True)
  for path in[plan,meta_path]:
   dest=canonical/path.name
   if dest.exists()and path.name.endswith('.gz')and dest.read_bytes()!=path.read_bytes():raise ValueError('Immutable plan collision')
   if not dest.exists():shutil.copyfile(path,dest)
  registration=store.register(meta,rows,batch,chunk_size);cached=registration['cached'];jobs=[];stop=threading.Event();lost=threading.Event();lock=threading.RLock()
  def pulse():
   while not stop.wait(15):
    try:
     with lock:store.heartbeat_many(jobs)
    except Exception:lost.set();return
  thread=threading.Thread(target=pulse,daemon=True);thread.start();checked=0
  try:
   for _ in registration['chunks']:
    j=store.claim(registration['batch'],owner,[store.STAGE],lease_seconds=300)
    if not j:break
    with lock:jobs.append(j)
   chunks={j['payload']['chunk']for j in jobs};owned={u for u,_,ch,_ in registration['members']if ch in chunks};requested=[r for r in rows if r['uid']in owned and r['uid']not in cached]
   if requested:
    request=tmp/'requests.jsonl.gz';result_path=tmp/'results.jsonl.gz';write_rows(request,requested)
    process=subprocess.Popen([node,str(HERE/'engine.mjs'),'compute',str(result_path),str(request)],cwd=ROOT)
    try:
     while process.poll()is None:
      if lost.wait(.5):process.terminate();raise ValueError('Chunk lease renewal lost')
     if process.returncode:raise ValueError('Audit engine failed; no results accepted')
    finally:
     if process.poll()is None:
      process.terminate()
      try:process.wait(timeout=5)
      except subprocess.TimeoutExpired:process.kill();process.wait()
    by_uid={r['uid']:r for r in read_rows(result_path)};by_chunk=defaultdict(list)
    for uid,_,ch,_ in registration['members']:
     if uid in by_uid:by_chunk[ch].append(by_uid[uid])
    pending=list(jobs)
    for offset in range(0,len(pending),8):
     group=pending[offset:offset+8]
     if lost.is_set():raise ValueError('Chunk lease lost before result publication')
     with lock:
      checked+=store.finish_group(group,[r for j in group for r in by_chunk[j['payload']['chunk']]])
      for j in group:jobs.remove(j)
    shutil.copyfile(result_path,canonical/('results-'+uuid.uuid4().hex+'.jsonl.gz'))
   else:
    for j in list(jobs):
     with lock:store.finish_chunk(j,[]);jobs.remove(j)
  finally:stop.set();thread.join()
  result=store.report(meta['runId']);result.update(issue='HKS-221',batch=batch,reusedAtStart=len(cached),newlyAudited=checked,seconds=round(time.monotonic()-start,3),tiles=meta['tiles'],pipelineSha=meta['pipelineSha'],scope=meta['scope'],limits=['Finite footprint boundary/midpoint/interior-centre samples; not exhaustive terrain intersection.','Native asset identity and local SHA availability only; native triangles, collision, architecture and visual acceptance not checked.','No source acquisition, model publication, model-review ledger updates or AI calls.','Terrain dependency hashes include root terrain plus intersecting ordered patches; unrelated sibling patches are excluded.'])
  report=canonical/('run-'+uuid.uuid4().hex+'.json');report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result,report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['migrate','run','report']);p.add_argument('--batch');p.add_argument('--run-id');p.add_argument('--out',default=str(HERE/'local'));p.add_argument('--node',default=os.getenv('NODE',shutil.which('node')));p.add_argument('--chunk-size',type=int,default=8192);a=p.parse_args()
 if a.command=='migrate':store.migrate();print('Scoped city audit schema ready')
 elif a.command=='report':print(json.dumps(store.report(a.run_id),indent=2))
 else:
  if not a.batch or not a.node:p.error('run requires batch and Node runtime')
  result,_=run(a.batch,a.out,a.node,a.chunk_size)
  if result['missing']:raise SystemExit('Audit incomplete; resume the same inputs after outstanding chunk leases finish/expire')
if __name__=='__main__':main()
