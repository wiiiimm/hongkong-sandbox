"""Publish verified compact assets and the shared Central terrain patch locally.
Original source tiles and all other regional hydro/terrain remain unchanged.
"""
from pathlib import Path
import json,shutil
r=Path(__file__).resolve().parents[3];src=r/'source-scripts/city/central-completion';out=r/'3d-viewer/city/data';p=out/'manifest.json';m=json.loads(p.read_text())
for folder,name in [('compact','central'),('compact-followup','central-west-wing'),('compact-corridor','island-corridor')]:
 target=out/'official-models'/name;target.mkdir(parents=True,exist_ok=True)
 cat=json.loads((src/folder/'catalogue.json').read_text());cat['kind']='official-model-catalogue';cat['loadingPolicy']='Progressive exact-source detail. Keep the existing footprint until the individual model passes decoding, identity, geometry and memory-budget checks. No whole-section acceptance is implied.'
 (target/'catalogue.json').write_text(json.dumps(cat,ensure_ascii=False,separators=(',',':'))+'\n')
 for e in cat['models']:
  asset=target/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/folder/e['asset'],asset)
 url=f'city/data/official-models/{name}/catalogue.json'
 if url not in m.setdefault('officialModelCatalogues',[]):m['officialModelCatalogues'].append(url)
patch=src/'terrain-central.json';shutil.copyfile(patch,out/patch.name)
m['terrainPatches']=[p for p in m['terrainPatches'] if not p['url'].endswith('terrain-central.json')]
m['terrainPatches'].append({'url':'city/data/'+patch.name,'resolution':5,'area':'Central and adjoining island corridor','source':{'provider':'Lands Department / Hong Kong SAR Government','note':'16 retained original terrain TIN sheets and archival DTM fallback. EPSG:2326 / HKPD; source sheet union plus existing outer transition. Terrain-source revisions retained in patch metadata.'}})
p.write_text(json.dumps(m,ensure_ascii=False,separators=(',',':'))+'\n');print('Published 37 compact models and source terrain; existing source building fields, terrain and hydro regions retained.')
