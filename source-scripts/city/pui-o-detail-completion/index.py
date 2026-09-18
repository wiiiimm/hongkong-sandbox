"""Refresh bounded official index with object-ID completeness verification."""
import datetime,hashlib,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
for name,dataset in [('index','landsd_rcd_1742809441342_98380'),('individual-index','landsd_rcd_1671676915450_88604')]:
 base=f'https://portal.csdi.gov.hk/server/rest/services/common/{dataset}/FeatureServer/0/query';args={'f':'json','where':'1=1','geometry':'814965,810765,816535,812035','geometryType':'esriGeometryEnvelope','inSR':2326,'outSR':2326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','returnIdsOnly':'true'}
 ids_url=base+'?'+urllib.parse.urlencode(args);ids=json.load(urllib.request.urlopen(ids_url));assert 'error' not in ids;object_ids=ids.get('objectIds') or [];assert object_ids
 args.pop('returnIdsOnly');args['objectIds']=','.join(map(str,object_ids));url=base+'?'+urllib.parse.urlencode(args);raw=urllib.request.urlopen(url).read();data=json.loads(raw);assert not data.get('exceededTransferLimit') and {f['attributes']['OBJECTID'] for f in data['features']}==set(object_ids)
 (HERE/f'{name}.json').write_bytes(raw);(HERE/f'{name}-provenance.json').write_text(json.dumps({'url':url,'idsUrl':ids_url,'ids':ids,'sha256':hashlib.sha256(raw).hexdigest(),'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completeObjectIdSet':True},indent=2)+'\n');print(name,len(object_ids))
