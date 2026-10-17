"""Determine whether missing source boundaries are separately recorded upper towers."""
import sys,json,shapely
from shapely.geometry import shape,Polygon,mapping
from run import ROOT,HERE,read,save
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import BASE,request
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-op-complete-pair-20261009'
missing=shape(read(DOC/'missing-target-and-source-excess.geojson')['features'][0]['geometry']);metrics=read(DOC/'complete-original-pair-current-measures.json');wanted=set(metrics['allForeignFormsRetained']);forms={}
for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
 for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
  if b['uid'] in wanted:forms[b['uid']]=b
rows=[]
for uid,b in forms.items():
 poly=Polygon(b['rings'][0],b['rings'][1:]);covered=missing.intersection(poly)
 if covered.area<.01:continue
 rows.append({'uid':uid,'name':b.get('name',''),'buildingCSUID':b['buildingCSUID'],'missingTargetCoveredM2':covered.area,'originalCurrentForm':b,'coveredMissingGeometry':mapping(covered)})
rows.sort(key=lambda r:-r['missingTargetCoveredM2']);save(DOC/'missing-area-separate-upper-form-candidates.json.gz',{'rows':rows,'identityAccepted':False,'qualification':'Current upper form intersections identify possible complete original source-family candidates, not permission to remove their footprint from coverage or suppress forms.'})
for r in rows:
 csuid=r['buildingCSUID'];params={'f':'json','where':"BuildingCSUID='"+csuid+"'",'outFields':'*','returnGeometry':'false','resultRecordCount':'1000'};raw,rec=request(BASE+'/1002/query',params);(DOC/('upper-op-relations-'+csuid+'.json')).write_bytes(raw);save(DOC/('upper-op-relations-'+csuid+'.request.json'),rec)
 relation=json.loads(raw);ids=[f['attributes']['BuildingStructureID'] for f in relation['features']]
 if ids:
  params={'f':'json','where':'BuildingStructureID IN('+','.join(map(str,ids))+')','outFields':'*','returnGeometry':'false','resultRecordCount':'1000'};raw,rec=request(BASE+'/1003/query',params);(DOC/('upper-op-structures-'+csuid+'.json')).write_bytes(raw);save(DOC/('upper-op-structures-'+csuid+'.request.json'),rec)
 print({k:r[k] for k in ['uid','name','missingTargetCoveredM2']},flush=True)
