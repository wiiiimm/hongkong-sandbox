"""Private multi-original preview on unchanged BASIC supports; complete empty-native scope required."""
import argparse,copy,json,math,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','scope','inventory','empty-native','viewer-url']:p.add_argument('--'+k,required=True)
 p.add_argument('--uid',action='append',required=True);p.add_argument('--retain-basic',action='append',required=True);p.add_argument('--direction',action='append',required=True);p.add_argument('--dependency',action='append',default=[]);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch and len(set(a.uid))==len(a.uid)and len(set(a.retain_basic))==len(a.retain_basic)
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;leasepath=local/'reservation.json';refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,'selection.json.gz');selected={r['uid']:r for r in selection['rows']};assert set(a.uid)==set(selected)
 scope=take(a.scope,'summary.json');inventory=take(a.inventory,'complete-bounds.json.gz');take(a.empty_native,'summary.json')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==selection['manifestSHA256']==scope['currentManifestSHA256']==pins[a.inventory][str(manifest.relative_to(ROOT))]==pins[a.empty_native][str(manifest.relative_to(ROOT))];refs.append(manifest)
 assert set(scope['uids'])==set(a.uid)and all(r['currentNativeActorsChecked']==len(inventory['rows'])and not r['nearbyNativeActors']for r in scope['rows'])
 forms={};tiles={}
 for uid in a.uid:
  for item in take(a.scope,uid.split('/')[1]+'-forms.json.gz'):
   f=item['building'];assert f['uid']not in forms or forms[f['uid']]==f;forms[f['uid']]=f;tile=ROOT/'3d-viewer'/item['tile'];assert digest(tile.read_bytes())==item['tileSHA256'];assert next(v for v in read(tile)['buildings']if v['uid']==f['uid'])==f;refs.append(tile);tiles[str(tile.relative_to(ROOT))]=item['tileSHA256']
 assert set(a.retain_basic)<=set(forms)and not set(a.uid)&set(a.retain_basic)
 current=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[a.inventory][str(path.relative_to(ROOT))];refs.append(path);current.extend(read(path)['models'])
 assert len(current)==len({e['uid']for e in current})==len(inventory['rows'])
 forbidden=set(a.uid+a.retain_basic);assert not forbidden&{e['uid']for e in current}and not forbidden&{u for e in current for u in e.get('suppressesBuildingUids',[])}
 directions={}
 for value in a.direction:
  uid,*raw=value.split(',');assert uid in a.uid and uid not in directions;v=list(map(float,raw));assert len(v)==3 and all(math.isfinite(x)for x in v)and sum(x*x for x in v)>0;directions[uid]=v
 assert set(directions)==set(a.uid)
 if not a.owned:
  assert not out.exists()and not local.exists();claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),['building:'+u for u in sorted(forms)],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(leasepath),sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
  finally:
   if reservations.owns(lease):assert reservations.release(lease)['ok']
  return
 lease=read(leasepath);assert reservations.owns(lease)and not out.exists();out.mkdir();entries=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid in a.uid:
   row=selected[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);entry=copy.deepcopy(row['candidate']['entry']);assert entry['sha256']==row['sourceSHA256']and entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
   assert not any(entry.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids','partialSource','embeddedModel','embeddedModels'])
   native=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert native and native[1]==row['native']['resultSha']
   entry.update(sourceTile=native[0],asset='assets/'+row['sourceSHA256']+'.glb.gz',priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False);dest=local/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());entries.append(entry)
 dependencies=dict(v.split(',')for v in a.dependency);assert len(dependencies)==len(a.dependency)and set(dependencies)<=set(a.uid)and set(dependencies.values())<=set(a.uid)
 by_uid={e['uid']:e for e in entries}
 for uid,parent in dependencies.items():
  assert uid!=parent;target=by_uid[parent];by_uid[uid]['supportDependencies']=[dict(uid=parent,state='installed',buildingCSUID=target['buildingCSUID'],sha256=target['sha256'])]
 from dependency_preflight import from_catalogues
 save(local/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',diagnosticOnly=True,physicalAcceptance=False,publicationApproved=False,datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=len(entries))))
 report=from_catalogues(manifest,[local/'catalogue.json']);assert not any(r['blockers']for r in report['rows']);save(out/'dependency-preflight.json',report)
 save(local/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']));save(local/'source-forms.json',[selected[u]['source']['building']for u in a.uid]);save(local/'validation-forms.json',{u:selected[u]['source']for u in a.uid})
 config=dict(viewerURL=a.viewer_url,stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',terrain=[],browserUids=a.uid,fitBox=True,captureDirectionByModel=directions,retainedBuildingUids=a.retain_basic,additionalRetainedUids=[],retainedNativeOwnViews=True,jointUids=a.uid,nativeSupportUidsByModel={})
 tool=HERE/'ronsdale_three_live_browser_v14_20261025.mjs';refs.append(tool);preflight=local/'preflight-config.json';save(preflight,dict(**config,doc=str(out.relative_to(ROOT))+'/'));subprocess.run(['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],cwd=ROOT,check=True)
 commands=[]
 for width in [1280,390]:
  assert reservations.owns(lease);cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(**config,viewportWidths=[width],failureTestUids=a.uid if width==390 else[],doc=str((out/str(width)).relative_to(ROOT))+'/'))
  with(out/('browser-'+str(width)+'.log')).open('w')as log:r=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
  report=out/str(width)/'staged-browser.json';passed=r.returncode==0 and report.exists()and read(report)['passed'];commands.append(dict(width=width,exitCode=r.returncode,diagnosticPassed=passed));save(out/('command-'+str(width)+'.json'),commands[-1])
 assert digest(manifest.read_bytes())==sha
 for key,h in tiles.items():assert digest((ROOT/key).read_bytes())==h
 refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json');result=dict(replacementDependenciesByUid=dependencies,uids=a.uid,retainedBasicUids=a.retain_basic,leasedFormUids=sorted(forms),currentNativeActors=len(current),commands=commands,allBrowserDiagnosticsPassed=all(c['diagnosticPassed']for c in commands),diagnosticOnly=True,visualAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Unapproved original sources, complete current empty-native scope and exact retained BASIC scene. All4source approval flags false. Exact candidate neighbour replacement dependency is previewed, with no engineering-support claim. No geometry/terrain/source pose edits or installation credit. ROOT must actually inspect exported canvases before any visual approval.')
 module('scoped_originals_basic_preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-scoped-originals-and-retained-basic-private-preview',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
