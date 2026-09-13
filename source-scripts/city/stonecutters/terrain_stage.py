"""Reuse the common original-TIN resampling and terrain patch pipeline."""
import importlib.util
from fetch import HERE,ROOT,BOUNDS
if __name__=='__main__':
    spec=importlib.util.spec_from_file_location('shared_bridge_terrain',HERE.parent/'tsing-ma/terrain_stage.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.main(here=HERE,doc=ROOT/'docs/astra-city/stonecutters',bounds=BOUNDS,region='stonecutters',area='Stonecutters Bridge and port foundations')
