"""Hash-bound, per-model viewing priority edits without geometry or budget changes."""
import hashlib,json

def stage_priorities(root,plan,manifest,edits,report):
 def read(ref):
  p=(root/ref['path']).resolve();assert p.is_relative_to(root.resolve()),'Priority review outside repository'
  raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'],'Priority review changed'
  return json.loads(raw)
 for entry in plan.get('priorityReviews',[]):
  review=read(entry);approval=read(entry['visualApproval']);assert approval['status']=='approved-for-integration','Priority visual approval missing';read(review['evidence'])
  for cat in review['catalogues']:
   p=root/cat['source'];assert cat['url'] in manifest['officialModelCatalogues'],'Unknown priority catalogue'
   assert hashlib.sha256(p.read_bytes()).hexdigest()==cat['oldSHA256'],'Priority catalogue changed'
   data=json.loads(edits.get(p,p.read_bytes()));models={m['uid']:m for m in data['models']}
   changes=[c for c in review['changes'] if c['catalogue']==cat['source']];assert set(cat['models'])=={c['uid'] for c in changes}
   for c in changes:
    m=models[c['uid']];assert m['sha256']==c['modelSHA256'] and m['modelId']==c['modelId'] and m['buildingCSUID']==c['buildingCSUID'],'Priority model identity changed'
    assert m.get('priority')==c['oldPriority'],'Priority metadata changed'
    assert c['priority'] in ('detail','landmark'),'Unsupported viewing priority'
    m['priority']=c['priority'];report.setdefault('priorityUpdates',[]).append({'uid':m['uid'],'before':c['oldPriority'],'after':c['priority'],'assetUnchanged':m['sha256']})
   edits[p]=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
