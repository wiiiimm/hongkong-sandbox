"""Read-only refinement progress: current job sets, installed IDs and held candidates.
No processing, downloads, AI calls or publication. Historical job rows are separate.
"""
import argparse,collections,datetime,gzip,hashlib,json,pathlib,sqlite3,time
ROOT=pathlib.Path(__file__).resolve().parents[3]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def snapshot(root,db):
 started=time.monotonic();c=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
 try:
  mismatches=[]
  for path,expected in c.execute('select path,sha256 from inputs'):
   p=root/'3d-viewer'/path
   if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:mismatches.append(path)
  if mismatches:raise ValueError('Inventory stale; run inventory.py first: '+', '.join(mismatches[:8]))
  active=c.execute('select count(*) from buildings where active=1').fetchone()[0];embedded={r[0] for r in c.execute('select uid from buildings where active=1 and embedded=1')};progressive={r[0] for r in c.execute('select uid from models')};installed=embedded|progressive
  sets={}
  for name,status,n in c.execute('select s.name,j.status,count(*) from batch_job_sets s join batch_jobs j on j.id=s.id group by s.name,j.status'):sets.setdefault(name,{})[status]=n
  historical=dict(c.execute('select status,count(*) from batch_jobs j where not exists(select 1 from batch_job_sets s where s.id=j.id) group by status'))
  old=read(root/'docs/astra-city/building-batch/cached-models/catalogue.json.gz');uids={m['uid'] for m in old['models']}
  a=read(root/'source-scripts/city/architecture-batch/acceptance.json');selection=read(root/'source-scripts/city/architecture-batch/selection.json');selected={u for g in selection['groups'] for u in g['uids']};prepared=read(root/'source-scripts/city/architecture-batch/report.json');outcomes=collections.Counter(r['outcome'] for r in prepared['results']);confirmed=set(a['accepted'])&installed
  assert len(confirmed)==len(a['accepted']),'Approved architecture models are missing from inventory'
  return {'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inventoryInputsVerified':True,'currentJobSets':sets,'unreferencedHistoricalJobs':historical,'inventory':{'buildingForms':active,'embeddedDetailed':len(embedded),'progressiveDetailed':len(progressive),'uniqueDetailed':len(installed)},'originalCachedTrial':{'preparedCandidates':len(uids),'installedNow':len(uids&installed),'notInstalledNow':len(uids-installed),'qualification':'Uninstalled is not missing source data or an automatic placement rejection; inspect source/terrain evidence.'},'architectureBatch1':{'selectedSourceParts':len(selected),'approvedInstalled':len(confirmed),'priorDetailed':outcomes['already-detailed'],'placementHolds':a['held'],'sourceMatchCases':outcomes['no-standard-match-in-cache'],'issue':'HKS-208','followup':'HKS-209'},'seconds':round(time.monotonic()-started,3),'aiCalls':0,'networkRequests':0,'limits':['Current sets exclude superseded jobs; historical pending entries do not constitute a runnable current queue.','Complete conversion jobs are not published buildings or region acceptance.','Job states are ledger observations, not operating-system process monitoring.','No geometry, terrain, inventory or job state was changed.']}
 finally:c.close()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--db',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);a=p.parse_args();d=snapshot(a.root,a.db or a.root/'source-scripts/city/building-batch/local/buildings.sqlite');text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
 print(text,end='')
