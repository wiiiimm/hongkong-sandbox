"""Bounded Pui O configuration of the existing source/model/TIN pipeline.
Every output stays staged; there is deliberately no live publication command.
"""
import argparse,gzip,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/pui-o-completion'
CONFIG=json.loads((HERE/'config.json').read_text())
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['fetch','select','build','terrain','source-audit']);args=parser.parse_args()
 sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
 if args.step=='fetch':module('shared_model_fetch',HERE.parent/'mui-wo-models/fetch.py').fetch_tiles(HERE,CONFIG['tiles'])
 elif args.step=='select':
  shared=module('shared_source_selection',HERE.parent/'tai-o-models/select_footprints.py');shared.HERE=HERE;shared.main()
 elif args.step=='build':
  package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  module('shared_model_build',HERE.parent/'mui-wo-models/build.py').build_models(source_dir=HERE,official_path=HERE/'official-selection.json.gz',buildings=package['buildings'],tiles=CONFIG['tiles'],doc=DOC,existing_assets=[],preserved_models={},scope=CONFIG['scope'])
 elif args.step=='terrain':
  package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))
  module('shared_terrain_build',HERE.parent/'terrain-detail/build.py').build_patch(bbox=package['bboxWGS84'],output=HERE/CONFIG['terrainOutput'],detail_paths=sorted((HERE/'staged').glob('*/terrain-source-5m.json')),evidence=DOC,area=CONFIG['area'],rendered_transition=True)
 elif args.step=='source-audit':module('shared_source_audit',HERE.parent/'mui-wo-models/audit_sources.py').audit_sources(HERE,DOC,[])
if __name__=='__main__':main()
