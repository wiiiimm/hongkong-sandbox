"""Propose metadata-only migration from surveyed fallback to proven native support."""
import argparse,json,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=ROOT/'docs/astra-city/assembly-support-review';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('family',choices=['airside','branksome']);a=p.parse_args();support='landsd/335194:0' if a.family=='airside' else 'landsd/232907:0';uids=['landsd/335196:0'] if a.family=='airside' else ['landsd/222976:0','landsd/265180:0'];report=OUT/(a.family+'-native-support.json');r=read(report);rows={p['uid']:p for p in r['rows']};changes=[];cats=[]
for entry in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
 path=ROOT/'3d-viewer'/entry;c=read(path);matches=[m for m in c['models'] if m['uid'] in uids]
 if not matches:continue
 cats.append({'url':entry,'source':str(path.relative_to(ROOT)),'oldSHA256':sha(path),'models':[m['uid'] for m in matches]})
 for m in matches:
  row=rows[m['uid']];assert row['sha256']==m['sha256'];distances=[]
  for rim in row['rim']:
   native=[d['distance'] for d in rim['contacts'] if d['uid']==support and 'fallback' not in d['state']];assert native;distances.append(min(native))
  assert max(distances)<=.5;deps=copy.deepcopy(m['supportDependencies']);found=False
  for d in deps:
   if d['uid']==support:assert 'fallback' in d['state'];d['state']='installed';d['distance']=max(distances);found=True
  assert found;changes.append({'uid':m['uid'],'modelSHA256':m['sha256'],'modelId':m['modelId'],'buildingCSUID':m['buildingCSUID'],'catalogue':str(path.relative_to(ROOT)),'oldSupportDependencies':m['supportDependencies'],'supportDependencies':deps,'contactEvidenceSHA256':sha(report)})
assert len(changes)==len(uids)
v={'issue':'HKS-214','version':1,'published':False,'scope':'Only migrate proven native supportDependencies; every other model field and source asset remains unchanged.','catalogues':cats,'changes':changes,'contactReport':str(report.relative_to(ROOT)),'contactReportSHA256':sha(report),'requiresNewNativeUids':[support],'requiresVisualApproval':True,'visualApproval':{'status':'approved-for-integration','evidence':'docs/astra-city/assembly-support-review/visual-acceptance-'+('foundation' if a.family=='airside' else 'exact-next')+'.json','scope':'Native supporting source model inspected in normal and isolated exported views; installed dependant geometry unchanged and every actual lowest-rim vertex contacts native support within0.5m.'}}
for base in [HERE,OUT]:(base/('dependency-replacements-'+a.family+'.json')).write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps({'family':a.family,'changes':len(changes),'maxDistances':[max(d['distance'] for d in c['supportDependencies'] if d['uid']==support) for c in changes]}))
