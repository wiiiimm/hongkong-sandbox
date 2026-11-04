"""Reuse the existing official map-layer fetcher for the bounded Ting Kau corridor."""
import importlib.util,pathlib
HERE=pathlib.Path(__file__).resolve().parent
if __name__=='__main__':
 spec=importlib.util.spec_from_file_location('shared_bridge_hydro_fetch',HERE.parent/'tsing-ma/hydro_fetch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.HERE=HERE;m.BOUNDS=[825850,824200,826800,825550];m.fetch()
