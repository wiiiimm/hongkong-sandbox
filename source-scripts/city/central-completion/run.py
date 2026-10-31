"""Thin Central configuration over the existing source selection/model/terrain pipeline."""
import argparse,gzip,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/central-completion'
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['select','build','terrain']);args=parser.parse_args();config=json.loads((HERE/'config.json').read_text());sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
 if args.step=='select':
  existing=load('shared_area_source_selection',HERE.parent/'tai-o-models/select_footprints.py');existing.HERE=HERE;existing.main()
 else:
  package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  if args.step=='build':load('shared_model_builder',HERE.parent/'mui-wo-models/build.py').build_models(source_dir=HERE,official_path=HERE/'official-selection.json.gz',buildings=package['buildings'],tiles=config['tiles'],doc=DOC,existing_assets=[],preserved_models={b['uid']:b['modelGeometry'] for b in package['buildings'] if b.get('modelGeometry')},scope=config['scope'])
  else:
   # The existing mosaic requires complete source grids, so include the full
   # retained sheet union in the terrain crop. This does not widen the section
   # acceptance window or alter any original samples.
   from pyproj import Transformer
   paths=sorted((HERE/'staged').glob('*/terrain-source-5m.json'));native=[]
   for path in paths:
    d=json.loads(path.read_text());g=d['meta']['georef'];native.extend([(g['bE'],g['bN']),(g['bE']+(d['w']-1)*5,g['bN']-(d['h']-1)*5)])
   inverse=Transformer.from_crs(2326,4326,always_xy=True);points=[inverse.transform(e,n) for e,n in native]
   bbox=[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
   (DOC/'terrain-crop.json').write_text(json.dumps({'reviewBBoxWGS84':package['bboxWGS84'],'terrainBBoxWGS84':bbox,'policy':'Complete original source grid union plus existing importer transition margin; geographic section acceptance still uses the smaller review window.'},indent=2)+'\n')
   load('shared_terrain_builder',HERE.parent/'terrain-detail/build.py').build_patch(bbox=bbox,output=HERE/'terrain-central.json',detail_paths=paths,evidence=DOC,area=config['area'],rendered_transition=True)
