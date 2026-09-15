"""Stage only officially mapped Ting Kau water using the existing source triangle-cut pipeline."""
import importlib.util,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if __name__=='__main__':
 spec=importlib.util.spec_from_file_location('shared_bridge_hydro',HERE.parent/'tsing-ma/hydro_stage.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.stage(here=HERE,doc=ROOT/'docs/astra-city/ting-kau',bounds=[825850,824200,826800,825550],region='ting-kau',sample_points=[(-8427.765,-8887.478),(-8340,-8710),(-8229.83,-8485.528),(-8140,-8300),(-8019.633,-8059.256)])
