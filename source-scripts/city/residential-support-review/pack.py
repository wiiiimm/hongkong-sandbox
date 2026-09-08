"""Reuse the exact-bit packer and conservative matching without a SQLite writer."""
import json,pathlib,sqlite3,sys,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
for p in ['/tmp/astra-residential-support-lease.json','/tmp/astra-residential-podium-lease.json']:assert reservations.owns(json.loads(pathlib.Path(p).read_text()))
sys.path.insert(0,str(ROOT/'source-scripts/city/building-batch'));import cached_models
read=lambda p:json.loads(p.read_bytes());out=HERE/'candidates';processor=cached_models.Processor(ROOT,out,max_output_bytes=10_000_000)
c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
plan=read(HERE/'plan.json');results=[]
for target in plan['targets']:
 b=dict(c.execute('SELECT * FROM buildings WHERE uid=? AND active=1',(target['uid'],)).fetchone());options=[]
 for path in (HERE/'staged').glob('*/manifest.json'):
  m=read(path)
  for s in m['models']:
   if s['officialBuildingCSUIDs']==[b['csuid']]:options.append({'manifest':str(path.relative_to(ROOT)),'spec':s,'tile':m['tile'],'revision':m['tileRevision'],'sourceArchiveSHA256':m['sourceArchiveSha256']})
 assert len(options)==1,(target['uid'],len(options))
 result=processor({'building':b,'disposition':'match-and-pack','candidate':options[0],'priorCompact':[]});assert result['outcome']=='staged-needs-placement-review',result;results.append(result)
c.close();catalogue=read(ROOT/'source-scripts/city/grounded-model-review/candidates/catalogue.json');catalogue.update(area='LOHAS missing podium source assembly review',models=[r['record']for r in results],counts={'packedModels':len(results)})
(out/'catalogue.json').write_text(json.dumps(catalogue,indent=2)+'\n');(DOC/'packing.json').write_text(json.dumps({'issue':'HKS-214','results':results,'published':False,'sourceBytesPreserved':True},indent=2)+'\n')
for m in catalogue['models']:print(m['uid'],m['modelId'],m['worldBounds'],m['bytes'])
