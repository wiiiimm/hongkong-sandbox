"""Private four-original runtime qualification on trimmed terrain; no publication."""
from pathlib import Path
import copy,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-four-original-browser-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PAIR=BASE/'government-xl-victoria-three-original-checked-20261009';CURRENT=BASE/'government-xl-victoria-mall-neighbours-v5-20261020';TERRAIN=BASE/'government-xl-victoria-mall-trimmed-overlap-validation-v1-20261020'
POD='landsd/227593:0';TOWER3='landsd/251609:0';UIDS=[POD,'landsd/251614:0','landsd/251615:0',TOWER3]
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PAIR,CURRENT,TERRAIN]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    if folder==PAIR and e['path']!=str((PAIR/'support-inputs.json').relative_to(ROOT)):continue
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 sources=read(PAIR/'support-inputs.json')['sources'];assert {r['uid']for r in sources}==set(UIDS)
 tile=ROOT/'3d-viewer/city/data/tiles/0_-1.json';forms={b['uid']:b for b in read(tile)['buildings']};models=[];sha={r['uid']:r['sourceSHA256']for r in sources};refs.append(tile)
 for uid in UIDS:
  r=next(r for r in sources if r['uid']==uid);e=copy.deepcopy(r['candidate']['entry']);assert e['buildingCSUID']==forms[uid]['buildingCSUID'];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==sha[uid]==e['sha256'];refs.append(ROOT/r['candidate']['path'])
  e.update(priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,supportDependencies=[]if uid==POD else[dict(uid=POD,csuid=forms[POD]['buildingCSUID'],sha256=sha[POD],state='candidate')]);e['asset']='assets/'+sha[uid]+'.glb.gz';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);models.append(e)
 cat=dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=models,counts=dict(packedModels=4))
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',[forms[u]for u in UIDS]);save(LOCAL/'validation-forms.json',{u:dict(building=forms[u],tile='city/data/tiles/0_-1.json',tileSHA256=digest(tile.read_bytes()))for u in UIDS})
 current=ROOT/'3d-viewer/city/data/official-models/support-review-20260909/catalogue.json';c=read(current);retained=[m for m in c['models']if m['uid']!=TOWER3];assert len(retained)==len(c['models'])-1;old=next(m for m in c['models']if m['uid']==TOWER3);assert old['sha256']==sha[TOWER3]
 save(LOCAL/'retained-catalogue.json',{**c,'models':retained,'counts':{**c['counts'],'packedModels':len(retained)}});refs.append(current)
 terrainpath=TERRAIN/'candidate-terrain.json';terrain=[dict(source=str(terrainpath.relative_to(ROOT)),destination='city/data/victoria-trimmed-private-v1.json',resolution=5,area='Private Victoria original source terrain')]
 save(DOC/'terrain-candidates.json',[dict(path=str(terrainpath.relative_to(ROOT)),sha256=digest(terrainpath.read_bytes()),uids=[POD])])
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'validation-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'loader.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 v=read(DOC/'validation.json');save(DOC/'loader-command.json',dict(command=cmd,exitCode=p.returncode));assert v['loaderAccepted']==4 and not v['exceptions'];refs.append(tool)
 config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,catalogueReplacements=[dict(url=str(current.relative_to(ROOT/'3d-viewer')),source=str((LOCAL/'retained-catalogue.json').relative_to(ROOT)))],browserUids=UIDS,failureTestUids=[],jointUidsByModel={u:([POD]if u==POD else[POD,u])for u in UIDS},fitBox=True,captureDirectionByModel={u:[-1,.65,.1]for u in UIDS})
 browser=HERE/'victoria_four_original_acceptance_browser_v2_20261020.mjs';refs.append(browser)
 for width in [390,1280]:
  cfg={**config,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};p=LOCAL/f'browser-config-{width}.json';save(p,cfg);cmd=['node',str(browser),'staged',str(p.relative_to(ROOT))]
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
  save(DOC/f'command-{width}.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode==0
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and len([v for v in report['views']if 'time'in v])==8
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 module('victoria_four_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-four-originals-trimmed-terrain-runtime',list(dict.fromkeys(refs)),dict(uids=UIDS,newSources=[u for u in UIDS if u!=TOWER3],retainedSource=TOWER3,installationApproved=False,visualAcceptance=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
