"""Stage two coherent native assemblies and guarded metadata-only dependency replacements."""
import json,pathlib,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 audit=read(DOC/'migration-support.json');assert all(r['allNativeContacts']for r in audit['rows']);current=read(ROOT/'3d-viewer/city/data/manifest.json');entries={};paths={}
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for m in read(path)['models']:entries[m['uid']]=m;paths[m['uid']]=path
 original=read(HERE/'review-candidates/catalogue.json');source={m['uid']:m for m in original['models']};oldrows=[r for r in audit['rows']if r['oldDependencies']];uids={r['uid']for r in audit['rows']}|{r['podiumUID']for r in audit['rows']};stage=HERE/'migration-candidates';stage.mkdir(exist_ok=True);changes=[];catalogues={}
 for r in oldrows:
  uid=r['uid'];m=entries[uid];assert m['sha256']==r['modelSHA256'] and m['supportDependencies']==r['oldDependencies'];path=paths[uid];pathrel=str(path.relative_to(ROOT));dependencies=[dict(d)for d in m['supportDependencies']]
  for d in dependencies:
   if d['uid']==r['podiumUID']:
    assert d['state']=='surveyed-footprint-fallback';d['state']='installed';d['distance']=r['maxDistance']
  changes.append({'uid':uid,'modelSHA256':m['sha256'],'modelId':m['modelId'],'buildingCSUID':m['buildingCSUID'],'catalogue':pathrel,'oldSupportDependencies':r['oldDependencies'],'supportDependencies':dependencies,'contactEvidenceSHA256':sha(DOC/'migration-support.json')})
  if pathrel not in catalogues:catalogues[pathrel]={'url':pathrel.removeprefix('3d-viewer/'),'source':pathrel,'oldSHA256':sha(path),'models':[]}
  catalogues[pathrel]['models'].append(uid)
 deps={r['uid']:r['supportDependencies']for r in read(DOC/'decisions.json')['rows']};models=[]
 for uid in sorted(uids):
  installed=uid in entries;m=dict(entries[uid]if installed else source[uid]);sourcepath=paths[uid].parent/m['asset']if installed else HERE/'review-candidates'/m['asset'];assert sha(sourcepath)==m['sha256'];shutil.copyfile(sourcepath,stage/m['asset']);change=next((r for r in changes if r['uid']==uid),None);m['supportDependencies']=change['supportDependencies']if change else deps[uid];m['priority']='landmark';models.append(m)
 original['models']=models;original['counts']['packedModels']=len(models);save(stage/'catalogue.json',original)
 plan={'issue':'HKS-214','version':1,'published':False,'scope':'Only replace supportDependencies of six installed exact native models after all their lower-rim vertices contact the new native podium within0.5m. Every other field and every asset byte must remain unchanged.','catalogues':list(catalogues.values()),'changes':changes,'contactReport':'docs/astra-city/residential-support-review/migration-support.json','contactReportSHA256':sha(DOC/'migration-support.json'),'requiresNewNativeUids':sorted(uids-set(entries)),'requiresVisualApproval':True};save(HERE/'dependency-replacements.json',plan);save(DOC/'dependency-replacements.json',plan)
 for c in plan['catalogues']:
  data=read(ROOT/c['source'])
  for m in data['models']:
   change=next((r for r in changes if r['uid']==m['uid']),None)
   if change:m['supportDependencies']=change['supportDependencies']
  save(HERE/'migration-existing'/pathlib.Path(c['source']).parent.name/'catalogue.json',data)
 save(HERE/'migration-selection.json',{'snapshot':'native-support-migration-v1','parts':[{'uid':m['uid'],'name':m['label'],'proposedIdentity':False}for m in models]});print(json.dumps({'models':len(models),'newNative':len(plan['requiresNewNativeUids']),'metadataReplacements':len(changes)}))
if __name__=='__main__':main()
