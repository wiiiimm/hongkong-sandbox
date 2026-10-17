"""Capture unchanged original source against current production ground."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from require_remaining_xl import require_remaining
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-apex227942-current-capture-v2-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/227942:0';SHA='83cc3270d1de801eace0d72a63dfc470df8e2862b8d6399f0422e0a4ceb8ed0c'
COUNT=BASE/'government-xl-namcheong244683-original-installed-v1-20261017/full-xl-current-count.json'
ORIGINAL=BASE/'government-xl-remaining-20260923/selection.json.gz'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());current=read(manifest)
 row=next(r for r in read(ORIGINAL)['rows']if r['uid']==UID);assert row['sourceSHA256']==SHA
 pins={};refs=[Path(__file__),COUNT,ORIGINAL]
 def pin(p):pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());refs.append(p)
 pin(manifest)
 forms=[]
 for t in current['tiles']:
  p=ROOT/'3d-viewer'/t['url']
  for b in read(p)['buildings']:
   if b['uid']==UID:forms.append(dict(building=b,tile=t['url'],tileSHA256=digest(p.read_bytes())));pin(p)
 assert len(forms)==1 and forms[0]['building']['buildingCSUID']==row['source']['building']['buildingCSUID']
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;assert all(m['uid']!=UID for m in read(p)['models']);pin(p)
 entry=dict(row['native']['model']['candidate'],sourceTile=row['native']['sheet'],rootTranslation=[-834500,0,816500]);row['candidate']=dict(entry=entry,path=str((HERE/'local/government-xl-source-http-retry-20260924/recovered'/entry['asset']).relative_to(ROOT)))
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;pin(asset)
 dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes())
 row['source']=forms[0];row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)))
 DOC.mkdir();(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes())
 save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=start));save(LOCAL/'catalogue.json',dict(models=[row['candidate']['entry']]));save(DOC/'terrain-candidates.json',[])
 closure=DOC/'production-module-closure.json'
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(closure)],cwd=ROOT,check=True)
 c=read(closure);assert c['completeAuditedLiteralImportClosure'] and c['unsupportedDynamicImports']==0
 for p,h in c['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pin(ROOT/p)
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==1 and not metrics['rows'][0].get('error')
 geometry=read(LOCAL/'runtime-geometry.json.gz');assert [r['uid']for r in geometry['rows']]==[UID]
 for p,h in geometry['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pin(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 assert reservations.owns(lease)
 refs.extend([dest,closure,DOC/'selection.json.gz',DOC/'metrics.json',LOCAL/'runtime-geometry.json.gz'])
 result=module('yoho_current_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex227942-current-original-runtime-capture-v2',refs,dict(uids=[UID],sourceSHA256=SHA,currentManifestSHA256=start,sourceGeometryChanges=0,noTerrainProposal=True,fullAcceptance=False,publication=False,newlyInstalled=0,metrics=metrics['rows']))
 print(result['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 require_remaining(COUNT,UID,SHA);assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('apex227942-current-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
