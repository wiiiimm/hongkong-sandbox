"""Independent cross-package coincident footprint audit."""
import json,pathlib
from shapely.geometry import Polygon
from shapely.strtree import STRtree
ROOT=pathlib.Path(__file__).resolve().parents[4]
rows=[];polygons=[]
for path in sorted((ROOT/'3d-viewer/city/data/regional').glob('*.json')):
 for surface in json.loads(path.read_text())['surfaces']:
  rows.append((path.stem,surface));polygons.append(Polygon(surface['rings'][0],surface['rings'][1:]))
tree=STRtree(polygons);duplicates=[]
for i,p in enumerate(polygons):
 for j in tree.query(p):
  if j<=i or rows[j][0]==rows[i][0]:continue
  overlap=p.intersection(polygons[j]).area
  if overlap>max(1,min(p.area,polygons[j].area)*.95):duplicates.append({'first':rows[i][1]['id'],'firstPackage':rows[i][0],'second':rows[j][1]['id'],'secondPackage':rows[j][0],'overlapArea':overlap})
result={'surfaces':len(rows),'criterion':'Cross-package polygon overlap over 95% of the smaller footprint and over 1 square metre, regardless of source ID','duplicateFootprints':duplicates}
pathlib.Path(__file__).with_name('seams.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
