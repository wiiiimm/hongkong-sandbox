"""Retain official bridge-area index and original infrastructure glTF/bin entries.
Reuses the project's bounded range downloader; no image/texture downloads.
"""
import importlib.util,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
BOUNDS=[824200,823000,826900,824000]
def index(dataset,filename):
 url='https://portal.csdi.gov.hk/server/rest/services/common/'+dataset+'/FeatureServer/0/query?'+urllib.parse.urlencode(dict(f='json',geometry=','.join(map(str,BOUNDS)),geometryType='esriGeometryEnvelope',inSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',outSR=2326))
 path=HERE/filename
 if not path.exists():path.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 data=json.loads(path.read_text());assert data.get('features') and not data.get('exceededTransferLimit')
 path.with_suffix('.request.txt').write_text(url+'\n');return data
if __name__=='__main__':
 data=index('landsd_rcd_1742809441342_98380','index.json');index('landsd_rcd_1671676915450_88604','individual-index.json')
 spec=importlib.util.spec_from_file_location('shared_fetch',HERE.parent/'mui-wo-models/fetch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.fetch_tiles(here=HERE,tiles=[f['attributes']['SHEETNO'] for f in data['features']],member_prefixes=['INFRASTRUCTURE/'])
 for folder,filename,tiles,prefixes in [('towers','index.json',['10-NE-2D','10-NE-3B'],['BUILDING/B2501123381','BUILDING/B2502223342','BUILDING/B2633023775','BUILDING/B2634223737']),('individual','individual-index.json',['10-NE-2D','10-NE-3A'],['GENERIC/','INFRASTRUCTURE/']),('terrain','index.json',[f['attributes']['SHEETNO'] for f in data['features']],['TERRAIN'])]:
  target=HERE/folder;target.mkdir(exist_ok=True);(target/'index.json').write_bytes((HERE/filename).read_bytes());m.fetch_tiles(here=target,tiles=tiles,member_prefixes=prefixes)
