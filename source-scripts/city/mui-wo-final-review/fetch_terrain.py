"""Only adjoining 10-SW-8C terrain is needed to remove a false source-edge blend.
Reuse the retained index and existing bounded downloader/decoder; no building import.
"""
import hashlib,importlib.util,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import stage
from resample_model_terrain import resample

def main():
 source=HERE.parent/'mui-wo-completion/index.json';index=json.loads(source.read_text());index['features']=[f for f in index['features'] if f['attributes']['SHEETNO']=='10-SW-8C'];assert len(index['features'])==1
 (HERE/'index.json').write_text(json.dumps(index,indent=2)+'\n');(HERE/'index-provenance.json').write_text(json.dumps({'retainedIndex':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'selection':'One exact existing SHEETNO 10-SW-8C; metadata and attributes unchanged. Needed across the 7D eastern edge for buildings landsd/201705:0 and landsd/206970:0.'},indent=2)+'\n')
 spec=importlib.util.spec_from_file_location('existing_range_fetch',HERE.parent/'mui-wo-models/fetch.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.fetch_tiles(here=HERE,tiles=['10-SW-8C'],member_prefixes=['TERRAIN'])
 source=HERE/'sources/10-SW-8C';assets=HERE/'staged/10-SW-8C';record=json.loads((source/'download.json').read_text());assert all(e['name'].startswith('TERRAIN') for e in record['entries'])
 if not (assets/'manifest.json').exists():stage(source/'10-SW-8C.zip',record,HERE.parent/'mui-wo-buildings/landsd-mui-wo.json.gz',assets)
 if not (assets/'terrain-source-5m.json').exists():resample(assets,assets)
 manifest=json.loads((assets/'manifest.json').read_text());assert manifest['models']==[]
if __name__=='__main__':main()
