"""Query the official Central sheet index and reuse the bounded original-entry fetcher."""
import argparse,importlib.util,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
DATASET='landsd_rcd_1742809441342_98380'
def index():
 config=json.loads((HERE/'config.json').read_text());params=dict(f='json',geometry=','.join(map(str,config['sourceBoundsHK1980'])),geometryType='esriGeometryEnvelope',inSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',outSR=2326)
 url='https://portal.csdi.gov.hk/server/rest/services/common/'+DATASET+'/FeatureServer/0/query?'+urllib.parse.urlencode(params)
 target=HERE/'index.json'
 if not target.exists():target.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 data=json.loads(target.read_text());assert data.get('features') and not data.get('exceededTransferLimit'),data
 (HERE/'index-request.txt').write_text(url+'\n')
 sheets=[f['attributes']['SHEETNO'] for f in data['features']]
 config['tiles']=sheets;(HERE/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sheets':len(sheets),'tiles':sheets}),flush=True)
 return sheets
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--index-only',action='store_true');args=parser.parse_args();sheets=index()
 if not args.index_only:
  spec=importlib.util.spec_from_file_location('existing_model_fetch',HERE.parent/'mui-wo-models/fetch.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.fetch_tiles(here=HERE,tiles=sheets)
