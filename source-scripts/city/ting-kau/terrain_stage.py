"""Stage a 5m Ting Kau patch with the existing shared bridge terrain pipeline."""
import importlib.util,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if __name__=='__main__':
 spec=importlib.util.spec_from_file_location('shared_bridge_terrain',HERE.parent/'tsing-ma/terrain_stage.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.main(here=HERE,doc=ROOT/'docs/astra-city/ting-kau',bounds=[825850,824200,826800,825550],region='ting-kau',area='Ting Kau Bridge foundations')
