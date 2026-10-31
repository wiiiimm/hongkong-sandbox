"""Private original-library loader checks and source identity captures; no approval."""
from pathlib import Path
import json,sys,uuid,copy,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-library-loader-identity-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-central-library-private-ground-v1-20261019';NEAR=BASE/'government-xl-central-library-neighbours-v1-20261019';FOUND=BASE/'government-xl-central-library-four-mode-foundations-v2-20261019';UID='landsd/232240:0'
def owned():
 assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,NEAR,FOUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];assert row['uid']==UID
 e=copy.deepcopy(row['candidate']['entry']);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset=LOCAL/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');key=row['native']['cacheKey']
  assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()[0]==row['native']['resultSha']
  sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
 assert not e.get('sourceTile') or e['sourceTile']==sheet;e['sourceTile']=sheet
 save(DOC/'source-tile-binding.json',dict(uid=UID,cacheKey=key,resultSha=row['native']['resultSha'],sourceTile=sheet))
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[e],counts=dict(packedModels=1),area='Private Central Library original podium'))
 save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']});save(DOC/'terrain-candidates.json',read(CAP/'terrain-candidates.json'))
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with (DOC/'validation.log').open('w') as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'validation-command.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode in [0,1];v=read(DOC/'validation.json');refs.append(tool)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');matches=[]
 for url in manifest['officialModelCatalogues']:
  catpath=ROOT/'3d-viewer'/url
  for entry in read(catpath)['models']:
   if entry['uid']=='landsd/227428:0':matches.append((entry,catpath))
 assert len(matches)==1;other,catpath=matches[0];otherpath=catpath.parent/other['asset'];assert digest(otherpath.read_bytes())==other['sha256'];refs.extend([catpath,otherpath])
 source=dict(assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=e['worldBounds'],triangles=row['triangles'],sourceUid=UID)
 component=dict(uid=other['uid'],assetPath=str(otherpath.relative_to(ROOT)),sourceSHA256=other['sha256'],worldBounds=other['worldBounds'],triangles=other['triangles'])
 models=[]
 for name,frame,direction in [('whole',None,[.7,.8,1]),('whole-reverse',None,[-.7,.8,-1]),('frontage',[[3015,0,755],[3140,24,885]],[.7,.8,1])]:models.append(dict(**source,uid='review/'+name,originalComponents=[component],forms=[row['source']['building']],failedSamples=[],reviewFrame=frame,viewDirection=direction))
 viewtool=HERE/'central_library_identity_views_v1_20261019.mjs';save(DOC/'input.json',dict(models=models,inputHashes={source['assetPath']:source['sourceSHA256'],component['assetPath']:component['sourceSHA256']}));subprocess.run(['node',str(viewtool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==3 and not report['errors'];refs.append(viewtool)
 identity=read(BASE/'government-xl-next-twenty-original-identity-v1-20261018/232240:0/identity.json');policy=module('central_library_policy',HERE/'acceptance-policy.py');metrics=read(CAP/'metrics.json');rawreasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
 summary=dict(uid=UID,loaderAccepted=v['loaderAccepted'],checksPassed=v['checksPassed'],exceptions=v['exceptions'],ordinaryConcerns=[dict(uid=r['uid'],concerns=r.get('concerns',[]))for r in v['results']],rawPolicyReasons=rawreasons,views=3,identityApprovalPending=True,installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 for report in [v,report]:
  for p,h in {**report.get('inputHashes',{}),**report.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'acceptance-policy.py',BASE/'government-xl-next-twenty-original-identity-v1-20261018/232240:0/identity.json']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 module('central_library_loader_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'central-library-original-loader-and-identity-views',list(dict.fromkeys(refs)),dict(uids=[UID],summary=summary,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID,'building:landsd/227428:0','terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
