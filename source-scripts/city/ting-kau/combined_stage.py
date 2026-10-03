"""One continuous source-terrain mosaic; reuse immutable regional water constraints.
Only derived staging files are written. No bridge model or live dataset changes.
"""
import importlib.util,json,os,pathlib,hashlib,copy
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];TARGET=HERE/'combined';DOC=ROOT/'docs/astra-city/ting-kau/combined'
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def link(target,source):
 target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():target.symlink_to(os.path.relpath(source,target.parent),target_is_directory=source.is_dir())
def build():
 TARGET.mkdir(exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
 regions=[('tsing-ma',HERE.parent/'tsing-ma',[824200,823000,826900,824000]),('ting-kau',HERE,[825850,824200,826800,825550])]
 for _,source,_ in regions:
  for folder in (source/'terrain/sources').iterdir():
   link(TARGET/'terrain/sources'/folder.name,folder)
   link(TARGET/'terrain/staged'/folder.name,source/'terrain/staged'/folder.name)
 terrain=module('shared_combined_terrain',HERE.parent/'tsing-ma/terrain_stage.py')
 terrain.main(here=TARGET,doc=DOC,bounds=[824200,823000,826900,825550],region='tsing-ma-ting-kau',area='Tsing Ma and Ting Kau bridge cluster')
 patch=TARGET/'terrain-tsing-ma-ting-kau.json';hydro=module('shared_combined_hydro',HERE.parent/'tsing-ma/hydro_stage.py');pieces=[]
 for region,source,bounds in regions:
  local=TARGET/region;local.mkdir(exist_ok=True);evidence=DOC/region;evidence.mkdir(exist_ok=True);link(local/'hydro-sources',source/'hydro-sources')
  result,_,_=hydro.stage(here=local,doc=evidence,bounds=bounds,region=region,terrain_path=patch,sample_points=[])
  old=json.loads((source/f'hydro-{region}.json').read_text());assert result['water']==old['water'],'Mapped source water must not change'
  pieces.append(result)
 cuts={}
 for piece in pieces:
  for cut in piece['terrainCuts']:
   key=json.dumps(cut['georef'],sort_keys=True);target=cuts.setdefault(key,{**cut,'cells':[],'removedAreaM2':0})
   target['cells'].extend(cut['cells']);target['removedAreaM2']+=cut['removedAreaM2']
 for cut in cuts.values():
  # Disjoint source water scopes: no source terrain cell should be overwritten twice.
  indices=[(c['c'],c['r']) for c in cut['cells']] if cut['cells'] and 'c' in cut['cells'][0] else [c.get('index',c.get('cell')) for c in cut['cells']]
  if indices and indices[0] is not None:assert len(indices)==len(set(indices))
 merged={'schemaVersion':1,'region':'tsing-ma-ting-kau','bounds':[min(p['bounds'][0] for p in pieces),min(p['bounds'][1] for p in pieces),max(p['bounds'][2] for p in pieces),max(p['bounds'][3] for p in pieces)],'regions':[{k:v for k,v in p.items() if k not in ['terrainCuts','bedTriangles','bankTriangles','water']} for p in pieces],'illustrativeBed':-4,'source':{'derivation':'Disjoint source water regions, cut against one continuous combined source-terrain grid. Original regional water polygons and foundations are unchanged.'},'water':[r for p in pieces for r in p['water']],'terrainCuts':list(cuts.values()),'bedTriangles':[n for p in pieces for n in p['bedTriangles']],'bankTriangles':[n for p in pieces for n in p['bankTriangles']]}
 (TARGET/'hydro-tsing-ma-ting-kau.json').write_text(json.dumps(merged,separators=(',',':'))+'\n')
 (DOC/'manifest.json').write_text(json.dumps({'terrain':str(patch.relative_to(ROOT)),'terrainSha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'hydro':str((TARGET/'hydro-tsing-ma-ting-kau.json').relative_to(ROOT)),'sourceRegions':[p['region'] for p in pieces],'sourceTerrainSheets':sum(len(list((source/'terrain/sources').iterdir())) for _,source,_ in regions),'sourceWaterUnchanged':True,'livePublished':False},indent=2)+'\n')
if __name__=='__main__':build()
