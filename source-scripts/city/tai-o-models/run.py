"""Area configuration for the existing government model pipeline; no renderer fork."""
import argparse,gzip,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];CONFIG=json.loads((HERE/'config.json').read_text());DOC=ROOT/'docs/astra-city/tai-o-models'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['fetch','select','build','terrain','publish']);args=parser.parse_args()
 sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
 if args.step=='fetch':module('shared_model_fetch',HERE.parent/'mui-wo-models/fetch.py').fetch_tiles(HERE,CONFIG['tiles'])
 elif args.step=='select':module('tai_o_source_selection',HERE/'select_footprints.py').main()
 elif args.step=='build':
  package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  module('shared_model_build',HERE.parent/'mui-wo-models/build.py').build_models(source_dir=HERE,official_path=HERE/'official-selection.json.gz',buildings=package['buildings'],tiles=CONFIG['tiles'],doc=DOC,existing_assets=[],preserved_models={},scope=CONFIG['scope'])
 elif args.step=='terrain':
  package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  module('shared_terrain_build',HERE.parent/'terrain-detail/build.py').build_patch(bbox=package['bboxWGS84'],output=ROOT/'3d-viewer/city/data'/CONFIG['terrainOutput'],detail_paths=sorted((HERE/'staged').glob('*/terrain-source-5m.json')),evidence=DOC,area=CONFIG['area'],rendered_transition=True)
 elif args.step=='publish':
  module('shared_model_publish',HERE.parent/'mui-wo-models/publish.py').publish_models(payload_path=HERE/'model-geometries.json.gz',package_path=HERE/'building-selection.json.gz',terrain_path=ROOT/'3d-viewer/city/data'/CONFIG['terrainOutput'],doc=DOC,foundation_mode='preserve',area=CONFIG['area'])
if __name__=='__main__':main()
