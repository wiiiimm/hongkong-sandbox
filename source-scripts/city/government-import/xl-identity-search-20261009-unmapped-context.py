"""Fresh provider coordinate-cell context search for four unmapped XL originals.
Nearby objects are research leads, never inferred target identity.
"""
import json,sys
from pathlib import Path
from run import ROOT,HERE,read,save
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request,BASE
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
def main():
 assert not (DOC/'unmapped-context.json.gz').exists()
 rows=[r for r in read(DOC/'live-georef-research.json.gz')['rows'] if r['uid'] is None];assert len(rows)==4
 out=[]
 for row in rows:
  geo=row['geoRefNo'];x=800000+int(geo[:5]);y=800000+int(geo[5:]);geometry={'xmin':x-60,'ymin':y-60,'xmax':x+61,'ymax':y+61,'spatialReference':{'wkid':2326}}
  params={'f':'json','where':'1=1','geometry':json.dumps(geometry,separators=(',',':')),'geometryType':'esriGeometryEnvelope','inSR':'2326','spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'false','resultRecordCount':'1000','orderByFields':'OBJECTID'}
  raw,receipt=request(BASE+'/0/query',params);data=json.loads(raw);assert not data.get('exceededTransferLimit')
  name='unmapped-'+geo;(DOC/(name+'.json')).write_bytes(raw);save(DOC/(name+'.request.json'),receipt)
  item={'uid':None,'modelId':row['modelId'],'sourceKey':row['sourceKey'],'sourceSHA256':row['sourceSHA256'],'officialFeatureCount':len(data['features']),'nearbyFeatures':[f['attributes'] for f in data['features']],'identityAccepted':False,'installationApproved':False,'qualification':'60m coordinate-cell neighbourhood query. Proximity/name/shape cannot reassign model UID or establish original component coverage.'};out.append(item)
  print(json.dumps({'modelId':row['modelId'],'nearby':[(f['attributes']['BuildingCSUID'],f['attributes']['BuildingNameEN'],f['attributes']['BuildingBlockType']) for f in data['features']]},ensure_ascii=False),flush=True)
 save(DOC/'unmapped-context.json.gz',{'rows':out})
if __name__=='__main__':main()
