"""Compare the original GeoJSON representation against fresh official GeoJSON.

Read-only representation diagnosis; existing2mm polygon equality is unchanged.
"""
import importlib.util,json,sys
from pyproj import Transformer
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-three-outline-provenance-20261008';DOC=BASE/'government-xl-four-current-geojson-provenance-20261008'
def main():
 assert not DOC.exists();sys.path.insert(0,str(HERE.parent/'landsd-territory'));spec=importlib.util.spec_from_file_location('geojson_source',HERE.parent/'landsd-territory/source.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
 archived=read(OLD/'archive-features.json')['features'];csuids=[r['properties']['BuildingCSUID'] for r in archived];official=read(BASE/'government-xl-22-complete-group-official-context-v2-20261008/official-context.json')['rows'];uids={r['csuid']:r['uid'] for r in official};wanted={uids[c] for c in csuids};forms={b['uid']:b for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles'] for b in read(ROOT/'3d-viewer'/t['url'])['buildings'] if b['uid'] in wanted};project=Transformer.from_crs(4326,2326,always_xy=True);results=[]
 for sr in ('4326','2326'):
  raw,receipt=source.request(source.BASE+'/0/query',{'f':'geojson','where':'BuildingCSUID IN ('+','.join("'"+s+"'" for s in sorted(csuids))+')','outFields':'*','returnGeometry':'true','outSR':sr,'returnTrueCurves':'false'})
  (DOC/f'current-{sr}.geojson').parent.mkdir(parents=True,exist_ok=True);(DOC/f'current-{sr}.geojson').write_bytes(raw);save(DOC/f'request-{sr}.json',receipt);data=json.loads(raw)
  if 'error' in data:print(sr,data['error'],flush=True);results.append({'sr':sr,'error':data['error']});continue
  assert data['type']=='FeatureCollection' and len(data['features'])==4
  for f in data['features']:
   csuid=f['properties']['BuildingCSUID'];uid=uids[csuid];archive=next(r for r in archived if r['properties']['BuildingCSUID']==csuid);a=transform(project.transform,shape(archive['geometry']));current=transform(project.transform,shape(f['geometry'])) if sr=='4326' else shape(f['geometry']);viewer=Polygon([[(x+834500,816500-y) for x,y in ring] for ring in forms[uid]['rings']][0],[[(x+834500,816500-y) for x,y in ring] for ring in forms[uid]['rings'][1:]]);row={'uid':uid,'csuid':csuid,'sr':sr,'currentToArchiveHausdorffM':current.hausdorff_distance(a),'currentToViewerHausdorffM':current.hausdorff_distance(viewer),'archiveVertices':sum(len(r) for r in archive['geometry']['coordinates']),'currentVertices':sum(len(r) for r in f['geometry']['coordinates']),'currentStatus':f['properties']['Status'],'publication':False,'installationApproved':False};results.append(row);print(json.dumps(row),flush=True)
 save(DOC/'summary.json',{'rows':results,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0})
if __name__=='__main__':main()
