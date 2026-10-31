"""Record the metadata-only Lei Yue Mun terrain provenance correction in Neon."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;DOC=s.DOC/'lei-install';LOCAL=s.LOCAL/'lei-install';UID='landsd/109467:0';BATCH='government-xxl-lei-provenance-20260912';read,save,h,rel=s.read,s.save,s.h,s.rel
sys.path.insert(0,str(HERE.parent/'model-review-ledger'));import ledger

def call(args):subprocess.run(args,cwd=ROOT,check=True)
def start():
 claim=s.reservations.claim('codex-lei-provenance-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH);assert claim['ok'];save(LOCAL/'provenance-reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'provenance-reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 receipt=LOCAL/'provenance-reservation.json';assert s.reservations.owns(read(receipt));terrain=ROOT/'3d-viewer/city/data/government-grid-109467-0.json';model=read(ROOT/'3d-viewer/city/data/official-models/government-xxl-lei-20260912/catalogue.json')['models'][0]
 validation=read(DOC/'validation.json');assert validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0;live=read(DOC/'live-browser.json');assert live['passed']
 correction={'policy':'metadata-provenance-correction-v1','uid':UID,'modelSHA256':model['sha256'],'oldTerrainSHA256':'9ebede5be91804a51cbf50dfe5285a3e718f5adacb79fe97656f67d41bbdccaf','correctedTerrainSHA256':h(terrain),'correction':'The five-metre support grid samples the existing rendered 70-metre Lands Department parent terrain. The recovered native TIN bounded and verified the site but was omitted because its overlapping facets regressed adjacent fallback forms. Model and terrain numeric arrays are unchanged.','validationSHA256':h(DOC/'validation.json'),'neighbourChecksSHA256':h(DOC/'neighbour-checks.json'),'stagedBrowserSHA256':h(DOC/'staged-browser.json'),'liveBrowserSHA256':h(DOC/'live-browser.json'),'aiCalls':0,'geometryChanges':0};save(DOC/'provenance-correction.json',correction)
 snapshot=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'];effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-203','run_id':snapshot,'output_ref':rel(DOC/'provenance-correction.json')};commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();observation='Metadata-only correction: Lei Yue Mun support grid samples the existing rendered Lands Department parent terrain; recovered native TIN was used for bounds/verification. Numeric terrain arrays and exact government model geometry unchanged; all gates rerun and pass.'
 ledger.record_many(snapshot,receipt,[(UID,'installed-verified',DOC/'provenance-correction.json',observation,commit)],effort=effort,request_id=BATCH+'-'+correction['correctedTerrainSHA256'][:16]);print(json.dumps({'recorded':UID,'snapshot':snapshot,'terrainSHA256':correction['correctedTerrainSHA256'],'aiCalls':0}))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
