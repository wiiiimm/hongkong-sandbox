"""Shared publisher for the existing city tile, catalogue and overview formats."""
import collections,json,math
from build_city import ROOT,OUT

def write(path,content):
 temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(content);temporary.replace(path)
def dump(path,value):write(path,json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
def publish(tiles,manifest):
 size=manifest['tileSize'];metadata=[];features=[]
 for key,tile in sorted(tiles.items()):
  x,z=map(int,key.split('_'));bounds=[x*size,z*size,(x+1)*size,(z+1)*size]
  for b in tile['buildings']:
   for px,pz in b['rings'][0]:bounds=[min(bounds[0],px),min(bounds[1],pz),max(bounds[2],px),max(bounds[3],pz)]
   # Detailed roofs/eaves can extend beyond their mapped footprint.
   model_bounds=b.get('modelGeometry',{}).get('worldBounds')
   if model_bounds is not None:
    assert len(model_bounds)==2 and all(len(point)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in point) for point in model_bounds),b['uid']
    low,high=model_bounds;assert all(low[i]<=high[i] for i in range(3)),b['uid']
    bounds=[min(bounds[0],low[0]),min(bounds[1],low[2]),max(bounds[2],high[0]),max(bounds[3],high[2])]
  tile['bounds']=bounds;content=json.dumps(tile,ensure_ascii=False,separators=(',',':')).encode();path=OUT/'tiles'/f'{key}.json'
  if not path.exists() or path.read_bytes()!=content:write(path,content)
  counts={'buildings':len(tile['buildings']),'roads':len(tile['roads']),'parks':len(tile['parks']),'heights':dict(collections.Counter(b['heightSource'] for b in tile['buildings']))}
  metadata.append({'id':key,'bounds':bounds,'centre':[(x+.5)*size,(z+.5)*size],'url':f'city/data/tiles/{key}.json','bytes':len(content),'counts':counts});features.extend(tile['buildings'])
 fields=('id','uid','tile','name','zh','height','heightSource','levels','base','centre')
 dump(OUT/'catalogue.json',[{k:b[k] for k in fields}|({'parent':b['parent']} if b.get('parent') else {}) for b in features if b['name'] or b['zh']])
 dump(OUT/'overview.json',{k:[b['centre'] for b in t['buildings']] for k,t in tiles.items() if t['buildings']})
 manifest['tiles']=metadata;manifest['counts']={'buildings':len(features),'roads':sum(len(t['roads']) for t in tiles.values()),'parks':sum(len(t['parks']) for t in tiles.values()),'heights':dict(collections.Counter(b['heightSource'] for b in features))}
 manifest['heightEstimateCounts']=dict(collections.Counter(b.get('heightRule','generic') for b in features if b['heightSource']=='estimated'));dump(OUT/'manifest.json',manifest)
 return features
