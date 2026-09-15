"""Stage exact support metadata and existing Harbourside migration; no live catalogue writes."""
import pathlib,json,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
report=read(DOC/'support.json');rows={r['uid']:r for r in report['rows']};assert rows['landsd/204153:0']['contacts']==rows['landsd/204153:0']['rimSamples']==41
cat=read(HERE/'review-candidates/catalogue.json')
for m in cat['models']:
 uid=m['uid'];dep='landsd/273061:0'if uid in ['landsd/203728:0','landsd/203724:0']else 'landsd/151601:0'if uid=='landsd/37369:0'else 'landsd/161320:0'if uid=='landsd/323059:0'else None
 m['supportDependencies']=[{'uid':dep,'state':'candidate'if dep=='landsd/273061:0'else 'surveyed-footprint-fallback'}]if dep else []
save(HERE/'review-candidates/catalogue.json',cat)
url='city/data/official-models/support-review-20260909/catalogue.json';src=ROOT/'3d-viewer'/url;original=read(src);old=next(m for m in original['models']if m['uid']=='landsd/204153:0');new=[{'uid':'landsd/273061:0','state':'candidate'}];change={'uid':old['uid'],'modelSHA256':old['sha256'],'modelId':old['modelId'],'buildingCSUID':old['buildingCSUID'],'catalogue':'3d-viewer/'+url,'oldSupportDependencies':old['supportDependencies'],'supportDependencies':new,'contactEvidenceSHA256':sha(DOC/'support.json')}
review={'issue':'HKS-214','catalogues':[{'url':url,'source':'3d-viewer/'+url,'oldSHA256':sha(src),'models':[old['uid']]}],'changes':[change],'contactReport':str((DOC/'support.json').relative_to(ROOT)),'contactReportSHA256':sha(DOC/'support.json'),'requiresNewNativeUids':['landsd/273061:0'],'sourceGeometryModified':False};save(HERE/'dependency-replacements.json',review)
old['supportDependencies']=new;save(HERE/'harbourside-migrated-catalogue.json',original);print('Five candidate dependencies, one existing native dependency migration staged')
