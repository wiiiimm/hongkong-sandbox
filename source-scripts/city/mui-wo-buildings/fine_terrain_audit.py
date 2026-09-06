"""Independently audit source building elevations against the root's finer DTM patch.
Only constructs triangles in each building's bounds, never a territory-wide index.
"""
import collections,importlib.util,json,math
from pathlib import Path
from shapely.geometry import Polygon
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('muiwo',HERE/'build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DemSampler(m.Terrain):
 def __init__(self,data,path=None):
  self.path=path;self.dem=data;self.g=data['meta']['georef'];self.w=data['w']
 def extrema(self,p):
  g=self.g;x0,z0,x1,z1=p.bounds
  c0,c1=sorted([(x0+m.ORIGIN[0]-g['bE'])/g['aE'],(x1+m.ORIGIN[0]-g['bE'])/g['aE']]);r0,r1=sorted([(m.ORIGIN[1]-z0-g['bN'])/g['aN'],(m.ORIGIN[1]-z1-g['bN'])/g['aN']])
  values=[]
  for r in range(max(0,math.floor(r0)),min(self.dem['h']-1,math.ceil(r1))):
   for c in range(max(0,math.floor(c0)),min(self.w-1,math.ceil(c1))):
    points=[(g['aE']*cc+g['bE']-m.ORIGIN[0],m.ORIGIN[1]-(g['aN']*rr+g['bN'])) for cc,rr in [(c,r),(c+1,r),(c,r+1),(c+1,r+1)]]
    for triangle in [Polygon([points[0],points[1],points[2]]),Polygon([points[1],points[3],points[2]])]:
     for clipped in m.polys(triangle.intersection(p)):
      values.extend(self.ground(x,z) for ring in [clipped.exterior,*clipped.interiors] for x,z in ring.coords)
  if not values:raise ValueError('Footprint lies outside finer DTM patch')
  return dict(min=round(min(values),3),max=round(max(values),3),centre=round(self.ground(p.centroid.x,p.centroid.y),3),method=f'Exact extrema at footprint/{abs(g["aE"]):g} m terrain triangle intersections')
class FineTerrain(DemSampler):
 def __init__(self,path):super().__init__(m.read(path),path)

def main():
 terrain=FineTerrain(m.ROOT/'3d-viewer/city/data/terrain-mui-wo.json');staged=m.read(m.OUT)['buildings'];rows=[];counts=collections.Counter();clusters=collections.defaultdict(collections.Counter)
 for b in staged:
  p=Polygon(b['rings'][0],b['rings'][1:]);t=terrain.extrema(p);new=m.render_elevations(b['sourceAttributes'],t);top=new['renderTopHeight'];base=new['base'];wholly=top<t['min']-.1;partly=top<t['max']-.1
  row=dict(uid=b['uid'],objectId=b['objectId'],structureType=b['structureType'],heightSource=b['heightSource'],locality=b['locality'],sourceBaseHeight=b['baseHeightHKPD'],sourceTopHeight=b['topHeightHKPD'],coarseTerrain=b['terrain'],fineTerrain=t,fineRenderBase=base,fineRenderTop=top,roofMinusMin=round(top-t['min'],3),roofMinusMax=round(top-t['max'],3),baseMinusMin=round(base-t['min'],3),baseMinusMax=round(base-t['max'],3),roofWhollyBelowTerrain=wholly,roofPartlyBelowTerrain=partly,baseWhollyAboveTerrain=base>t['max']+.5)
  rows.append(row);counts['all']+=1;counts['roofWhollyBelowTerrain']+=wholly;counts['roofPartlyBelowTerrain']+=partly;counts['baseWhollyAboveTerrain']+=row['baseWhollyAboveTerrain']
  if b['heightSource']=='landsd':
   counts['recordedHeights']+=1;counts['recordedRoofWhollyBelowTerrain']+=wholly;counts['recordedRoofPartlyBelowTerrain']+=partly;counts['recordedBaseWhollyAboveTerrain']+=row['baseWhollyAboveTerrain']
  clusters[b['locality']['name']]['all']+=1;clusters[b['locality']['name']]['whollyBelow']+=wholly;clusters[b['locality']['name']]['partlyBelow']+=partly
 output=dict(terrain=m.fingerprint(terrain.path),counts=dict(counts),policy='Recorded source elevations unchanged. For missing source elevations only, recompute explicitly estimated render base from this fine terrain. Roof conflicts use 0.1 m tolerance; floating bases use 0.5 m tolerance.',clusters={k:dict(v) for k,v in sorted(clusters.items())},buildings=rows)
 m.dump(m.DOC/'fine-terrain-audit.json',output,True);print(json.dumps(output['counts'],indent=2))
if __name__=='__main__':main()
