"""Fresh read-only current renderer capture of unchanged native254491; no reacceptance."""
import subprocess,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PHYSICAL=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';BATCH='government-xl-parkview-block6-fresh-current-carrier-capture-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/254491:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);original=read(B/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011/selection.json.gz');row=next(r for r in original['rows']if r['uid']==UID)
 entries=[]
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']==UID:entries.append((p,e))
 assert len(entries)==1;cat,entry=entries[0];asset=cat.parent/entry['asset'];raw=asset.read_bytes();assert digest(raw)==entry['sha256']==row['sourceSHA256'];destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
 form=next(r['building']for r in read(PHYSICAL/'neighbour-inputs.json.gz')['rows']if r['building']['uid']==UID);row.update(source=dict(building=form,tile=row['source']['tile']),candidate=dict(path=str(destination.relative_to(ROOT)),entry=entry));save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=start['sha256']));save(DOC/'terrain-candidates.json',[]);save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[entry],counts=dict(packedModels=1)));save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
 rel=lambda p:str(p.relative_to(ROOT));subprocess.run(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')],cwd=ROOT,check=True);assert ref(manifest)==start
 save(DOC/'literal-source-inputs.json.gz',dict(rows=[dict(uid=UID,path=str(destination.relative_to(ROOT)),entry=entry,building=form)],currentManifest=start,currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']],evidenceRefs=[ref(DOC/'selection.json.gz'),ref(destination),ref(cat)]));subprocess.run(['node',str(HERE/'parkview_block6_current_carrier_actual_render_attributes_20261011.mjs'),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')],cwd=ROOT,check=True);assert ref(manifest)==start
 save(DOC/'capture-scope.json',dict(currentManifest=start,installedCarrierSource=ref(asset),installedCatalogue=ref(cat),notNativeReacceptance=True,sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(freshCurrentCarrierCaptured=True)),flush=True)
if __name__=='__main__':main()
