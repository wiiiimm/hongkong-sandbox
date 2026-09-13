"""Reproduce the bounded terrain-only cache using the established byte-range fetcher."""
import importlib.util,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('city_source_fetch',HERE.parent/'mui-wo-models/fetch.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
if __name__=='__main__':
 config=json.loads((HERE/'terrain-config.json').read_text());shared.fetch_tiles(here=HERE,tiles=[t['sheet'] for t in config['tiles']],member_prefixes=config['memberPrefixes'])
