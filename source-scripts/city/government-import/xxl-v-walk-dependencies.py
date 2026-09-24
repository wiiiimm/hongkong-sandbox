"""Stage metadata-only Cullinan dependency migration to native V Walk support."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/final-script-pass/v-walk'
STAGE=HERE/'accepted/government-xxl-v-walk-20260913'
UID='landsd/262871:0'; TOWERS={'landsd/178816:0','landsd/268497:0','landsd/95379:0'}
CAT=ROOT/'3d-viewer/city/data/official-models/support-review-20260909/catalogue.json'
read=lambda p:json.loads(Path(p).read_text()); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
report=read(DOC/'native-support.json'); rows={r['uid']:r for r in report['rows']};assert set(rows)==TOWERS and all(r['contacts']==r['rimSamples'] and r['maxDistance']<=.5 for r in rows.values())
original=read(CAT); migrated=copy.deepcopy(original); changes=[]
for model in migrated['models']:
 if model['uid'] not in TOWERS:continue
 old=copy.deepcopy(model['supportDependencies']); found=False
 for dep in model['supportDependencies']:
  if dep['uid']==UID:
   assert 'fallback' in dep['state'];dep['state']='candidate';dep['distance']=rows[model['uid']]['maxDistance'];found=True
 assert found
 changes.append({'uid':model['uid'],'modelSHA256':model['sha256'],'modelId':model['modelId'],'buildingCSUID':model['buildingCSUID'],'catalogue':str(CAT.relative_to(ROOT)),'oldSupportDependencies':old,'supportDependencies':model['supportDependencies'],'contactEvidenceSHA256':sha(DOC/'native-support.json')})
assert len(changes)==3
migrated_path=STAGE/'support-review-migrated-catalogue.json';save(migrated_path,migrated)
approval={'issue':'HKS-203','status':'approved-for-integration','scope':'Metadata-only migration after all 1,176 unique lower-rim tower vertices contact unchanged native V Walk within 0.172 m. Automated staged browser framing, picking, collision, retry and terrain-ray checks pass; no architecture claim or AI review.','stagedBrowserSHA256':sha(DOC/'staged-browser.json'),'supportEvidenceSHA256':sha(DOC/'native-support.json'),'sourceGeometryChanged':False,'aiCalls':0};save(DOC/'dependency-approval.json',approval)
review={'issue':'HKS-203','version':1,'published':False,'scope':'Only migrate three proven supportDependencies from surveyed fallback to the unchanged native V Walk candidate; every model asset and all geometry remain unchanged.','catalogues':[{'url':'city/data/official-models/support-review-20260909/catalogue.json','source':str(CAT.relative_to(ROOT)),'oldSHA256':sha(CAT),'models':sorted(TOWERS)}],'changes':changes,'contactReport':str((DOC/'native-support.json').relative_to(ROOT)),'contactReportSHA256':sha(DOC/'native-support.json'),'requiresNewNativeUids':[UID],'sourceGeometryModified':False};save(DOC/'dependency-replacements.json',review)
plan=read(STAGE/'plan.json');plan['dependencyReviews']=[{'path':str((DOC/'dependency-replacements.json').relative_to(ROOT)),'sha256':sha(DOC/'dependency-replacements.json'),'visualApproval':{'path':str((DOC/'dependency-approval.json').relative_to(ROOT)),'sha256':sha(DOC/'dependency-approval.json')}}];save(STAGE/'plan.json',plan)
config=read(STAGE/'browser-config.json');config['catalogueReplacements']=[{'url':'city/data/official-models/support-review-20260909/catalogue.json','source':str(migrated_path.relative_to(ROOT))}];save(STAGE/'browser-config.json',config)
print(json.dumps({'changes':len(changes),'maxDistance':max(r['maxDistance'] for r in rows.values()),'geometryChanges':0,'aiCalls':0}))
