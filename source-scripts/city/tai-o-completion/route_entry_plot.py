"""Reproduce the bridge-entry source disagreement and final walking-line diagnostic."""
import gzip,json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/tai-o-completion'
r=json.loads((DOC/'route.json').read_text());entry=r['publicConnectors'][0]
m=next(m for m in json.loads(gzip.decompress((HERE/'infrastructure-models.json.gz').read_bytes()))['models'] if m['id']==entry['sourceBridgeId']);a=m['modelGeometry']['position']
fig,ax=plt.subplots(figsize=(10,8),dpi=160);fig.patch.set_facecolor('#f6f3eb');ax.set_facecolor('#f6f3eb')
for i in range(len(a)//9):
 p=[a[j:j+3] for j in range(i*9,i*9+9,3)]
 if max(t[2] for t in p)<3676:continue
 ax.add_patch(Polygon([(t[0],t[2]) for t in p],facecolor='#aad3c3' if i in m['walkTriangleIndices'] else 'none',edgecolor='#808b86',linewidth=.3))
seen=set()
for f in entry['sources'][1]['features']:
 kind=f['attributes']['PEDESTRIANTYPE']
 for line in f['paths']:
  ax.plot(*zip(*line),color={'STP':'#cf604d','FBR':'#26809a','PA':'#cc9444'}[kind],lw=1.1,label=None if kind in seen else 'iB1000 '+kind+' plan lines');seen.add(kind)
ax.plot(*zip(*r['centreline'][19:24]),color='#2d55a3',lw=1.6,ls='--',label='Original OSM line (retained)')
ax.plot(*zip(*entry['centreline']),color='#cf9335',lw=4,alpha=.65,label='Explicitly estimated public connector')
ax.plot(*zip(*r['walkCentreline']),color='#28332e',lw=1.6,label='Continuously verified walking line')
ax.scatter(*entry['sourceDeckEntry'],s=55,color='#7f3d8c',zorder=5,label='Exact source floor boundary entry')
ax.set_xlim(-30673,-30653);ax.set_ylim(3692,3676.5);ax.set_aspect('equal');ax.grid(alpha=.18);ax.tick_params(labelsize=8)
ax.set_title('TAI CHUNG BRIDGE  /  PUBLIC ENTRY\nOriginal railings preserved; source plan and mesh discrepancy remains explicit',loc='left',fontsize=12,pad=15)
ax.set_xlabel('World x / metres (east)');ax.set_ylabel('World z / metres (south)');ax.legend(fontsize=7,loc='lower left',framealpha=.96)
fig.text(.125,.015,'Sources: Lands Department original 3D mesh + iB1000 linework; OpenStreetMap. Added approach alignment and stair profile are illustrative.',fontsize=7)
fig.savefig(DOC/'route-entry-review.png',bbox_inches='tight');plt.close(fig)
