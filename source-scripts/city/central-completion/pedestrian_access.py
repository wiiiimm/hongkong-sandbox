"""Retain the selected official opening-time tables and source specifications."""
import gzip,json,pathlib
from pedestrian_fetch import HERE,BASE,cached,shared

def main():
 refs={
  '3DPN_DataDictionary_v2.2.pdf':'https://static.csdi.gov.hk/csdi-webpage/download/common/a373f1e864fcdc20e033423e91abfc6409a1f911984323639957e7d6199f4f54',
  'metadata.html':'https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637222018065_52265/html',
  'specification.html':'https://static.csdi.gov.hk/csdi-webpage/view/common/bef82cb27e1ff780cb48e47b05eae5813266079b5046c9cd41fbcac97e4d441a',
  'escalator-operation.html':'https://www.td.gov.hk/en/transport_in_hong_kong/pedestrians/hillside_escalator/index.html',
 }
 for name,url in refs.items():
  path=HERE/'pedestrian-source'/name;meta=path.with_name(path.name+'.request.json')
  if not path.exists():raw,info=shared.request(url,json_expected=False);shared.atomic(path,raw);shared.save_json(meta,info)
 features=json.loads(gzip.decompress((HERE/'pedestrian-network.json.gz').read_bytes()))['features']
 ids=sorted({f['attributes']['AccessTimeID'] for f in features if f['attributes'].get('AccessTimeID') is not None})
 result={}
 for layer,name in [(1005,'AccessTime'),(1006,'AccessTimeDetails')]:
  metadata=cached(name+'-layer.json',BASE+'/'+str(layer),{'f':'json'});print(name,[f['name'] for f in metadata['fields']],flush=True)
  rows=[]
  for i in range(0,len(ids),50):
   where='AccessTimeID IN ('+','.join(map(str,ids[i:i+50]))+')'
   data=cached(name+f'-{i//50:03d}.json',BASE+f'/{layer}/query',{'f':'json','where':where,'outFields':'*','returnGeometry':'false','orderByFields':'OBJECTID'});assert not data.get('exceededTransferLimit');rows.extend(f['attributes'] for f in data['features'])
  result[name]=rows
 out={'source':BASE,'accessTimeIdsRequested':ids,'tables':result,'note':'Only records referenced by the retained Central network. Null schedule links are kept as null, not inferred as a guarantee of 24-hour access.'}
 shared.save_json(HERE/'pedestrian-access.json',out);print({k:len(v) for k,v in result.items()})
if __name__=='__main__':main()
