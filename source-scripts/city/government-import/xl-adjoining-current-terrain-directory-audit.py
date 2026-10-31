"""Refresh only adjoining directory metadata missing from the bounded XL audit."""
import sys,uuid,json,importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from run import ROOT,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
DIR=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import'
sys.path.insert(0,str(DIR.parent/'citywide-source'))
from discover import scan
BATCH='government-xl-adjoining-current-terrain-directory-audit-20261007'
PREVIEWS=['government-xl-remaining-historical-current-tin-preview-20261007','government-xl-refreshed-current-tin-preview-20261007']
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 doc=BASE/BATCH;local=DIR/'local'/BATCH;assert not doc.exists();routes={};uids=set();refs=[]
 for name in PREVIEWS:
  p=BASE/name/'result.json';d=read(p);refs.append(ref(p))
  for r in d['rows']:
   for sheet in r['unavailableCurrentTerrainSheets']:routes.setdefault(sheet,set()).add(r['uid']);uids.add(r['uid'])
 assert len(routes)==11 and len(uids)==10
 spec=importlib.util.spec_from_file_location('adjoining_receipts',DIR/'xl-cell-indexed-terrain-continuation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');old=dict(con.execute('SELECT DISTINCT ON(sheet) sheet,result FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC',(sorted(routes),)).fetchall())
 assert set(old)==set(routes)
 claim=reservations.claim('codex-adjoining-directory-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)],batch=BATCH);assert claim['ok'];lease=claim['reservation']
 try:
  save(doc/'inputs.json',{'routes':{s:sorted(u) for s,u in routes.items()},'oldDirectories':old,'evidenceRefs':refs,'runner':ref(Path(__file__))})
  def inspect(sheet):
   prior=old[sheet];current,_=scan({'SHEETNO':sheet,'Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},local/'sheets'/sheet/'directory',refresh=True)
   cached=[]
   for folder in sorted((DIR/'local').glob('*/sheets/'+sheet)):
    proof=m.verified_terrain(folder)
    if proof and proof[0]['directorySHA256']==current['directorySHA256']:
     cached.append({'cache':str(folder.relative_to(ROOT)),'receipt':ref(folder/'original/download.json'),'terrainFiles':proof[1]})
   return {'sheet':sheet,'uids':sorted(routes[sheet]),'directorySHA256':current['directorySHA256'],'currentDirectory':ref(local/'sheets'/sheet/'directory/result.json'),'matchingCompleteCaches':cached,'transferredModelPayloads':0}
  rows=[]
  with ThreadPoolExecutor(max_workers=4) as pool:
   for future in as_completed([pool.submit(inspect,s) for s in sorted(routes)]):
    r=future.result();rows.append(r);assert reservations.owns(lease);print(json.dumps({'sheet':r['sheet'],'completeCurrentCaches':len(r['matchingCompleteCaches'])}),flush=True)
  rows.sort(key=lambda r:r['sheet']);save(doc/'directories.json',{'rows':rows,'publication':False})
  refs.extend([ref(doc/'inputs.json'),ref(doc/'directories.json'),ref(Path(__file__)),ref(DIR.parent/'citywide-source/discover.py'),ref(DIR/'xl-cell-indexed-terrain-continuation.py')]);refs.extend(r['currentDirectory'] for r in rows)
  payload={'uids':sorted(uids),'evidenceRefs':refs};stage='bounded-adjoining-current-terrain-directory-audit-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':rows,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'downloadedModelPayloads':0,'qualification':'Current official directory hashes and complete original cached TIN files only; no acceptance or review credit.'}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for e in refs:assert ref(ROOT/e['path'])==e
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'sheets':len(rows)},flush=True)
 finally:reservations.release(lease)
if __name__=='__main__':main()
