"""Audit exact GeoRef/type companion names in complete cached archive directories.

A companion is only a diagnostic lead. It grants no source ownership, assembly,
new-version identity or publication approval and is never automatic skip credit.
"""
import json,uuid
from pathlib import Path
from collections import defaultdict
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
BATCH='government-xl-original-sibling-archive-audit-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=ROOT/'docs/astra-city/government-import'
SCOPE=BASE/'government-xl-current-320-blocker-families-20261009/dispositions.json.gz'
MEASURE=HERE/'local/government-xl-pier8-successor-direct-group-20261009/diagnostic.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists(),'Fresh audit phase required'
 scope=read(SCOPE);prefixes={r['modelId'][:13] for r in scope['rows']}
 seen=set();found=defaultdict(list);directory_refs=[]
 for p in sorted((HERE/'local').glob('**/directory/result.json')):
  d=read(p);h=d.get('directorySHA256')
  if not h or h in seen:continue
  seen.add(h);directory_refs.append(ref(p))
  for m in d.get('models',[]):
   if m.get('modelId','')[:13] in prefixes:
    found[m['modelId'][:13]].append({'modelId':m['modelId'],'sheet':d.get('sheet'),'revision':d.get('revision'),'directorySHA256':h,'directoryReceipt':ref(p)})
 rows=[]
 for source in scope['rows']:
  siblings=[m for m in found.get(source['modelId'][:13],[]) if m['modelId']!=source['modelId']]
  if siblings:rows.append({'uid':source['uid'],'indexedModelId':source['modelId'],'indexedSourceSHA256':source['sourceSHA256'],'sourceKey':source['sourceKey'],'siblings':siblings})
 assert len(rows)==1 and rows[0]['uid']=='landsd/213352:0'
 assert {m['modelId'] for m in rows[0]['siblings']}=={'B347431642801063C1'}
 measure=read(MEASURE);assert measure['uid']=='landsd/213352:0' and measure['modelId']=='B347431642801063C1'
 for path,h in measure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 assert len(measure['groupForms'])==1 and measure['groupForms'][0]['uid']==measure['uid']
 assert measure['measurements']['sourceExcessMaximumDistanceFromTargetM']>10
 identity=read(BASE/'government-xl-central-piers-current-identity-20261007/result.json')
 acquisition=read(BASE/'government-xl-central-piers-current-originals-20261007/result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [identity,acquisition]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 save(DOC/'cached-companions.json',{'rows':rows,'scope':320,'uniqueHistoricalDirectoryHashes':len(seen),'directoryReceipts':directory_refs,'qualification':'Cached directory inventory, not a fresh government index claim. Same prefix does not establish component complementarity or assembly ownership.'})
 save(DOC/'pier8-current-direct-group.json',measure)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==scope['manifestSHA256']
 refs=[ref(p) for p in [Path(__file__),SCOPE,MEASURE,DOC/'cached-companions.json',DOC/'pier8-current-direct-group.json',BASE/'government-xl-central-piers-current-identity-20261007/result.json',BASE/'government-xl-central-piers-current-originals-20261007/result.json',manifest]]
 refs += [{'path':path,'sha256':h} for path,h in measure['inputHashes'].items()]
 claim=reservations.claim('codex-xl-source-companions-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'evidenceRefs':refs,'sourceScope':320};stage='cached-original-companion-inventory-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'uniqueHistoricalDirectories':len(seen),'sourcesWithCompanionNames':1,'uninvestigatedCompanions':0,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'aiGeometryModelling':False,'companionUid':'landsd/213352:0','sourceSHA256':measure['sourceSHA256'],'completeDirectGroupMeasures':measure['measurements'],'reasons':['known-current-successor-extent-over-10m','no-additional-current-direct-shared-osm-form'],'qualification':'The only companion is already separately acquired Central Pier 8 C1. Fresh complete direct-OSM group contains only its own form, so the 13.6326m source extent failure remains. Old C0 member absence and new C1 identity failure are separate source-version facts; neither is waived, corrupt nor installed.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs+directory_refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'directories':len(seen),'uninvestigatedCompanions':0,'newlyInstalled':0}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
