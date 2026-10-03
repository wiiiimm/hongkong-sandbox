"""HKS-208: selected registry IDs through the existing cached-model processor."""
import collections,hashlib,json,pathlib,sqlite3,sys,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'building-batch'))
from cached_models import Processor
EXCLUDED={'landsd/329094:0':'Namesake Peak Tower in the New Territories, outside Victoria Peak landmark.'}
GROUPS=['hkcec','tai-kwun','cheung-kong-centre','lippo-centre','asia-society','henderson','flagstaff-house','court-final-appeal','central-government-offices','legislative-council','chief-executive-office','hysan-place','opus','peak-tower']
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 started=time.monotonic();registry=read(ROOT/'docs/astra-city/landmark-registry/inventory-candidates.json');groups=[dict(id=r['id'],name=r['name'],uids=[c['uid'] for c in r['candidates']]) for r in registry['rows'] if r['id'] in GROUPS]
 extra=HERE/'taikwun-audit.json'
 if extra.exists():
  audit=read(extra)
  for g in groups:
   if g['id'] in audit.get('groups',{}):g['uids']=audit['groups'][g['id']]['uids']
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 for g in groups:g['uids']=[u for u in g['uids'] if u not in EXCLUDED]
 targets={uid:dict(c.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(uid,)).fetchone()) for g in groups for uid in g['uids']};existing={r[0] for r in c.execute('SELECT uid FROM models')};byuid=collections.defaultdict(list);bygeo=collections.defaultdict(list)
 for path in sorted(ROOT.glob('source-scripts/city/*/staged/*/manifest.json')):
  m=read(path)
  for spec in m.get('models',[]):
   candidate=dict(manifest=str(path.relative_to(ROOT)),spec=spec,tile=m['tile'],revision=m['tileRevision'],sourceArchiveSHA256=m.get('sourceArchiveSha256',m.get('sourceCacheSha256')))
   if spec.get('geoRefNo'):bygeo[spec['geoRefNo']].append(candidate)
   for uid,b in targets.items():
    if b['csuid'] in spec.get('officialBuildingCSUIDs',[]):byuid[uid].append(candidate)
 processor=Processor(ROOT,HERE/'compact',max_output_bytes=30*1024**2);results=[];models=[]
 for uid,b in targets.items():
  if b['embedded'] or uid in existing:results.append({'uid':uid,'outcome':'already-detailed'});continue
  options=byuid[uid];options.sort(key=lambda r:(r['revision'],r['manifest']),reverse=True)
  if not options:
   results.append({'uid':uid,'outcome':'no-standard-match-in-cache','possibleExactGeoRefModels':[{'modelId':r['spec']['id'],'manifest':r['manifest'],'officialMatches':r['spec'].get('officialMatches')} for r in bygeo[b['csuid'][:10]]]});continue
  ids={r['spec']['id'] for r in options}
  if len(ids)!=1 or any(len(r['spec']['officialBuildingCSUIDs'])!=1 for r in options):results.append({'uid':uid,'outcome':'ambiguous-source-match'});continue
  candidate=options[0];same=[r for r in options if r['revision']==candidate['revision']]
  assert len({json.dumps(r['spec']['sourceHashes'],sort_keys=True) for r in same})==1,uid
  result=processor(dict(building=b,candidate=candidate,priorCompact=[],disposition='match-and-pack'));results.append(result)
  if result.get('record'):models.append(result['record'])
 assert len({m['uid'] for m in models})==len(models)
 counts={'selectedSourceParts':len(targets),'packedModels':len(models),'compressedBytes':sum(m['bytes'] for m in models),'triangles':sum(m['triangles'] for m in models),'outcomes':dict(collections.Counter(r['outcome'] for r in results))}
 cat={'schemaVersion':1,'kind':'staged-official-model-catalogue','datasetId':'landsd_rcd_1742809441342_98380','area':'Expanded architecture landmarks batch1','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'counts':counts,'models':models}
 write(HERE/'compact/catalogue.json',cat);write(HERE/'compact/catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']});write(HERE/'selection.json',{'issue':'HKS-208','groups':groups,'sourceRegistry':'source-scripts/city/landmark-registry/landmarks.json','excludedSourceUids':EXCLUDED,'qualification':'Initial named/source-ID scope; incomplete compound identities are explicit, not whole-region coverage.'});write(HERE/'report.json',{'issue':'HKS-208','counts':counts,'results':results,'seconds':round(time.monotonic()-started,3),'aiCalls':0,'networkRequests':0,'verticalScale':1});print(json.dumps(counts))
if __name__=='__main__':main()
