"""Promote the installed Tian Tan source asset to landmark streaming range; no geometry changes."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;DOC=s.DOC/'third-pass/tian-tan/visibility';LOCAL=s.LOCAL/'tian-tan-visibility';UID='landsd/241332:0';BATCH='government-xxl-tian-tan-visibility-20260912';read,save,h,rel=s.read,s.save,s.h,s.rel
STAGED=HERE/'accepted/government-xxl-tian-tan-20260912/catalogue.json';LIVE=ROOT/'3d-viewer/city/data/official-models/government-xxl-tian-tan-20260912/catalogue.json'
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger

def call(args):subprocess.run(args,cwd=ROOT,check=True)
def start():
 claim=s.reservations.claim('codex-tian-tan-visibility-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 receipt=LOCAL/'reservation.json';assert s.reservations.owns(read(receipt));before={rel(p):h(p) for p in (STAGED,LIVE)};original={p:p.read_bytes() for p in (STAGED,LIVE)}
 for p in (STAGED,LIVE):
  cat=read(p);models=[m for m in cat['models'] if m['uid']==UID];assert len(models)==1;m=models[0];assert m['sha256']=='d369abcc4b6c02da3722ec2372e5cdf00eb075026709408b91d07c206a93238a' and m['label']=='Tian Tan Buddha Statue' and m['priority'] in ('detail','landmark');m['priority']='landmark';save(p,cat)
 config=read(HERE/'accepted/government-xxl-tian-tan-20260912/browser-config.json');config['doc']=rel(DOC)+'/';config['browserUids']=[UID];config['failureTestUids']=[UID];save(DOC/'browser-config.json',config)
 try:call(['node',str(HERE/'resolution-browser.mjs'),'live',rel(DOC/'browser-config.json')])
 except BaseException:
  for p,raw in original.items():p.write_bytes(raw)
  raise
 report=read(DOC/'live-browser.json');assert report['passed'] and not report['errors'] and report['aiCalls']==0;assert {v['uid'] for v in report['views'] if v.get('fallbackRetained')}=={UID};after={rel(p):h(p) for p in (STAGED,LIVE)};model=read(LIVE)['models'][0]
 correction={'policy':'landmark-streaming-visibility-correction-v1','uid':UID,'cause':'The complete 41.22 m-tall source mesh was classified as detail, limiting activation to 300 m on mobile and 500 m on desktop while its simple base remained visible.','beforePriority':'detail','priority':'landmark','mobileRangeMetres':1800,'desktopRangeMetres':2500,'sourceSHA256':model['sha256'],'worldHeightMetres':model['worldBounds'][1][1]-model['worldBounds'][0][1],'catalogueBeforeSHA256':before,'catalogueAfterSHA256':after,'liveBrowserSHA256':h(DOC/'live-browser.json'),'aiCalls':0,'geometryChanges':0};save(DOC/'correction.json',correction)
 snapshot=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'];effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'correction.json')};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();observation='Metadata-only Tian Tan visibility correction: exact government source geometry unchanged; priority promoted from detail to landmark after the full statue disappeared at ordinary sightseeing distance. Live desktop/mobile, picking, collision, terrain and fallback/retry checks pass.'
 ledger.record_many(snapshot,receipt,[(UID,'installed-verified',DOC/'correction.json',observation,commit)],effort=effort,request_id=BATCH+'-'+after[rel(LIVE)][:16]);print(json.dumps({'updated':UID,'priority':'landmark','sourceSHA256':model['sha256'],'aiCalls':0,'geometryChanges':0}))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
