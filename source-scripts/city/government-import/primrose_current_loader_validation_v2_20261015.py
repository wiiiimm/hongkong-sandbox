"""Current read-only loader validation for the four unmodified Primrose originals."""
from pathlib import Path
import os,subprocess,shutil,json
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-primrose-current-loader-validation-v2-20261015'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()and not LOCAL.exists();DOC.mkdir();LOCAL.mkdir()
 source=BASE/'government-xl-primrose-remaining-original-components-v2-20261015';rows=read(source/'selection.json.gz')['rows'];entries=[];forms={};pins={}
 review=read(BASE/'government-xl-primrose-shelter-source-review-v1-20261015/ROOT-SOURCE-REVIEW.json')
 assert review['conditionalBasicSuppressionApprovedForStaging']
 for row in sorted(rows,key=lambda r:r['uid']!='landsd/74573:0'):
  e=dict(row['candidate']['entry']);e.update(priority='landmark',proceduralWindows=False,placementReviewed=False,publicationApproved=False,suppressesBuildingUids=['landsd/74566:0']if row['uid']=='landsd/74573:0'else[])
  if row['uid']!='landsd/74573:0':e['supportDependencies']=[dict(uid='landsd/74573:0',state='candidate',csuid='3143125892P20080429',sha256='fd040d3cca8829a4e31ee37db4212134454c3591fa00ce9195455f0cfe9b42c2')]
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest);entries.append(e)
  tile=row['source']['tile'];p=ROOT/'3d-viewer'/tile;h=digest(p.read_bytes());assert row['source']['building']in read(p)['buildings'];forms[row['uid']]=dict(tile=tile,tileSHA256=h,building=row['source']['building']);pins[str(p.relative_to(ROOT))]=h
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',area='Primrose current original validation',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=4),models=entries))
 save(LOCAL/'catalogue-index.json',dict(models=4,catalogues=['catalogue.json']));save(LOCAL/'source-forms-lookup.json',forms)
 terrain=BASE/'government-xl-primrose-private-terrain-floor-v5-20261015/terrain-candidates.json';candidates=read(terrain)
 for q in candidates:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pins[str(manifest.relative_to(ROOT))]=digest(manifest.read_bytes())
 save(DOC/'inputs.json',dict(currentPins=pins,originalSources={r['uid']:r['sourceSHA256']for r in rows},terrainCandidates=candidates,publication=False))
 rel=lambda p:str(p.relative_to(ROOT))
 cmd=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms-lookup.json'),'--terrain-candidates',rel(terrain),'--out',rel(DOC/'validation.json')]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False))
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
 assert p.returncode==0,'Read validation.log; preserve failed evidence'
 print('Current original loader validation complete; no publication.',flush=True)
if __name__=='__main__':main()
