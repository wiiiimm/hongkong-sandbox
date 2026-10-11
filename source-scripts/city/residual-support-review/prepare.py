"""Reserve a bounded follow-up of native podiums and their existing source dependencies."""
import json,sys,pathlib,hashlib,uuid
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review'
read=lambda p:json.loads((ROOT/p).read_bytes())
report=read('docs/astra-city/residential-support-review/combined-support.json');parts={p['uid']:p for p in read('source-scripts/city/residential-support-review/review-input.json')['parts']};manifest=read('3d-viewer/city/data/manifest.json');installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read('3d-viewer/'+url)['models']}
exclude={'landsd/22089:0','landsd/255427:0'}
for file in ['visual-acceptance-foundation.json','visual-acceptance-exact-next.json','visual-acceptance-peak.json']:
 d=read('docs/astra-city/assembly-support-review/'+file)
 def walk(o):
  if isinstance(o,dict):
   if 'uid' in o:exclude.add(o['uid'])
   for v in o.values():walk(v)
  elif isinstance(o,list):
   for v in o:walk(v)
 walk(d)
podiums={'landsd/'+str(u)+':0' for u in [111608,229653,230686,233883,234162,245053,247062,255200,262368,265478,306084,6471,80800]}-installed-exclude
selected=set(podiums)
for row in report['rows']:
 if row['uid'] in installed|exclude or row['knownHold']:continue
 if any(c['uid'] in podiums for p in row['rim'] for c in p['contacts']):selected.add(row['uid'])
selection={'issue':'HKS-214','snapshotId':'11a25ce297101f9e','basePreflightSnapshot':read('source-scripts/city/residential-support-review/review-input.json')['snapshotId'],'podiumUids':sorted(podiums),'uids':sorted(selected),'parts':[parts[u] for u in sorted(selected)],'installedExcluded':sorted(installed&set(parts)),'concurrentExcluded':sorted(exclude),'basis':'Source contact review of previously held native podium foundations and their contacting components. No approval inferred.'}
(HERE/'input.json').write_text(json.dumps({'snapshotId':selection['basePreflightSnapshot'],'parts':selection['parts']},indent=2)+'\n');(HERE/'selection.json').write_text(json.dumps(selection['uids'],indent=2)+'\n');(DOC/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
receipt=pathlib.Path('/tmp/astra-residual-support-lease.json');assert not receipt.exists()
r=reservations.claim('residual-support-'+str(uuid.uuid4()),['building:'+u for u in sorted(selected)],batch='HKS-214-residual-support-review');assert r['ok'],r;receipt.write_text(json.dumps(r['reservation'],default=str,indent=2)+'\n');print(json.dumps({'reserved':len(selected),'podiums':len(podiums),'receipt':str(receipt)}))
