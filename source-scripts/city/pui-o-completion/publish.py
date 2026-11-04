"""Opt-in local publication through the existing territory publisher.
Default is a staged plan only. --apply is reserved for root's integration turn.
"""
import argparse,gzip,hashlib,json,pathlib,shutil,sys
from run import HERE,ROOT,DOC,CONFIG,module
OUT=ROOT/'3d-viewer/city/data'
CATALOGUE_URL='city/data/official-models/pui-o/catalogue.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
IMMUTABLE=('id','uid','objectId','buildingCSUID','buildingId','rings','name','zh','kind','structureType','baseHeightHKPD','topHeightHKPD','sourceDataset')
def plan():
 selection=load(HERE/'building-selection.json.gz');byuid={b['uid']:b for b in selection['buildings']};manifest=load(OUT/'manifest.json');current={}
 for tile in {b['tile'] for b in byuid.values()}:
  for b in load(OUT/'tiles'/(tile+'.json'))['buildings']:
   if b['uid'] in byuid:current[b['uid']]=b
 assert current.keys()==byuid.keys(),'Current source selection changed'
 for uid,b in current.items():
  for key in IMMUTABLE:assert b.get(key)==byuid[uid].get(key),(uid,key,'Source mismatch; review before publishing')
  assert 'modelGeometry' not in b,'A newer detailed model already exists; review rather than overwrite it'
 compact=load(HERE/'compact/catalogue.json');proof=load(DOC/'compact-assets.json');runtime=load(DOC/'runtime-verification.json');audit=load(DOC/'terrain-audit.json')
 assert sha(HERE/'compact/catalogue.json')==proof['catalogueSha256']==runtime['catalogueSha256']
 assert sha(HERE/'terrain-pui-o.json')==audit['terrain']['sha256'];assert compact['counts']['packedModels']==runtime['models']==681
 for entry in compact['models']:assert sha(HERE/'compact'/entry['asset'])==entry['sha256']
 return {'staged':True,'area':'Pui O','selectedForms':len(byuid),'matchedModels':len(compact['models']),'sourceUpdates':{'estimatedBasesOnlyWhenBothSourceElevationsAbsent':audit['counts']['baseEstimatesChanged'],'sourceRecordedFieldsUnchanged':True,'foundationMode':'preserve'},'terrainSource':str((HERE/'terrain-pui-o.json').relative_to(ROOT)),'terrainDestination':'3d-viewer/city/data/terrain-pui-o.json','catalogueSource':str((HERE/'compact/catalogue.json').relative_to(ROOT)),'catalogueURL':CATALOGUE_URL,'catalogueManifestKey':'officialModelCatalogues','existingCatalogues':manifest.get('officialModelCatalogues',[]),'existingPatchURLs':[p['url'] for p in manifest.get('terrainPatches',[])],'retainedHydroSha256':sha(OUT/'terrain.json'),'policy':'Reuse publish_models with an empty embedded geometry map: update labelled absent-elevation estimates/terrain audit only, then append compact catalogue. All current forms, other models, patches, hydro and existing manifest entries are preserved.','applyCommand':'/tmp/astra-city-venv/bin/python source-scripts/city/pui-o-completion/publish.py --apply'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args();report=plan();(DOC/'publication-plan.json').write_text(json.dumps(report,indent=2)+'\n')
 if not args.apply:print(json.dumps(report,indent=2));return
 before=load(OUT/'manifest.json');selection=load(HERE/'building-selection.json.gz');tileids={b['tile'] for b in selection['buildings']};selected={b['uid'] for b in selection['buildings']};prior={b['uid']:b for tile in tileids for b in load(OUT/'tiles'/(tile+'.json'))['buildings']};existingPatches={p['url']:p for p in before.get('terrainPatches',[])};patchHashes={url:sha(ROOT/'3d-viewer'/url) for url in existingPatches}
 # This small derived payload directs the existing publisher to refresh terrain
 # estimates without embedding 31 MB of model arrays into one building tile.
 baked=load(HERE/'model-geometries.json.gz');terrainOnly=HERE/'compact-publication-metadata.json.gz';metadata={'schemaVersion':1,'kind':'official-building-model-geometries','byBuildingUid':{},'sourceManifests':baked['sourceManifests'],'note':'Source models are independently verified compact catalogue assets. Empty embedded map is intentional; only staged terrain and missing source elevation estimates are refreshed by the existing publisher.'};terrainOnly.write_bytes(gzip.compress(json.dumps(metadata,separators=(',',':')).encode(),mtime=0))
 shutil.copyfile(HERE/'terrain-pui-o.json',OUT/'terrain-pui-o.json');shutil.copytree(HERE/'compact',OUT/'official-models/pui-o',dirs_exist_ok=True)
 sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
 module('shared_territory_model_publish',HERE.parent/'mui-wo-models/publish.py').publish_models(payload_path=terrainOnly,package_path=HERE/'building-selection.json.gz',terrain_path=OUT/'terrain-pui-o.json',doc=DOC,foundation_mode='preserve',area='Pui O')
 manifest=load(OUT/'manifest.json');catalogues=list(manifest.get('officialModelCatalogues',[]))
 if CATALOGUE_URL not in catalogues:catalogues.append(CATALOGUE_URL)
 manifest['officialModelCatalogues']=catalogues
 sys.path.insert(0,str(HERE.parent));module('shared_city_tiles',HERE.parent/'publish_tiles.py').dump(OUT/'manifest.json',manifest)
 assert manifest['counts']==before['counts'];assert sha(OUT/'terrain.json')==report['retainedHydroSha256'],'Coarse terrain/hydro changed'
 assert all(sha(ROOT/'3d-viewer'/url)==digest for url,digest in patchHashes.items())
 assert all(p in manifest['terrainPatches'] for p in existingPatches.values());assert all(url in manifest['officialModelCatalogues'] for url in before.get('officialModelCatalogues',[]))
 for tile in tileids:
  for b in load(OUT/'tiles'/(tile+'.json'))['buildings']:
   old=prior[b['uid']]
   if b['uid'] not in selected:assert b==old
   else:
    for key in IMMUTABLE:assert b.get(key)==old.get(key),(b['uid'],key)
    assert 'modelGeometry' not in b
 report.update(staged=False,published=True,manifestSha256=sha(OUT/'manifest.json'),embeddedGeometryAdded=0,existingPatchesAndHydroPreserved=True,cityCounts=manifest['counts']);(DOC/'publication.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
