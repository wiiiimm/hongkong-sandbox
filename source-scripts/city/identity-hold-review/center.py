"""Check OSM decorative components against the already installed native Center model."""
import pathlib,json,sys,numpy as np
from shapely.geometry import Polygon
from shapely import union_all
ROOT=pathlib.Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
p=ROOT/'source-scripts/city/central-completion/staged/11-SW-8D/manifest.json';m=json.loads(p.read_bytes());s=next(s for s in m['models']if s['id']=='B339821618801063C0');b=bake(s,p.parent);tri=np.array(b['position']).reshape(-1,3,3);f=[Polygon(t[:,[0,2]])for t in tri];projection=union_all([x for x in f if x.area>1e-8]);tile=json.loads((ROOT/'3d-viewer/city/data/tiles/-1_0.json').read_bytes());rows=[]
for b in tile['buildings']:
 if b['uid'] not in ['way/1323732349:0','way/1323732350:0','way/1323732351:0','way/1323732352:0','way/1323732360:0','way/1323732361:0','way/1323732362:0','way/1323732363:0']:continue
 f=Polygon(b['rings'][0],b['rings'][1:]);rows.append({'uid':b['uid'],'sourcePart':b['part'],'sourceParent':b['parent'],'sourceMaterial':b['material'],'minimum':b['minimum'],'height':b['height'],'area':f.area,'nativeModelProjectionCoverage':projection.intersection(f).area/f.area,'footprint':b['rings']})
report={'govUid':'landsd/67579:0','nativeModelId':s['id'],'sourceManifest':str(p.relative_to(ROOT)),'sourceHashes':s['sourceHashes'],'rows':rows,'decision':'Eight OSM building:part glass components share the known parent The Center. They are not eight independent missing government buildings. They remain source-specific unmatched components; no fabricated government identity and no automatic suppression.','dbWrites':0};(ROOT/'docs/astra-city/identity-hold-review/center.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['uid'],round(r['nativeModelProjectionCoverage'],4))for r in rows])
