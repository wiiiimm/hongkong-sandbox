"""Fresh primary-provider identifier/outline search for every current XL identity hold.
Research only: no model/source/review edits and no acceptance or installation credit.
"""
import collections,json,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
sys.path.insert(0,str(HERE.parent/'mui-wo-buildings'))
from build import official_geometry,polys
from shapely.geometry import Polygon
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-current-320-blocker-families-20261009/dispositions.json.gz'
def main():
 assert not DOC.exists(),'Fresh research directory required'
 rows=[r for r in read(INPUT)['rows'] if 'identity-or-component-coverage' in r['reasonFamilies']]
 assert len(rows)==190
 DOC.mkdir(parents=True)
 refs=sorted({r['modelId'][1:11] for r in rows});features=[]
 for i in range(0,len(refs),20):
  batch=refs[i:i+20];params={'f':'json','where':'GeoRefNo IN ('+','.join("'"+v+"'" for v in batch)+')','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'false','resultRecordCount':'1000','orderByFields':'OBJECTID'}
  raw,receipt=request(BASE+'/0/query',params);payload=json.loads(raw)
  assert not payload.get('exceededTransferLimit');assert all(str(f['attributes']['GeoRefNo']) in batch for f in payload['features'])
  (DOC/f'official-georefs-{i//20:02d}.json').write_bytes(raw);save(DOC/f'official-georefs-{i//20:02d}.request.json',receipt)
  features+=payload['features'];print(json.dumps({'batch':i//20,'geoRefs':len(batch),'officialFeatures':len(payload['features'])}),flush=True)
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
 wanted={r['uid'] for r in rows if r['uid']};forms={};bycsuid=collections.defaultdict(list)
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b.get('buildingCSUID','')[:10] in refs:bycsuid[b['buildingCSUID']].append({'building':b,'tile':tile['url'],'tileSHA256':digest(path.read_bytes())})
   if b['uid'] in wanted:forms[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(path.read_bytes())}
 results=[]
 for row in rows:
  geo=row['modelId'][1:11];subtype={'01':'Tower','02':'Podium'}[row['modelId'][11:13]]
  candidates=[]
  for f in features:
   a=f['attributes']
   if str(a['GeoRefNo'])!=geo:continue
   item={'attributes':a,'sourceTypeMatches':a['BuildingBlockType']==subtype,'currentViewerStableCSUIDMatches':[{'uid':v['building']['uid'],'tile':v['tile']} for v in bycsuid[a['BuildingCSUID']]]}
   own=forms.get(row['uid']);item['sourceCurrentExactCSUIDMatches']=bool(own and own['building'].get('buildingCSUID')==a['BuildingCSUID'])
   if own and item['sourceCurrentExactCSUIDMatches']:
    polygon=Polygon(own['building']['rings'][0],own['building']['rings'][1:]);geometry,repaired=official_geometry(f);matches=[p for p in polys(geometry) if p.intersection(polygon).area>0]
    item['officialGeometryRepaired']=repaired;item['matchingPolygonCount']=len(matches)
    if len(matches)==1:
     p=matches[0];item.update(hausdorffDistanceM=float(polygon.hausdorff_distance(p)),symmetricDifferenceM2=float(polygon.symmetric_difference(p).area),sourceViewerAreaM2=float(polygon.area),currentOfficialAreaM2=float(p.area),officialRings=[list(map(list,r.coords)) for r in [p.exterior,*p.interiors]])
   candidates.append(item)
  exact=[c for c in candidates if c['sourceTypeMatches'] and c['sourceCurrentExactCSUIDMatches']]
  state='exact-current-official-identity-found' if len(exact)==1 else ('official-exact-type-but-unmapped' if any(c['sourceTypeMatches'] for c in candidates) else 'no-exact-type-official-feature')
  results.append({k:row[k] for k in ['uid','sourceKey','sourceSHA256','modelId','name','reasons']}|{'geoRefNo':geo,'expectedType':subtype,'state':state,'officialCandidates':candidates,'identityAccepted':False,'installationApproved':False})
 output={'inputSHA256':digest(INPUT.read_bytes()),'manifestSHA256':digest(manifest_path.read_bytes()),'sources':190,'geoRefs':len(refs),'officialFeatures':len(features),'rows':results,'states':dict(collections.Counter(r['state'] for r in results)),'geometryChanges':0,'newlyInstalled':0,'qualification':'Fresh live primary-provider GeoRef/type/stable-CSUID search and exact current outline comparison. Positive identifier matches establish provider identity only, not complete mesh component coverage or physical/runtime acceptance. Current OBJECTIDs are not substituted for retained viewer OBJECTIDs.'}
 save(DOC/'live-georef-research.json.gz',output)
 print(json.dumps({'states':output['states'],'changedOutlinesOver2mm':[{'uid':r['uid'],'name':c['attributes']['BuildingNameEN'],'distanceM':c.get('hausdorffDistanceM')} for r in results for c in r['officialCandidates'] if c.get('hausdorffDistanceM',0)>.002],'unmapped':[r for r in results if r['uid'] is None]},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
