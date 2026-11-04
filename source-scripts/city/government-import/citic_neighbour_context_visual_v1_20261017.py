"""Four unchanged original-source context views; diagnostic, not runtime acceptance."""
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
local=HERE/'local/government-xl-citic-neighbour-originals-v1-20261017';doc=ROOT/'docs/astra-city/government-import/government-xl-citic-exact-contacts-v1-20261017'
rows=[dict(uid='CITIC podium',sourceSHA256='a8058e18e0fbdfa4a38b10b9b58a5dea5d62ddf0debf76df1e39198a07969b74')]+read(ROOT/'docs/astra-city/government-import/government-xl-citic-neighbour-originals-v1-20261017/source-records.json')
tri=[]
for r in rows:
 raw=(local/'assets'/(r['sourceSHA256']+'.glb.gz')).read_bytes();assert digest(raw)==r['sourceSHA256'];tri.append(decode_original_world_triangles(raw))
fig=plt.figure(figsize=(16,13),dpi=120);colors=['#e9b44c','#487dcc','#a75bb0','#50b598'];center=np.array([765,0,775])
for i,(elev,azim) in enumerate([(70,-80),(15,-60),(15,120),(10,30)]):
 ax=fig.add_subplot(2,2,i+1,projection='3d')
 for t,c,r in zip(tri,colors,rows):
  ax.add_collection3d(Poly3DCollection((t-center)[:,:,[0,2,1]],facecolor=c,edgecolor='#333333',linewidth=.12,alpha=.65,label=r['uid']))
 for r in read(doc/'contacts.json.gz')['rows']:
  for contact in r['proof']['contacts']:
   pts=np.array([[float(__import__('fractions').Fraction(x)) for x in p] for p in contact['exactPoints']])-center
   ax.plot(pts[:,0],pts[:,2],pts[:,1],color='red',linewidth=2)
 ax.set_xlim(-60,50);ax.set_ylim(-60,65);ax.set_zlim(0,55);ax.set_box_aspect((110,125,55));ax.view_init(elev=elev,azim=azim);ax.set_title(f'Original sources — elevation {elev}, azimuth {azim}')
 ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('HKPD m')
fig.suptitle('CITIC podium: gold | Tamar low block: blue | Substation: purple | Small neighbour: green\nExact original contacts: red. Source geometry unchanged; diagnostic views only.')
fig.tight_layout();fig.savefig(doc/'original-neighbours-context-1920x1560.png')
