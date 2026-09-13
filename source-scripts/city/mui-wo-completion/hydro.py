"""Stage current Mui Wo shore/tidal rivers through the verified Tai O GML pipeline.
Imports are isolated module instances; the frozen Tai O source files are not modified.
"""
import collections,concurrent.futures,gzip,hashlib,importlib.util,json,pathlib,sys,subprocess
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import make_valid
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion';SHARED=HERE.parent/'tai-o-completion';BOUNDS=[816600,813400,818650,815250]
sys.path.insert(0,str(SHARED))
import hydro_prepare as decode
import hydro_build as coast
spec=importlib.util.spec_from_file_location('muiwo_hydro_fetch',SHARED/'hydro_fetch.py');fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
# These module globals only configure this process's imported decoder/fetch helpers.
fetch.HERE=HERE;decode.HERE=HERE;coast.HERE=HERE;coast.BOUNDS=BOUNDS
fetch.LAYERS=fetch.LAYERS+['Transportation/CartoPedLine']
def index(path,service):
 if not path.exists():subprocess.run(['curl','-fLsS','--get',service,'--data-urlencode','f=json','--data-urlencode','geometry='+','.join(map(str,BOUNDS)),'--data-urlencode','geometryType=esriGeometryEnvelope','--data-urlencode','inSR=2326','--data-urlencode','outSR=2326','--data-urlencode','outFields=*','--data-urlencode','returnGeometry=true','-o',str(path)],check=True)
 return json.loads(path.read_text())
def main():
 (HERE/'hydro-sources').mkdir(exist_ok=True)
 current=index(HERE/'hydro-index.json','https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637223748322_25497/MapServer/0/query')
 index(HERE/'hydro-ib5000-index.json',coast.INDEX)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:sources1000=list(pool.map(fetch.fetch,current['features']))
 sources5000=coast.fetch();rows=decode.load();x0,n0,x1,n1=BOUNDS;clip=box(x0-834500,816500-n1,x1-834500,816500-n0)
 landrows=[(r,g) for r,g in coast.ib5000() if r['layer']=='ContourPoly' and g.intersects(clip)]
 land=unary_union([g for r,g in landrows]).intersection(clip);ocean=clip.difference(land)
 rivers=[(r,g) for r,g in rows if r['layer']=='HydroPolygon' and r['attributes'].get('HYDROPOLYGONTYPE') in ['RIV','CHA','NUL'] and g.intersects(clip)]
 # Publicly documented lower estuaries only. A RIV feature can extend into a
 # non-tidal upland reach, so sea connectivity is not a tidal-limit algorithm.
 # The Wang Tong display starts at the northern edge of the retained bridge
 # source model. That is an explicit rendering study extent, not a tidal limit.
 inventory=json.loads((DOC/'infrastructure-inventory.json').read_text())
 bridge=next(m for m in inventory if m['id']=='I178581445403063C0')
 wang_scope=box(clip.bounds[0],bridge['worldBounds'][0][2],clip.bounds[2],clip.bounds[3])
 connected=[];remaining=[]
 for r,g in rivers:
  if r['id']=='HydroPolygon/1104404556':selected=g.intersection(clip);policy='Complete mapped lower River Silver estuary polygon; recorded 2D banks, illustrative bed only.'
  elif r['id']=='HydroPolygon/1104401625':selected=g.intersection(wang_scope);policy='Wang Tong seaward display extent from the northern bound of source bridge I178581445403063C0; this scope boundary is not a surveyed tidal limit.'
  else:selected=Polygon();policy='Not part of the reviewed lower-estuary display scope.'
  if not selected.is_empty and selected.intersects(ocean):connected.append(({**r,'displayScope':policy,'displayAreaM2':selected.area},selected))
  else:remaining.append((r,g))
 water=unary_union([ocean,*[g for r,g in connected]])
 water=make_valid(water.intersection(clip));out={'schemaVersion':1,'region':'mui-wo','sectionId':'10.6','bounds':list(clip.bounds),'boundsHK1980':BOUNDS,'illustrativeBed':-4,'source':{'provider':'Lands Department / HKSAR Government','dataset':'iB5000 closed ContourPoly land extent; connected iB1000 HydroPolygon surface rivers/channels','derivation':'Bounded sea complement of exact closed land polygons, plus separately reviewed lower-estuary source footprints. No manual bank tracing, gap closure or coordinate snapping. The Wang Tong upstream display boundary is a source-bridge extent, not a surveyed tidal limit.','verticalNote':'The -4m rendered bed is illustrative, not surveyed bathymetry. Raw terrain elevations and all source buildings remain unchanged.','sources':sources5000+sources1000,'landFeatures':[r for r,g in landrows],'riverFeatures':[{k:v for k,v in r.items() if k!='geometry'} for r,g in connected],'currentReference':'https://www.landsd.gov.hk/doc/en/mapping/ehkg/MapPages/GeoPDF/IS12_MuiWo.pdf','riverScope':{'wangTongSourceBridge':'I178581445403063C0','upstreamDisplayZ':bridge['worldBounds'][0][2],'scopeIsTidalLimit':False,'upstreamNote':'Complete original source river polygons remain retained. Upstream river levels and bathymetry are not inferred from cartographic zero-Z values.','contextReference':'https://www.epd.gov.hk/eia/register/report/eiareport/eia_2382016/EIA/pdf/IA14024_EIA_Final_v.4.0.pdf','contextAccess':'Indexed EIA section7.6.4 describes a non-tidal upper reach. Direct PDF returned404 at this retrieval; used only as contextual historical ecology, not current geometry.'}},'water':[]}
 for i,p in enumerate(coast.polys(water)):out['water'].append({'id':f'mui-wo-tidal-water-{i}','rings':[[[round(x,5),round(z,5)] for x,z in ring.coords] for ring in [p.exterior,*p.interiors]],'area':p.area})
 (HERE/'hydro-mui-wo.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
 excluded=[{'id':r['id'],'code':r['attributes'].get('HYDROPOLYGONTYPE'),'areaM2':g.area,'reason':'Outside reviewed lower-estuary rendering scope; retained complete in original GML, no implicit tidal classification'} for r,g in remaining]
 report={'bounds':list(clip.bounds),'landFeatures':len(landrows),'candidateSurfaceRivers':len(rivers),'connectedRivers':len(connected),'excludedRivers':excluded,'waterPolygons':len(out['water']),'vertices':sum(len(r) for p in out['water'] for r in p['rings']),'waterAreaM2':water.area,'sourceArchiveBytes':sum(r['archiveBytes'] for r in sources1000+sources5000),'retainedSourceFiles':sum(len(r['entries']) for r in sources1000+sources5000),'published':False}
 (DOC/'hydro-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
