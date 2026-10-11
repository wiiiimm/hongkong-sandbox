"""Audit published Tai O hydro against its retained sources and previous terrain."""
import gzip,hashlib,json,math,subprocess
import numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from hydro_build import HERE,ROOT,DOC,polys,ib5000
from hydro_prepare import load
from hydro_terrain import height
OUT=ROOT/'3d-viewer/city/data'
def main():
 published=json.loads((OUT/'terrain.json').read_text());hydro=published['hydro'];water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);old=json.loads(subprocess.check_output(['git','show','7757ee6:3d-viewer/city/data/terrain.json'],cwd=ROOT));assert {k:v for k,v in published.items() if k!='hydro'}==old
 patch=json.loads((OUT/'terrain-tai-o.json').read_text());assert patch==json.loads(subprocess.check_output(['git','show','7757ee6:3d-viewer/city/data/terrain-tai-o.json'],cwd=ROOT))
 overlap=0.;maxoverlap=0.;n=0;maxheight=0.
 for grid in hydro['terrainCuts']:
  d=patch if grid['georef']['aE']==5 else published
  for c in grid['cells']:
   for i in range(0,len(c['land']),9):
    a=c['land'][i:i+9];t=Polygon([(a[j],a[j+2]) for j in [0,3,6]]);o=t.intersection(water).area;overlap+=o;maxoverlap=max(maxoverlap,o);n+=1
    for j in [0,3,6]:maxheight=max(maxheight,abs(a[j+1]-height(d,a[j],a[j+2])))
 assert maxoverlap<.001,(maxoverlap,overlap);assert maxheight<.0001,maxheight
 footprints=json.loads(gzip.decompress((HERE.parent/'tai-o-models/building-selection.json.gz').read_bytes()))['buildings'];affected=[]
 for b in footprints:
  p=Polygon(b['rings'][0],b['rings'][1:]);a=water.intersection(p).area
  if a>1:affected.append({'uid':b['uid'],'name':b.get('name'),'mappedWaterAreaM2':round(a,3),'footprintShare':round(a/p.area,4)})
 clip=box(*hydro['bounds']);land=clip.difference(water);dist=[]
 for row,g in load():
  if row['layer']!='Shoreline' or not g.intersects(clip):continue
  g=g.intersection(clip)
  for l in g.geoms if g.geom_type=='MultiLineString' else [g]:
   if l.geom_type!='LineString':continue
   for d in np.arange(0,l.length,5):dist.append(water.boundary.distance(l.interpolate(d)))
 report={'baseline':'7757ee6','entireCoarseTerrainWithoutHydroUnchanged':True,'taiOPatchUnchanged':True,'rawTerrainSha256':hashlib.sha256(json.dumps(old['elev']).encode()).hexdigest(),'replacementTriangles':n,'maximumTriangleWaterOverlapM2':maxoverlap,'totalRoundingOverlapM2':overlap,'maximumReplacementHeightErrorM':maxheight,'mappedWaterIntersectingFootprintsOver1M2':len(affected),'sourceFootprints':affected,'shorelineCrossCheck':{'source':'Retained iB1000 HWM/SWA segments, sampled every5m against iB5000 water boundary','samples':len(dist),'medianDistanceM':float(np.median(dist)),'p95DistanceM':float(np.percentile(dist,95)),'within1M':sum(d<1 for d in dist),'limitation':'Two source products have cartographic differences and building gaps; all original boundaries remain available, not silently snapped.'}}
 (DOC/'hydro-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sourceFootprints'},indent=2))
 # Source-derived comparison; no satellite tracing or invented buildings.
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 for name,bounds in [('overview',hydro['bounds']),('village',[-30900,3200,-30050,3850])]:
  fig,ax=plt.subplots(figsize=(14,10));ax.set_facecolor('#a9d9e7')
  for p in polys(land):
   ax.fill(*p.exterior.xy,color='#dbe2c9')
   for ring in p.interiors:ax.fill(*ring.xy,color='#a9d9e7')
  for b in footprints:
   p=Polygon(b['rings'][0],b['rings'][1:]);ax.fill(*p.exterior.xy,color='#6d7283',alpha=.65,linewidth=.2,edgecolor='white')
  for row,g in load():
   if row['layer']!='Shoreline':continue
   for l in g.geoms if g.geom_type=='MultiLineString' else [g]:
    if l.geom_type=='LineString':ax.plot(*l.xy,color='#236781',lw=.8)
  ax.set_aspect('equal');ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[3],bounds[1]);ax.set_xlabel('City-local east (m)');ax.set_ylabel('City-local south (m)');ax.set_title('Tai O — current government land/water geometry and retained building footprints')
  fig.text(.07,.012,'Lands Department / HKSAR Government · iB5000 9-SW-C/D closed land extent; iB1000 shoreline cross-check\nGrey: source footprints; blue: mapped tidal water. No surveyed bathymetry. Source index revisions and per-feature dates retained.',fontsize=9);fig.tight_layout(rect=(0,.05,1,1));fig.savefig(DOC/f'hydro-source-{name}-1960x1400.png',dpi=140);plt.close(fig)
if __name__=='__main__':main()
