"""Disable procedural facade windows on source-specific non-standard landmarks; no geometry edits or AI."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/astra-city/government-import/nonstandard-window-skins-20260913'
TARGETS={
 'cultural-landmarks':None,
 'kai-tak-stadium':{'landsd/318723:0'},
 'model-pass-20260909-peak':{'landsd/248218:0'},
 'island-corridor':{'landsd/10114:0','landsd/124803:0'},
}
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,separators=(',',':'),sort_keys=True)+'\n')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 changed=[];catalogues=[];preexisting={'landsd/211702:0','landsd/252061:0'}
 for folder,uids in TARGETS.items():
  path=ROOT/'3d-viewer/city/data/official-models'/folder/'catalogue.json';relative=str(path.relative_to(ROOT));prior=json.loads(subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT));before=hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT)).hexdigest();data=json.loads(path.read_text());selected=data['models'] if uids is None else [m for m in data['models'] if m['uid'] in uids]
  assert selected and (uids is None or {m['uid'] for m in selected}==uids)
  for model in selected:
   prior_model=next(m for m in prior['models'] if m['uid']==model['uid']);model['proceduralWindows']=False
   if model['uid'] not in preexisting:changed.append({'uid':model['uid'],'label':model.get('label'),'catalogue':folder,'before':prior_model.get('proceduralWindows'),'after':False})
  save(path,data);catalogues.append({'path':str(path.relative_to(ROOT)),'beforeSHA256':before,'afterSHA256':digest(path),'modelsReviewed':len(selected)})
 assert len(changed)==12
 save(DOC/'review.json',{'policy':'nonstandard-source-surface-review-v1','decision':'Disable generic window shades on non-standard geometry where the government mesh defines the architectural surface arrangement.','reviewedModels':14,'changedModels':changed,'catalogues':catalogues,'deferred':['landsd/184076:0'],'deferredReason':'Court of Final Appeal has a conventional windowed facade and needs a direct visual comparison before changing its treatment.','sourceMaterialsRetained':True,'geometryChanges':0,'aiCalls':0})
 print(json.dumps({'reviewed':14,'changed':len(changed),'aiCalls':0,'geometryChanges':0}))
if __name__=='__main__':main()
