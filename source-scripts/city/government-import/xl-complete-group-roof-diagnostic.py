"""Measure component-specific upper coverage for the 22 complete-parent candidates.

Shared footprint and global maximum height cannot prove a tower is contained.
This adds evidence only; all current detail and acceptance gates remain intact.
"""
import importlib.util,json,subprocess,sys,uuid,math
from pathlib import Path
from collections import Counter
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
from component_roof_coverage import measure
BATCH='government-xl-22-component-roof-coverage-20261008'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 previous=read(SOURCE/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
 for item in previous['evidenceRefs']:assert ref(ROOT/item['path'])==item
 selection=read(SOURCE/'physical-selection.json.gz');contexts={r['uid']:r for r in read(SOURCE/'context.json.gz')['rows']}
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
 decoder=module('component_roof_original_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
 rows=[];refs=[ref(Path(__file__)),ref(HERE/'component_roof_coverage.py'),ref(HERE/'test_component_roof_coverage.py')]+[ref(SOURCE/f) for f in ['result.json','physical-selection.json.gz','context.json.gz','official-context.json']]
 for row in selection['rows']:
  uid=row['uid'];context=contexts[uid]
  for path,sha in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==sha
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(ref(ROOT/row['candidate']['path']))
  asset=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
  triangles=decoder.glb_triangles(row);components=[]
  for form in context['groupForms']:
   top=form.get('topHeightHKPD');component={'uid':form['uid'],'name':form.get('name'),'recordedTopHeightHKPD':top,'target':form['uid']==uid,'suppressionApproved':False}
   if isinstance(top,(int,float)) and math.isfinite(top):
    # Half-metre plane is an explicit diagnostic comparison only, not an acceptance tolerance.
    measured=measure(triangles,Polygon(form['rings'][0],form['rings'][1:]),top-.5)
    component.update(measurement=measured,assessment='upper-source-coverage-present-review-required' if measured['coveredFraction']>=.95 else 'upper-source-coverage-incomplete-retain-current-form')
   else:component.update(assessment='official-height-missing-retain-current-until-component-proof')
   components.append(component)
  r={'uid':uid,'sourceSHA256':row['sourceSHA256'],'components':components,'identityAccepted':False,'installationApproved':False,'suppressionApproved':False,'newlyInstalled':0}
  rows.append(r);save(DOC/(uid.split('/')[1].replace(':','-')+'.json'),r)
  assert reservations.heartbeat(lease,ttl=3600)['ok'];print(json.dumps({'uid':uid,'components':len(components)}),flush=True)
 save(DOC/'measurements.json.gz',{'rows':rows,'publication':False,'modelGeometryChanges':0})
 refs.append(ref(DOC/'measurements.json.gz'));refs=list({r['path']:r for r in refs}.values())
 counts=dict(Counter(c['assessment'] for r in rows for c in r['components']))
 payload={'uids':[r['uid'] for r in rows],'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows},'contextJobId':previous['jobId'],'evidenceRefs':refs}
 stage='complete-parent-component-upper-coverage-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':BATCH,'models':len(rows),'componentCounts':counts,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceIdentityReviewUsedAI':False,'qualification':'Exact analytic height-plane projection of unchanged originals, per official component footprint. Missing upper coverage or height metadata retains existing forms. High coverage is evidence for later review, not complete model ownership, suppression, physical acceptance or installation.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for item in refs:assert ref(ROOT/item['path'])==item
  assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'models':len(rows),'componentCounts':counts,'neonVerified':True}),flush=True)
if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not DOC.exists() and not LOCAL.exists()
  claim=reservations.claim('codex-component-roof-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
