"""HKS-171 availability only: retained cache first, then bounded official index queries."""
import datetime,hashlib,json,pathlib,urllib.parse,urllib.request
from shapely.geometry import Polygon,box
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/south-lantau-audit'
AREAS={'cheung-sha':{'name':'Cheung Sha','boundsHK1980':[812000,810050,814650,811200]},'tong-fuk':{'name':'Tong Fuk','boundsHK1980':[810650,809550,811650,810450]},'shui-hau':{'name':'Shui Hau','boundsHK1980':[808700,808750,809950,810050]}}
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query'
def audit():
 caches={}
 for file in (ROOT/'source-scripts/city').glob('**/sources/*/download.json'):
  d=json.loads(file.read_text());caches.setdefault(d.get('sheet',file.parent.name),[]).append({'metadata':str(file.relative_to(ROOT)),'revision':d.get('revisionDate'),'memberPrefixes':d.get('memberPrefixes'),'originalEntryCount':len(d.get('entries',[])),'retainedArchive':(file.parent/(file.parent.name+'.zip')).exists(),'entryNames':[e['name'] for e in d.get('entries',[])]})
 manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text());rows=[];all_sheets=set()
 for key,area in AREAS.items():
  target=HERE/(key+'-index.json');params={'f':'json','geometry':','.join(map(str,area['boundsHK1980'])),'geometryType':'esriGeometryEnvelope','inSR':'2326','spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','outSR':'2326'};url=BASE+'?'+urllib.parse.urlencode(params)
  if not target.exists():
   with urllib.request.urlopen(url,timeout=45) as r:raw=r.read()
   data=json.loads(raw);assert 'features' in data and not data.get('exceededTransferLimit');target.write_bytes(raw);(HERE/(key+'-index-request.txt')).write_text(url+'\n');(HERE/(key+'-index-source.json')).write_text(json.dumps({'url':url,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
  data=json.loads(target.read_text());scope=box(area['boundsHK1980'][0]-834500,816500-area['boundsHK1980'][3],area['boundsHK1980'][2]-834500,816500-area['boundsHK1980'][1]);sheets=[]
  for f in data['features']:
   a=f['attributes'];sheet=a['SHEETNO'];all_sheets.add(sheet);sheets.append({'sheet':sheet,'revision':datetime.datetime.fromtimestamp(a['REVISIONDATE']/1000,datetime.timezone.utc).isoformat(),'officialDownloadUrl':a.get('Format_glTF'),'retainedCaches':caches.get(sheet,[])})
  forms=[]
  for t in manifest['tiles']:
   if not box(*t['bounds']).intersects(scope):continue
   for b in json.loads((ROOT/'3d-viewer'/t['url']).read_text())['buildings']:
    p=Polygon(b['rings'][0],b['rings'][1:]);p=p if p.is_valid else p.buffer(0)
    if p.intersection(scope).area>.01:forms.append(b)
  rows.append({'id':key,**area,'sectionId':'10.8','scopeNote':'Preliminary bounded source-availability study box around the named village/coast; not an official locality boundary or a completeness acceptance polygon. Excludes Pui O source extent.','sourceSheets':sheets,'counts':{'sheets':len(sheets),'alreadyRetainedSheets':sum(bool(s['retainedCaches']) for s in sheets),'renderedForms':len(forms),'officialForms':sum(b['id'].startswith('landsd/') for b in forms),'existingDetailedModelForms':sum(bool(b.get('modelGeometry')) for b in forms),'sourceHeightForms':sum(b.get('heightSource')=='landsd' for b in forms)},'structureTypes':{v:sum(b.get('structureType',b.get('kind','unknown'))==v for b in forms) for v in sorted({b.get('structureType',b.get('kind','unknown')) for b in forms})}})
 report={'issue':'HKS-171','sectionId':'10.8','status':'availability-audit-only','areas':rows,'uniqueOfficialSheets':sorted(all_sheets),'cityManifestSha256':hashlib.sha256((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()).hexdigest(),'newModelArchivesDownloaded':0,'livePublished':False,'limits':['Official index presence establishes an advertised source sheet, not that every local form or infrastructure detail exists inside its archive.','Existing source-model caches were inspected before querying metadata. No Pui O implementation files were edited.','Current building counts use source footprint intersection with preliminary study rectangles, not official village boundaries.','Detailed original glTF/TIN/infrastructure inventory, water semantics and safe public route checks remain subsequent implementation work.']}
 (DOC/'availability.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'areas':[{a['id']:a['counts']} for a in rows],'uniqueSheets':len(all_sheets)},indent=2));return report
if __name__=='__main__':audit()
