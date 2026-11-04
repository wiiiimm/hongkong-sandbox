"""Fresh primary source-component search inside PopCorn 1's largest authored gap."""
import sys,json
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import BASE,request
from shapely.geometry import shape,Polygon
DOC=ROOT/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009';r=read(DOC/'295538-0/opening-diagnostics.json.gz');hole=shape(r['sourceAuthoredOpeningDiagnostics'][0]['geometry']);x0,z0,x1,z1=hole.bounds
geo={'xmin':x0+834500,'ymin':816500-z1,'xmax':x1+834500,'ymax':816500-z0,'spatialReference':{'wkid':2326}}
params={'f':'json','where':'1=1','geometry':json.dumps(geo),'geometryType':'esriGeometryEnvelope','inSR':'2326','spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'false','resultRecordCount':'1000'};raw,rec=request(BASE+'/0/query',params);j=json.loads(raw);assert not j.get('exceededTransferLimit');(DOC/'popcorn-gap-official-buildings.json').write_bytes(raw);save(DOC/'popcorn-gap-official-buildings.request.json',rec)
rows=[]
for f in j['features']:
 polys=[Polygon([(x-834500,816500-y) for x,y,*_ in ring]) for ring in f['geometry']['rings']];p=max(polys,key=lambda p:p.area);inter=p.intersection(hole).area
 if inter>0:rows.append({'attributes':f['attributes'],'holeIntersectionM2':inter,'holeCoverageFraction':inter/hole.area,'officialRings':f['geometry']['rings']})
rows.sort(key=lambda r:-r['holeIntersectionM2']);save(DOC/'popcorn-gap-official-building-candidates.json.gz',{'sourceDiagnosticSHA256':digest((DOC/'295538-0/opening-diagnostics.json.gz').read_bytes()),'primaryRequest':rec,'rows':rows,'identityAccepted':False,'qualification':'Current provider footprint intersections identify exact companion-source research candidates, not component ownership or installation acceptance.'});print(json.dumps([{k:v for k,v in row.items() if k!='officialRings'} for row in rows],ensure_ascii=False),flush=True)
