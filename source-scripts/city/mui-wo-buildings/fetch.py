"""Fetch a bounded Mui Wo subset directly from LandsD's official CSDI service.
Snapshots and requests are retained; rebuilds do not require live services.
"""
import datetime,gzip,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
META='https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html'
SPEC='https://static.csdi.gov.hk/csdi-webpage/view/common/6eda6a766520bcffe13206378c060a59bdb54a3c6f92480b1f01174d25fd7194'
STATISTICS='https://static.csdi.gov.hk/csdi-webpage/view/common/baf02be1c41e23608743d1a11e77544276f84b83729e325cdaf805bf825fae4d'
TERMS='https://portal.csdi.gov.hk/csdi-webpage/doc/TNC'
BBOX=[113.97922444961371,22.249711576500182,114.0180525556901,22.28564402349982]
def request(url,parameters=None):
 full=url+('?' + urllib.parse.urlencode(parameters) if parameters else '')
 req=urllib.request.Request(full,headers={'User-Agent':'HongKongSandbox-Astra/MuiWo building coverage (bounded CSDI open data)'})
 with urllib.request.urlopen(req,timeout=90) as response:raw=response.read()
 return raw,full

def main():
 target=HERE/'landsd-mui-wo.json.gz'
 if target.exists():print('Using retained',target);return
 queries=[]
 for filename,url in [('service-metadata.json',BASE),('layer-metadata.json',BASE+'/0')]:
  raw,query=request(url,{'f':'pjson'});obj=json.loads(raw)
  if obj.get('error'):raise ValueError(obj['error'])
  (HERE/filename).write_bytes(raw);queries.append(dict(file=filename,url=query))
 for filename,link in [('dataset-metadata.html',META),('simplified-data-specification.html',SPEC),('dataset-statistics.json',STATISTICS),('terms-of-use.html',TERMS)]:
  raw,url=request(link);(HERE/filename).write_bytes(raw);queries.append(dict(file=filename,url=url))
 params=dict(f='json',where='1=1',geometry=','.join(map(str,BBOX)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',returnIdsOnly='true')
 raw,url=request(BASE+'/0/query',params);ids=json.loads(raw)
 if ids.get('error'):raise ValueError(ids['error'])
 (HERE/'query-object-ids.json').write_bytes(raw);queries.append(dict(file='query-object-ids.json',url=url))
 count_params=dict(params);count_params.pop('returnIdsOnly');count_params['returnCountOnly']='true'
 raw,url=request(BASE+'/0/query',count_params);count=json.loads(raw)
 if count.get('count')!=len(ids['objectIds']):raise ValueError('Count differs from complete ID query')
 (HERE/'query-count.json').write_bytes(raw);queries.append(dict(file='query-count.json',url=url))
 object_ids=sorted(ids['objectIds']);features=[];sr=None
 for offset in range(0,len(object_ids),150):
  params=dict(f='json',objectIds=','.join(map(str,object_ids[offset:offset+150])),outFields='*',returnGeometry='true',outSR=2326,orderByFields='OBJECTID')
  raw,url=request(BASE+'/0/query',params);page=json.loads(raw)
  if page.get('error') or page.get('exceededTransferLimit'):raise ValueError(page.get('error') or 'Truncated response')
  features.extend(page['features']);sr=page.get('spatialReference',sr);queries.append(dict(page=offset//150,url=url,count=len(page['features'])))
 if sorted(f['attributes']['OBJECTID'] for f in features)!=object_ids:raise ValueError('Fetched IDs do not match complete bounded query')
 output=dict(source=BASE+'/0',datasetId='landsd_rcd_1637211194312_35158',datasetVersion='Building_Outline_Public_v20260819',retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),bboxWGS84=BBOX,spatialReference=sr,features=features)
 target.write_bytes(gzip.compress(json.dumps(output,separators=(',',':'),ensure_ascii=False).encode(),mtime=0));(HERE/'requests.json').write_text(json.dumps(queries,indent=2)+'\n')
 print(len(features),'official building forms;',sr)
if __name__=='__main__':main()
