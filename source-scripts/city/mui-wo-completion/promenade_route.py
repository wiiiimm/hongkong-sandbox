"""Derive an explicit walking line inside the existing public promenade source deck.
The former OSM centreline cuts through its source railing. Source geometry stays intact.
"""
import gzip,json,pathlib,math
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
def main():
 data=json.loads(gzip.decompress((HERE/'infrastructure-models.json.gz').read_bytes()));model=next(m for m in data['models'] if m['id'].endswith('/I178711420803063C0'));tri=np.array(model['modelGeometry']['position']).reshape(-1,3,3);floor=unary_union([Polygon(tri[i][:,[0,2]]) for i in model['walkTriangleIndices']]);safe=floor.buffer(-.7)
 route=json.loads((DOC/'routes-staged.json').read_text());leg=route['legs'][0];start_index=leg['nodeIds'].index(6598342309);street=leg['centreline'][start_index];target=leg['centreline'][-1];line=[]
 openings=json.loads((HERE/'opening-scan.json').read_text());opening=min(openings,key=lambda r:math.dist(street,r['outside']));start=opening['inside'][0]
 for x in np.linspace(start,target[0],int(np.ceil(abs(start-target[0])/1.5))+1):
  g=safe.intersection(LineString([(x,2200),(x,2400)]));parts=list(g.geoms) if hasattr(g,'geoms') else [g];parts=[p for p in parts if p.geom_type=='LineString' and p.length>1e-6]
  if not parts:raise ValueError('Source floor corridor gap at '+str(x))
  q=max(parts,key=lambda p:p.length).interpolate(.5,normalized=True);line.append([q.x,q.y])
 outside=opening['outside'];line=[opening['inside']]+line
 adjusted=leg['centreline'][:start_index+1]+[outside]+line+[target]
 evidence={'sourceModelId':model['id'],'sourceHashes':model['modelGeometry']['sourceHashes'],'sourceFloorFaces':model['walkTriangleIndices'],'publicAccessSource':model['publicAccessSource'],'sourceStreetNode':6598342309,'streetPosition':street,'outsideOpening':outside,'sourceDeckEntry':line[0],'sourceDeckLine':line,'target':target,'walkCentreline':adjusted,'method':'After the retained public street node, a short explicitly estimated connector approaches the source deck through an existing source-railing opening found by exact source collision tests. The walking line follows midpoints of vertical sections of the exact selected public floor polygon, inset0.7m; source mesh and former OSM centreline remain unchanged. This line is a derived simulation route, not a surveyed path centreline.','connectorDistanceM':float(np.linalg.norm(np.array(street)-np.array(outside))+np.linalg.norm(np.array(outside)-np.array(line[0]))),'sourceOpening':opening,'sourceGeometryChanged':False,'continuousWalkVerified':False}
 (HERE/'promenade-route.json').write_text(json.dumps(evidence,indent=2)+'\n');print('Promenade derived line',len(line),'connector',evidence['connectorDistanceM'])
if __name__=='__main__':main()
