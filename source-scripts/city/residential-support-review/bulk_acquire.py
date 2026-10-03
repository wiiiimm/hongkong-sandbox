"""Mechanical missing-support batch: exact identities, bounded parallel sheets, resumable local outputs."""
import pathlib,json,sys,importlib.util,shutil,concurrent.futures,sqlite3
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;OUT=HERE/'omitted-support';DOC=ROOT/'docs/astra-city/residential-support-review/omitted-support'
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
lease=json.loads(pathlib.Path('/tmp/astra-omitted-support-lease.json').read_text());assert reservations.owns(lease)
s=importlib.util.spec_from_file_location('a',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);a.HERE=OUT;a.DOCS=DOC;OUT.mkdir(exist_ok=True);DOC.mkdir(exist_ok=True)
for name in ['service.json','index.json']:
 if not(OUT/name).exists():shutil.copyfile(a.BASE/name,OUT/name)
targets=a.read(HERE/'discovered-targets.json');targets['targets']=[t for t in targets['targets']if t['uid'] not in {'landsd/54170:0','landsd/235988:0'}];assert {'building:'+t['uid']for t in targets['targets']}==set(lease['resources']);a.write(OUT/'target-input.json',targets);a.write(OUT/'batch.json',{'batchId':'omitted-support-v1','capBytes':150_000_000})
network=a.Network(OUT/'transfer-ledger.json',cap=150_000_000);plan=a.read(OUT/'plan.json')if(OUT/'plan.json').exists()else a.prepare(network);byuid={t['uid']:t for t in plan['targets']};caches=a.retained_caches();print('Plan',plan['targetParts'],'parts',len(plan['tiles']),'sheets',flush=True)
def work(item):
 sheet,tile=item;statepath=OUT/'sources'/sheet/'state.json'
 try:
  previous=a.read(statepath)if statepath.exists()else{}
  if previous.get('status')in ['staged','complete-directory-no-exact-model']:return sheet,previous['status'],None
  state=a.acquire_tile(network,sheet,tile,byuid,caches);return sheet,state['status'],None
 except Exception as e:
  state=a.read(statepath)if statepath.exists()else{'sheet':sheet};state.update(status='deferred-error',error=str(e));a.write(statepath,state);return sheet,'deferred-error',str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for sheet,status,error in pool.map(work,sorted(plan['tiles'].items())):
  print(sheet,status,error or '',flush=True);a.report(plan,network)
r=a.report(plan,network);print(json.dumps({'acquisition':r['summary'],'nativeParts':r['nativeModelParts'],'newBytes':r['transfer']['receivedBytes']}),flush=True)
assert reservations.owns(lease)
sys.path.insert(0,str(ROOT/'source-scripts/city/building-batch'));import cached_models
processor=cached_models.Processor(ROOT,OUT/'candidates',max_output_bytes=100_000_000);c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON');results=[]
for target in plan['targets']:
 b=dict(c.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(target['uid'],)).fetchone());options=[]
 for path in(OUT/'staged').glob('*/manifest.json'):
  m=a.read(path)
  for spec in m['models']:
   if spec['officialBuildingCSUIDs']==[b['csuid']]:options.append({'manifest':str(path.relative_to(ROOT)),'spec':spec,'tile':m['tile'],'revision':m['tileRevision'],'sourceArchiveSHA256':m['sourceArchiveSha256']})
 if not options:results.append({'uid':b['uid'],'outcome':'no-exact-unique-staged-source-match','acquisition':next(x['outcome']for x in r['rows']if x['uid']==b['uid'])});continue
 if len({x['spec']['id']for x in options})!=1:results.append({'uid':b['uid'],'outcome':'multiple-native-identities-held'});continue
 options.sort(key=lambda x:(x['revision'],x['tile']),reverse=True)
 try:results.append(processor({'building':b,'disposition':'match-and-pack','candidate':options[0],'priorCompact':[]}))
 except Exception as error:results.append({'uid':b['uid'],'outcome':'packing-exception-held','error':str(error)})
c.close();catalogue=a.read(HERE/'candidates/catalogue.json');catalogue.update(area='Omitted government support candidates v1',models=[x['record']for x in results if x.get('record')]);catalogue['counts']['packedModels']=len(catalogue['models']);a.write(OUT/'candidates/catalogue.json',catalogue);a.write(DOC/'packing.json',{'issue':'HKS-214','version':1,'results':results,'published':False});print(json.dumps({'packed':len(catalogue['models']),'held':len(results)-len(catalogue['models'])}),flush=True)
