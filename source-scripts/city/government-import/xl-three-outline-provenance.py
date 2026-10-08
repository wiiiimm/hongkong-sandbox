"""Compare four archived original outlines with current official true curves.

Diagnostic only: unchanged viewer/model geometry and strict identity tolerances.
"""
import importlib.util,json,sys
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape,Polygon
from shapely.ops import transform
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-three-outline-provenance-20261008'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();sys.path.insert(0,str(HERE.parent/'landsd-territory'));source=module('outline_archive',HERE.parent/'landsd-territory/retain.py');manifest=read(HERE.parent/'landsd-territory/manifest.json');archive=ROOT/manifest['snapshot']['file'];assert digest(archive.read_bytes())==manifest['snapshot']['compressedSHA256']
 official=read(ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/official-context.json');wanted={r['csuid']:r for r in official['rows'] if r['uid'] in {'landsd/313033:0','landsd/195849:0','landsd/258470:0','landsd/241723:0'}};assert len(wanted)==4
 features={}
 for f in source.iter_features(archive):
  csuid=f['properties']['BuildingCSUID']
  if csuid in wanted:assert csuid not in features;features[csuid]=f
 assert set(features)==set(wanted);save(DOC/'archive-features.json',{'features':list(features.values()),'sourceArchiveSHA256':manifest['snapshot']['compressedSHA256']})
 raw,receipt=source.request(source.BASE+'/0/query',{'f':'json','where':'BuildingCSUID IN ('+','.join("'"+s+"'" for s in sorted(wanted))+')','outFields':'*','returnGeometry':'true','outSR':'2326','returnTrueCurves':'true'})
 (DOC/'official-true-curves.json').write_bytes(raw);save(DOC/'request.json',receipt);current=json.loads(raw);assert len(current['features'])==4 and not current.get('exceededTransferLimit')
 project=Transformer.from_crs(4326,2326,always_xy=True);rows=[]
 for csuid,f in features.items():
  frozen=wanted[csuid];native=transform(project.transform,shape(f['geometry']));shifted=transform(lambda x,y:(x-834500,816500-y),native);original=Polygon(frozen['officialRings'][0],frozen['officialRings'][1:]);true=next(r for r in current['features'] if r['attributes']['BuildingCSUID']==csuid)
  # Current viewer is fetched directly from the pinned current source tiles.
  matches=[b for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles'] for b in read(ROOT/'3d-viewer'/tile['url'])['buildings'] if b['uid']==frozen['uid']];assert len(matches)==1;b=matches[0];viewer=Polygon(b['rings'][0],b['rings'][1:]);g=true['geometry']
  row={'uid':frozen['uid'],'csuid':csuid,'archiveObjectId':f['properties']['OBJECTID'],'currentObjectId':true['attributes']['OBJECTID'],'archiveToViewerHausdorffM':shifted.hausdorff_distance(viewer),'archiveToCurrentDensifiedHausdorffM':shifted.hausdorff_distance(original),'archiveVertices':sum(len(r) for r in f['geometry']['coordinates']),'currentDensifiedVertices':sum(map(len,frozen['officialRings'])),'currentGeometryKeys':sorted(g),'currentCurveSegments':[s for ring in g.get('curveRings',[]) for s in ring if isinstance(s,dict)],'publication':False,'identityAccepted':False};rows.append(row);print(json.dumps(row)[:2500],flush=True)
 save(DOC/'diagnostic.json',{'rows':rows,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'qualification':'Archived original coordinates and current true curves only. Explains numerical/representation mismatch without changing any source geometry, tolerance or acceptance.'})
if __name__=='__main__':main()
