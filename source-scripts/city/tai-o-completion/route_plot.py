"""Plot the retained route against current authoritative footprint geometry."""
import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/tai-o-completion'
r=json.loads((DOC/'route.json').read_text());m=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text());pts=r['centreline'];xs=[p[0] for p in pts];zs=[p[1] for p in pts];bounds=[min(xs)-35,min(zs)-30,max(xs)+35,max(zs)+30]
fig,ax=plt.subplots(figsize=(10,10),dpi=160);fig.patch.set_facecolor('#f6f3eb');ax.set_facecolor('#f6f3eb')
for t in m['tiles']:
 if t['bounds'][0]>bounds[2] or t['bounds'][2]<bounds[0] or t['bounds'][1]>bounds[3] or t['bounds'][3]<bounds[1]:continue
 for b in json.loads((ROOT/'3d-viewer'/t['url']).read_text())['buildings']:
  if not bounds[0]-20<b['centre'][0]<bounds[2]+20 or not bounds[1]-20<b['centre'][1]<bounds[3]+20:continue
  ax.add_patch(Polygon(b['rings'][0],facecolor='#dedacf',edgecolor='#aca99e',linewidth=.45))
ax.plot(xs,zs,color='#287b96',linewidth=1.4,label='Retained mapped public centreline')
if r.get('walkCentreline'):ax.plot(*zip(*r['walkCentreline']),color='#c55f3b',linewidth=1,label='Verified walk / documented public entry')
for s in r['segments']:
 if s['kind']=='bridge':ax.plot(*zip(*pts[s['fromIndex']:s['toIndex']+1]),color='#d68b31',linewidth=3,label='Tai Chung Bridge source centreline')
for i,s in enumerate(r['stops'],1):
 p=pts[s['index']];ax.scatter(*p,s=115,color='#172a35',zorder=6);ax.annotate(str(i),p,color='white',ha='center',va='center',fontsize=8,zorder=7)
ax.set_xlim(bounds[0],bounds[2]);ax.set_ylim(bounds[3],bounds[1]);ax.set_aspect('equal');ax.grid(alpha=.15);ax.tick_params(labelsize=7);ax.set_xlabel('World x / metres (east)');ax.set_ylabel('World z / metres (south)')
ax.set_title(f"TAI O  /  PUBLIC VILLAGE WALK\n{r['lengthMetres']:.1f} m original source / {r.get('walkLengthMetres',r['lengthMetres']):.1f} m walking line",loc='left',fontsize=13,pad=16)
ax.text(.02,.98,'N ↑',transform=ax.transAxes,va='top',fontsize=11)
ax.legend(loc='lower left',fontsize=7,framealpha=.95)
fig.text(.12,.04,'  ·  '.join(f"{i}. {s['title']}" for i,s in enumerate(r['stops'][:3],1)),fontsize=7)
fig.text(.12,.023,'  ·  '.join(f"{i}. {s['title']}" for i,s in enumerate(r['stops'][3:],4)),fontsize=7)
fig.text(.12,.005,'Sources: OpenStreetMap contributors / ODbL; Lands Department building outlines. Planimetric check only; continuous runtime walking is a separate acceptance test.',fontsize=6)
fig.savefig(DOC/'route-plan.png',bbox_inches='tight');plt.close(fig)
