"""Port the stadium's original government geometry with existing source checks."""
import gzip,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import scan
sys.path.insert(0,str(HERE.parent/'citywide-native'));from download import acquire
from convert import convert_sheet
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from retain import iter_features
from pyproj import Transformer
prior=json.loads((HERE/'directory.json').read_text())
row,_=scan({'SHEETNO':prior['sheet'],'Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},HERE/'local/directory')
assert row['etag']==prior['etag'] and row['directorySHA256']==prior['directorySHA256'],'Government source revision changed; retain a new plan before proceeding'
row['models']=[m for m in row['models'] if m['modelId']=='B383792035701063C1'];assert len(row['models'])==1
buildings=json.loads((ROOT/'3d-viewer/city/data/tiles/1_-2.json').read_text())['buildings'];b=next(b for b in buildings if b['uid']=='landsd/318723:0')
projection=Transformer.from_crs(4326,2326,always_xy=True);features=[]
for f in iter_features(HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz'):
 a=f['properties']
 if a.get('OBJECTID')!=b['objectId']:continue
 assert a['BuildingCSUID']==b['buildingCSUID'];g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
 features.append({'attributes':a,'geometry':{'rings':[[list(projection.transform(*p)) for p in r] for poly in polys for r in poly]},'viewerUids':[{k:b[k] for k in ['uid','rings','base','height']}]})
assert len(features)==1
selection=HERE/'official.json.gz';selection.write_bytes(gzip.compress(json.dumps({'features':features}).encode(),mtime=0))
download=acquire(row,HERE/'local/directory/zip-directory.bin',HERE/'local/original')
result=convert_sheet(HERE/'local/original/11-NE-16B.zip',download,selection,HERE/'candidates')
(HERE/'conversion-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['sourceModels','candidateModels','compressedBytes','outcomes']}))
