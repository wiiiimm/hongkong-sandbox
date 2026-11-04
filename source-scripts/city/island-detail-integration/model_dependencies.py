"""Hash-guarded support metadata migrations; never changes model geometry."""
import json,hashlib
from pathlib import Path

def dependency_rows(model):
 result=[]
 for d in model.get('supportDependencies',[]):
  if isinstance(d,str):result.append((d,'fallback'))
  else:
   assert d['state'] in ('fallback','surveyed-footprint-fallback','candidate','installed'),'Unknown dependency state'
   result.append((d['uid'],'native' if d['state'] in ('candidate','installed') else 'fallback'))
 return result

def stage_dependencies(root,plan,manifest,edits,new_models,report):
 def read(ref):
  p=(root/ref['path']).resolve();assert p.is_relative_to(root.resolve())
  raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256'],'Dependency review changed'
  return json.loads(raw)
 for entry in plan.get('dependencyReviews',[]):
  review=read(entry);approval=read(entry['visualApproval']);assert approval['status']=='approved-for-integration','Dependency assembly visual review missing'
  read({'path':review['contactReport'],'sha256':review['contactReportSHA256']})
  for cat in review['catalogues']:
   p=root/cat['source'];assert cat['url'] in manifest['officialModelCatalogues'];assert hashlib.sha256(p.read_bytes()).hexdigest()==cat['oldSHA256'],'Dependency catalogue changed'
   data=json.loads(edits.get(p,p.read_bytes()));byuid={m['uid']:m for m in data['models']}
   changes=[x for x in review['changes'] if x['catalogue']==cat['source']];assert set(cat['models'])=={x['uid'] for x in changes}
   for change in changes:
    m=byuid[change['uid']]
    assert m['sha256']==change['modelSHA256'] and m['modelId']==change['modelId'] and m['buildingCSUID']==change['buildingCSUID'],'Dependency model identity changed'
    assert m.get('supportDependencies',[])==change['oldSupportDependencies'],'Dependency metadata changed'
    m['supportDependencies']=change['supportDependencies'];dependency_rows(m)
    report.setdefault('dependencyUpdates',[]).append({'uid':m['uid'],'assetUnchanged':m['sha256'],'before':change['oldSupportDependencies'],'after':m['supportDependencies']})
   edits[p]=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
 current={}
 for url in manifest['officialModelCatalogues']:
  p=root/'3d-viewer'/url;data=json.loads(edits.get(p,p.read_bytes() if p.exists() else b'{}'))
  current.update({m['uid']:m for m in data.get('models',[])})
 changed=set(new_models)|{x['uid'] for x in report.get('dependencyUpdates',[])}
 for uid,m in current.items():
  for support,kind in dependency_rows(m):
   if kind=='fallback':assert support not in new_models,'New native support conflicts with an existing surveyed fallback requirement: '+uid+' -> '+support
   elif uid in changed:assert support in current,'Missing required native support: '+support
 def visit(uid,active,done):
  if uid in done:return
  assert uid not in active,'Cyclic native support dependency';active.add(uid)
  for support,kind in dependency_rows(current[uid]):
   if kind=='native':visit(support,active,done)
  active.remove(uid);done.add(uid)
 for uid in changed:visit(uid,set(),set())
 for entry in plan.get('dependencyReviews',[]):
  review=read(entry);assert set(review['requiresNewNativeUids'])<=set(current),'Incomplete native assembly publication'
