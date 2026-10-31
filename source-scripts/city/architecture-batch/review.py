"""HKS-208: explicit reviewed subset and hash guard around the shared publisher."""
import argparse,hashlib,importlib.util,json,pathlib,shutil,sys
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];D=R/'docs/astra-city/architecture-batch'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def prepare():
 a=read(H/'acceptance.json');c=read(H/'compact/catalogue.json');v=read(H/'compact/validation.json');assert v['checksPassed']==len(c['models'])
 assert set(a['accepted'])|set(a['held'])=={m['uid'] for m in c['models']}
 assert not set(a['accepted'])&set(a['held'])
 # Every accepted component must have passed an actual staged browser load.
 verified=set()
 for name in a['browserReports']:
  b=read(R/name);assert b['result']=='passed' and not b['errors']
  for area in b['areas']:
   verified.update(m['uid'] for m in area['models'] if m.get('active') and m.get('pick')==m['uid'] and m.get('contact'))
 assert set(a['accepted'])<=verified
 out=H/'approved';out.mkdir(exist_ok=True);models=[]
 for m in c['models']:
  if m['uid'] not in a['accepted']:continue
  assert a['accepted'][m['uid']]
  p=H/'compact'/m['asset'];assert sha(p)==m['sha256'];q=out/m['asset'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
  m.update(priority='landmark',placementReviewed=True,placementScreening='architecture-batch1-source-context',contextReview=a['accepted'][m['uid']]);models.append(m)
 c['models']=models;c['kind']='official-model-catalogue';c['counts'].update(packedModels=len(models),compressedBytes=sum(m['bytes'] for m in models),triangles=sum(m['triangles'] for m in models));write(out/'catalogue.json',c);write(out/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
 area={'area':'Expanded architecture batch1','catalogue':str((out/'catalogue.json').relative_to(R)),'destination':'city/data/official-models/architecture-batch-1/catalogue.json'}
 area.update(a.get('terrainPublication',{}));write(H/'publication-plan.json',{'areas':[area]})
 paths=set(a['browserReports'])|{str((H/p).relative_to(R)) for p in ['acceptance.json','report.json','selection.json','missing-source-report.json','placement-context.json','compact/validation.json','approved/catalogue.json','publication-plan.json']}
 paths.update(p for p in v['hashes'] if p.startswith('3d-viewer/'))
 paths.update(a.get('guardFiles',[]));write(H/'guard.json',{p:sha(R/p) for p in sorted(paths)})
 print(json.dumps(c['counts']))
def publish(apply):
 for p,h in read(H/'guard.json').items():assert sha(R/p)==h,'Reviewed input changed: '+p
 spec=importlib.util.spec_from_file_location('publisher',H.parent/'island-detail-integration/publish.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=R;m.DOC=D
 sys.argv=['publish.py',str((H/'publication-plan.json').relative_to(R))]+(['--apply'] if apply else []);m.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('step',choices=['prepare','publish']);p.add_argument('--apply',action='store_true');a=p.parse_args();prepare() if a.step=='prepare' else publish(a.apply)
