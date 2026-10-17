"""Prepare fresh official/current component context and original captures for XL groups.

Diagnostics only. Shared 2D coverage never establishes complete tower ownership,
suppression, identity, physical acceptance or installation.
"""
import argparse,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
sys.path.insert(0,str(HERE.parent/'mui-wo-buildings'))
from build import official_geometry,polys
from shapely.geometry import Polygon

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def owned(a,doc,local):
 lease=read(local/'reservation.json');assert reservations.owns(lease)
 scan=ROOT/a.scan;previous=read(scan/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(previous['jobId'],)).fetchone()==('complete',previous)
 for item in previous['evidenceRefs']:assert ref(ROOT/item['path'])==item
 candidates=[r for r in read(scan/'outcomes.json.gz')['rows'] if r['candidate']];assert len(candidates)==22
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
 installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  native={(k+'/'+m['modelId']):(sha,m) for k,sha,m in c.execute("SELECT cache_key,result_sha,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(sorted({r['sourceKey'].split('/')[0] for r in candidates}),[r['modelId'] for r in candidates])).fetchall()}
  reviews=dict(c.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(pointer['snapshotId'],)).fetchall())
 forms={b['uid']:b for r in candidates for b in r['groupForms']};ids=sorted({b['buildingCSUID'] for b in forms.values()})
 raw,receipt=request(BASE+'/0/query',{'f':'json','where':'BuildingCSUID IN ('+','.join("'"+v+"'" for v in ids)+')','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'false'},method='POST')
 official=json.loads(raw);assert not official.get('error') and not official.get('exceededTransferLimit')
 save(doc/'official.json.gz',official);save(doc/'request.json',receipt)
 byid={}
 for f in official['features']:byid.setdefault(f['attributes']['BuildingCSUID'],[]).append(f)
 official_rows=[]
 for uid,b in sorted(forms.items()):
  matches=byid.get(b['buildingCSUID'],[]);r={'uid':uid,'csuid':b['buildingCSUID'],'uniqueOfficialRecord':len(matches)==1,'alreadyInRuntimeCatalogue':uid in installed,'currentReviewState':reviews.get(uid)}
  if len(matches)==1:
   f=matches[0];g,repaired=official_geometry(f);p=Polygon(b['rings'][0],b['rings'][1:]);ps=[q for q in polys(g) if q.intersection(p).area>0]
   r.update(officialAttributes=f['attributes'],uniquePolygon=len(ps)==1,geometryRepaired=repaired)
   if len(ps)==1:r.update(hausdorffDistanceM=p.hausdorff_distance(ps[0]),officialRings=[list(map(list,v.coords)) for v in [ps[0].exterior,*ps[0].interiors]])
  official_rows.append(r)
 save(doc/'official-context.json',{'rows':official_rows,'publication':False,'identityAccepted':False})
 final=module('complete_groups_current_forms','xl-final-script-pass.py');decoder=module('complete_groups_decoder','xl-second-pass.py');decoder.LOCAL=local
 prior={r['sourceKey']:r for r in read(ROOT/'docs/astra-city/government-import/government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz')['rows']}
 hashes={ref(manifest)['path']:ref(manifest)['sha256']};models=[];rows=[];contexts=[]
 for candidate in candidates:
  sha,m=native[candidate['sourceKey']];assert sha==candidate['nativeResultSHA256'] and m['asset']['sha256']==candidate['sourceSHA256']
  assert ref(ROOT/candidate['original']['path'])==candidate['original']
  uid=candidate['uid'];lo,hi=m['worldBounds'];current=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);targets=[(b,url) for b,_,url in current if b['uid']==uid];assert len(targets)==1
  b,url=targets[0];assert b in candidate['groupForms']
  for _,_,tile in current:hashes['3d-viewer/'+tile]=digest((ROOT/'3d-viewer'/tile).read_bytes())
  entry={**m.get('candidate',{}),'uid':uid,'modelId':m['modelId'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'label':b.get('name') or uid,**m['asset'],'rootTranslation':[-834500,0,816500],'worldBounds':m['worldBounds'],'triangles':m['triangles'],'sourceTile':prior[candidate['sourceKey']]['sheet'],'placementReviewed':False,'publicationApproved':False,'priority':'unreviewed'}
  row={'uid':uid,'modelId':m['modelId'],'triangles':m['triangles'],'sourceSHA256':m['asset']['sha256'],'source':{'building':b,'tile':url,'tileSHA256':hashes['3d-viewer/'+url]},'candidate':{'entry':entry,'path':candidate['original']['path']},'native':{'cacheKey':candidate['sourceKey'].split('/')[0],'resultSha':sha,'model':m,'sheet':prior[candidate['sourceKey']]['sheet']},'currentReview':None,'historicallyPublished':uid in installed}
  asset=local/'assets'/(m['asset']['sha256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes((ROOT/candidate['original']['path']).read_bytes())
  tri=decoder.glb_triangles(row);identity=final.identity_context(row,tri,current)
  heights=[{'uid':v['uid'],'name':v.get('name'),'baseHeightHKPD':v.get('baseHeightHKPD'),'topHeightHKPD':v.get('topHeightHKPD'),'metadataTopAboveSourceBounds':isinstance(v.get('topHeightHKPD'),(int,float)) and v['topHeightHKPD']>hi[1]+.5,'alreadyInRuntimeCatalogue':v['uid'] in installed,'currentReviewState':reviews.get(v['uid'])} for v in candidate['groupForms']]
  contexts.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'identity':identity,'groupForms':candidate['groupForms'],'groupMeasures':candidate['measures'],'componentHeights':heights,'neighbourTileHashes':{tile:digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in current},'identityAccepted':False,'installationApproved':False,'suppressionApproved':False})
  models.append({'uid':uid,'name':b.get('name'),'modelId':m['modelId'],'sourceSHA256':row['sourceSHA256'],'assetPath':candidate['original']['path'],'worldBounds':m['worldBounds'],'triangles':m['triangles'],'forms':[v for v,_,_ in current]});rows.append(row)
 save(doc/'physical-selection.json.gz',{'rows':rows,'manifestSHA256':digest(manifest.read_bytes()),'batch':a.batch,'nativeRun':NATIVE_RUN});save(doc/'context.json.gz',{'rows':contexts,'qualification':'Group/height evidence only. Retain high components and all current detail until complete ownership, support and suppression are proven. Metadata heights are flags, not geometry truth or rejection.'})
 for path in [Path(__file__),HERE/'render-source-footprint-evidence.mjs',scan/'result.json',scan/'outcomes.json.gz',doc/'official-context.json',doc/'official.json.gz',doc/'request.json']:
  hashes[ref(path)['path']]=ref(path)['sha256']
 save(doc/'inputs.json',{'models':models,'inputHashes':hashes,'publication':False,'installationApproved':False,'architectureReview':False})
 stage='complete-original-group-official-capture-context-v1';payload={'scanJobId':previous['jobId'],'uids':[r['uid'] for r in rows],'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in rows},'inputs':ref(doc/'inputs.json')};jid=jobs.enqueue(a.batch,stage,payload);job=jobs.claim(a.batch,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
 try:
  subprocess.run(['node',str(HERE/'render-source-footprint-evidence.mjs'),'--inputs',str((doc/'inputs.json').relative_to(ROOT)),'--out',str(doc.relative_to(ROOT))],cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
  render=read(doc/'render.json');assert not render['errors'] and len(render['views'])==22
  refs=[ref(p) for p in sorted(doc.iterdir()) if p.is_file()]+[ref(Path(__file__))]+[r['original'] for r in candidates]
  result={**payload,'evidenceRefs':refs,'jobId':jid,'batch':a.batch,'sourcesCaptured':22,'componentForms':len(forms),'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'identityAccepted':False,'installationApproved':False,'sourceReviewUsesAI':False,'qualification':'Fresh official CSUID component polygons, current full original bounds/projections, current metadata heights and original native-pose captures. These are evidence, not permission to suppress tall towers or accept a whole complex based on shared OSM parent/2D coverage. Source-specific identity/component/support/physical/runtime/browser checks remain mandatory.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   for path,sha in render['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'sourcesCaptured':22,'componentForms':len(forms),'neonVerified':True}),flush=True)
 except Exception as e:jobs.finish(job,error=str(e));raise

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scan',required=True);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
 if a.owned:return owned(a,doc,local)
 assert not doc.exists() and not local.exists()
 rows=[r for r in read(ROOT/a.scan/'outcomes.json.gz')['rows'] if r['candidate']]
 claim=reservations.claim('codex-xl-complete-group-context-'+str(uuid.uuid4()),['native-model:'+r['sourceKey'] for r in rows],batch=a.batch,ttl=3600);assert claim['ok'],claim
 save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
