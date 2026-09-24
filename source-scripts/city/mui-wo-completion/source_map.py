"""Source geometry diagnostic; no source imagery tracing."""
import json,pathlib,sys
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import box,LineString
from shapely.ops import unary_union
import hydro
HERE=pathlib.Path(__file__).resolve().parent;DOC=hydro.DOC
x0,n0,x1,n1=hydro.BOUNDS;clip=box(x0-834500,816500-n1,x1-834500,816500-n0)
land=unary_union([g for r,g in hydro.coast.ib5000() if r['layer']=='ContourPoly' and g.intersects(clip)]).intersection(clip)
fig,ax=plt.subplots(figsize=(11,10));ax.set_facecolor('#91c4df')
for p in hydro.coast.polys(land):
 ax.add_patch(Patch(list(p.exterior.coords),facecolor='#e7e7d7',edgecolor='#777',linewidth=.35))
 for ring in p.interiors:ax.add_patch(Patch(list(ring.coords),facecolor='#91c4df',edgecolor='#777',linewidth=.35))
for r,g in hydro.decode.load():
 if r['layer']!='HydroPolygon' or not g.intersects(clip):continue
 for p in hydro.coast.polys(g.intersection(clip)):ax.add_patch(Patch(list(p.exterior.coords),facecolor='#4265b7',edgecolor='none',alpha=.8))
routes=json.loads((DOC/'routes-staged.json').read_text())
walk=json.loads((DOC/'route-navigation.json').read_text())['walkCentreline']
x,z=zip(*walk);ax.plot(x,z,color='#c24038',lw=.8)
for s in routes['stops']:
 x,z=s['nodePosition'];ax.plot(x,z,'o',ms=4,color='#962716');ax.annotate(s['id'],(x,z),xytext=(3,7),textcoords='offset points',fontsize=8)
ax.set_xlim(clip.bounds[0],clip.bounds[2]);ax.set_ylim(clip.bounds[3],clip.bounds[1]);ax.set_aspect('equal');ax.set_title('Mui Wo: current LandsD land / river footprints and checked public route\nLight blue: mapped sea complement; dark blue: mapped rivers; red: checked route (source paths + promenade floor detour)')
ax.set_xlabel('City X (m)');ax.set_ylabel('City Z (m; south positive)');fig.tight_layout();fig.savefig(DOC/'source-geometry.png',dpi=160)
