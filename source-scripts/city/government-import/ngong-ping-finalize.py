"""Freeze the runtime-clean Ngong Ping / Lantau peaks subset; no AI or geometry edits."""
import gzip,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE='government-ngong-ping-peaks-473-20260918';BATCH='government-ngong-ping-peaks-compute-20260918'
DOC=ROOT/'docs/astra-city/government-import'/SOURCE;LOCAL=HERE/'local'/SOURCE;STAGE=HERE/'accepted'/BATCH
def read(path):
 path=Path(path);raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return str(Path(path).relative_to(ROOT))

def main():
 validation=read(DOC/'runtime-validation.json');invalid={r['uid'] for r in validation['results'] if r['outcome']=='validation-exception'}
 catalogue=read(STAGE/'catalogue.json');catalogue['models']=[m for m in catalogue['models'] if m['uid'] not in invalid]
 for model in catalogue['models']:model['publicationApproved']=True
 valid={m['uid'] for m in catalogue['models']};assert valid;catalogue['counts']={'packedModels':len(valid)};save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(valid),'catalogues':['catalogue.json']})
 selection=read(DOC/'check-selection.json.gz');selected={r['uid']:r for r in selection['rows']};rows=[selected[uid] for uid in sorted(valid)];selection={**selection,'batch':BATCH,'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'rows':rows,'aiCalls':0};save(DOC/'runtime-selection.json.gz',selection)
 forms={uid:selected[uid]['source'] for uid in sorted(valid)};save(LOCAL/'runtime-source-forms.json',forms)
 browser_forms=[]
 for uid in sorted(valid):
  form=dict(selected[uid]['source']['building']);form['tile']=Path(selected[uid]['source']['tile']).stem;browser_forms.append(form)
 save(STAGE/'source-forms.json',browser_forms)
 terrain=read(DOC/'terrain-pass.json');top=[];metric=[]
 for entry in terrain['topLevelTerrainPatches']:
  path=ROOT/entry['source'];patch=read(path);targets=sorted(set(patch['meta']['targetUids'])&valid)
  if not targets:continue
  patch['meta']['targetUids']=targets;save(path,patch);entry={**entry,'sha256':sha(path)};top.append(entry);metric.append({'path':entry['source'],'sha256':entry['sha256']})
 bundles=[]
 for bundle_name in terrain['nestedTerrainBundles']:
  path=ROOT/bundle_name;bundle=read(path);patches=[]
  for patch in bundle['patches']:
   targets=sorted(set(patch['meta']['targetUids'])&valid)
   if targets:patch['meta']['targetUids']=targets;patches.append(patch)
  if not patches:continue
  bundle['patches']=patches;save(path,bundle);bundles.append(bundle_name)
  parent=ROOT/'3d-viewer'/bundle['parentTerrainURL'];wrapper={**read(parent),'patches':read(parent).get('patches',[])+patches};wrapper_path=LOCAL/'metric-terrain'/Path(bundle['parentTerrainURL']).name;save(wrapper_path,wrapper);metric.append({'path':rel(wrapper_path),'sha256':sha(wrapper_path),'replaces':{'url':bundle['parentTerrainURL'],'sha256':bundle['parentSha256']}})
 save(DOC/'terrain-candidates.json',metric)
 destination=f'city/data/official-models/{BATCH}/catalogue.json';plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination,'terrain':bundles}],'topLevelTerrainPatches':top};save(STAGE/'plan.json',plan)
 group_reps=[]
 for group in terrain['groups']:
  options=sorted(set(group['uids'])&valid)
  if options:group_reps.append(options[0])
 browser_uids=sorted(set(group_reps));assert browser_uids
 browser_terrain=[{'source':entry['source'],'destination':entry['destination'],'resolution':entry['resolution'],'area':entry['area']} for entry in top]
 for bundle_name in bundles:
  bundle=read(ROOT/bundle_name);parent=ROOT/'3d-viewer'/bundle['parentTerrainURL'];wrapper={**read(parent),'patches':read(parent).get('patches',[])+bundle['patches']};path=LOCAL/'browser-terrain'/Path(bundle['parentTerrainURL']).name;save(path,wrapper);browser_terrain.append({'source':rel(path),'destination':bundle['parentTerrainURL'],'resolution':wrapper['cell'],'area':'Ngong Ping / Lantau peaks government terrain','replaces':{'url':bundle['parentTerrainURL']}})
 save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':browser_terrain,'fitBox':True,'browserUids':browser_uids,'failureTestUids':browser_uids})
 exact=read(DOC/'exact-pass-results.json.gz');exact_holds={r['uid']:r['reasons'] for r in exact['rows'] if not r['publicationCandidate']};terrain_holds={uid:[reason] for uid,reason in terrain['held'].items()};runtime_holds={r['uid']:[r['error']] for r in validation['results'] if r['uid'] in invalid};holds={**exact_holds,**terrain_holds,**runtime_holds};assert not(valid&set(holds)) and valid|set(holds)==set(selected)
 save(DOC/'terminal-states.json',{'batch':BATCH,'modelsProcessed':len(selected),'installable':len(valid),'held':len(holds),'humanCounts':{'installed':0,'to-do':len(valid),'held-human':0,'held-ai':0,'held-unknown':len(holds),'in-process':0},'heldRows':[{'uid':uid,'reasons':reasons,'requiresAI':False,'requiresUserDecision':False,'needsMoreCompute':False,'scriptedWorkComplete':True,'humanStatus':'held-unknown'} for uid,reasons in sorted(holds.items())],'aiCalls':0,'modelGeometryChanges':0,'publication':False})
 print(json.dumps({'installable':len(valid),'held':len(holds),'browserRepresentatives':len(browser_uids),'topLevelPatches':len(top),'nestedBundles':len(bundles),'aiCalls':0}))
if __name__=='__main__':main()
