"""Reuse the city arrival repairer, keeping this extension's evidence separate."""
import importlib.util,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent))
spec=importlib.util.spec_from_file_location('shared_arrival_repair',HERE.parent/'repair_arrivals.py');repair=importlib.util.module_from_spec(spec);spec.loader.exec_module(repair)
if __name__=='__main__':
 repair.DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension/arrival-repairs'
 repair.main()
