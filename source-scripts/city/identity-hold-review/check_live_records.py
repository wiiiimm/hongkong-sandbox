"""Bounded read-only source refresh; record response instead of changing inventory."""
import json,pathlib,urllib.request,urllib.parse,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3];DOC=ROOT/'docs/astra-city/identity-hold-review';audit=json.loads((DOC/'audit.json').read_bytes());ids=[r['uid'].split('/')[1].split(':')[0]for r in audit['rows']]
base='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
query=urllib.parse.urlencode({'f':'json','objectIds':','.join(ids),'outFields':'OBJECTID,BuildingCSUID,GeoRefNo,BuildingID,BuildingBlockType,BaseHeight,TopHeight','returnGeometry':'true','outSR':'2326','orderByFields':'OBJECTID'})
url=base+'?'+query
with urllib.request.urlopen(url,timeout=60)as response:raw=response.read(2000001)
assert len(raw)<=2000000;data=json.loads(raw);assert not data.get('error');assert not data.get('exceededTransferLimit');assert len(data['features'])==len(ids)
(DOC/'live-footprints.json').write_bytes(raw);(DOC/'live-footprints-provenance.json').write_text(json.dumps({'url':url,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'records':len(data['features']),'published':False},indent=2)+'\n');print('Fetched',len(data['features']),'records',len(raw),'bytes')
