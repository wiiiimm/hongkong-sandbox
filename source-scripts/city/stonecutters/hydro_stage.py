"""Cut only original source-mapped water; retain container-port land in plan."""
import importlib.util
from fetch import HERE,ROOT,BOUNDS
if __name__=='__main__':
    spec=importlib.util.spec_from_file_location('shared_bridge_hydro',HERE.parent/'tsing-ma/hydro_stage.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.stage(here=HERE,doc=ROOT/'docs/astra-city/stonecutters',bounds=BOUNDS,region='stonecutters',sample_points=[[-4634.028,-4573.747],[-4490,-4450],[-4220,-4230],[-3970,-4030],[-3849.81,-3924.645]])
