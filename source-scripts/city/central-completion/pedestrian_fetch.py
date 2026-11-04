"""Retain the bounded official 3D pedestrian network; reuse retry/provenance helpers."""
import concurrent.futures,gzip,importlib.util,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('existing_public_request',HERE.parent/'landsd-territory/source.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared);shared.AGENT='HongKongSandbox-Astra/Central pedestrian source review'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637222018065_52265/MapServer'
def cached(name,url,params):
 path=HERE/'pedestrian-source'/name;meta=path.with_name(path.name+'.request.json');path.parent.mkdir(exist_ok=True)
 if path.exists() and meta.exists():return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
 raw,info=shared.request(url,params);shared.atomic(path,gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw);shared.save_json(meta,info);return json.loads(raw)
def main():
 config=json.loads((HERE/'config.json').read_text());service=cached('service.json',BASE,{'f':'json'});layer=cached('layer.json',BASE+'/0',{'f':'json'});assert layer['hasZ']
 params={'f':'json','geometry':','.join(map(str,config['sourceBoundsHK1980'])),'geometryType':'esriGeometryEnvelope','inSR':2326,'spatialRel':'esriSpatialRelIntersects','where':'1=1'}
 ids=cached('object-ids.json',BASE+'/0/query',{**params,'returnIdsOnly':'true'})['objectIds'];count=cached('count.json',BASE+'/0/query',{**params,'returnCountOnly':'true'})['count'];assert count==len(set(ids));ids=sorted(ids)
 def batch(i):
  wanted=ids[i:i+150];data=cached(f'page-{i//150:04d}.json.gz',BASE+'/0/query',{'f':'json','objectIds':','.join(map(str,wanted)),'outFields':'*','outSR':2326,'returnGeometry':'true','returnZ':'true','orderByFields':'OBJECTID'});assert not data.get('exceededTransferLimit');assert sorted(f['attributes']['OBJECTID'] for f in data['features'])==wanted
  return data
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:pages=list(pool.map(batch,range(0,len(ids),150)))
 features=[f for page in pages for f in page['features']];assert sorted(f['attributes']['OBJECTID'] for f in features)==ids
 for f in features:
  assert f['geometry'].get('paths') and all(len(p)==3 for line in f['geometry']['paths'] for p in line)
 out={'schemaVersion':1,'datasetId':'landsd_rcd_1637222018065_52265','source':BASE+'/0','retrievedAtUTC':shared.utc(),'boundsHK1980':config['sourceBoundsHK1980'],'spatialReference':pages[0]['spatialReference'],'count':count,'hasZ':True,'verticalDatum':'Hong Kong Principal Datum','sourceAccuracy':{'horizontalMetres':1,'verticalMetres':2,'basis':'Lands Department 3DPN Data Dictionary v2.2 (December 2025), sections 1.3–1.4'},'dataDictionary':'pedestrian-source/3DPN_DataDictionary_v2.2.pdf','features':features}
 shared.atomic(HERE/'pedestrian-network.json.gz',gzip.compress(shared.encode(out),mtime=0));print(json.dumps({'sourceFeatures':count,'bytes':(HERE/'pedestrian-network.json.gz').stat().st_size,'completeObjectIds':True,'sourceZRetained':True}),flush=True)
if __name__=='__main__':main()
