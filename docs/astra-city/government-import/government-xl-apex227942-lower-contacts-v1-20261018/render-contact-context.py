import sys
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,read
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
base=ROOT/'docs/astra-city/government-import';d=base/'government-xl-apex227942-lower-contacts-v1-20261018';t=np.asarray(read(base/'government-xl-apex227942-four-world-v2-20261018/world-triangles.json.gz')['balanced']['landsd/227942:0']);r=read(d/'balanced-contacts.json')['rows'][0];ids=sorted({c['faceIndex']for c in r['firstContacts']if c['faceNormalY']<.15});origin=t.min((0,1));v=t-origin;v=v[:,:,[0,2,1]];fig=plt.figure(figsize=(12,9))
for n,az in enumerate([30,120,210,300]):
 ax=fig.add_subplot(2,2,n+1,projection='3d');ax.add_collection3d(Poly3DCollection(v,facecolors='#aac0cf',edgecolors='none',alpha=.65));ax.add_collection3d(Poly3DCollection(v[ids],facecolors='#c94a29',edgecolors='#7d2511',linewidths=.4));lo=v.min((0,1));hi=v.max((0,1));ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(lo[2],hi[2]));ax.set_box_aspect(hi-lo);ax.view_init(20,az);ax.set_title('Unchanged source; non-upward contact faces red');ax.set_xlabel('east (m)');ax.set_ylabel('south (m)');ax.set_zlabel('height above source bottom (m)')
fig.tight_layout();fig.savefig('/tmp/apex-contact-context.png',dpi=150)
