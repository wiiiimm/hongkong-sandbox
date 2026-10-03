import pathlib,sys,json,zipfile,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
sys.path.insert(0,'docs/astra-city/mui-wo-buildings/review');from prepare_model_sample import model_geometry
z=zipfile.ZipFile('source-scripts/city/ting-kau/sources/6-SE-23B/6-SE-23B.zip');n=next(n for n in z.namelist() if n.endswith('.gltf'));d=json.loads(z.read(n));p=pathlib.PurePosixPath(n).parent;pos,_=model_geometry(d,lambda uri:z.read(str(p/uri)));T=pos.reshape(-1,3,3)
a=np.array([-8427.765,-8887.478]);b=np.array([-8019.633,-8059.256]);u=(b-a)/np.linalg.norm(b-a);v=np.array([-u[1],u[0]]);long=(pos[:,[0,2]]-a)@u;cross=(pos[:,[0,2]]-a)@v
cables=json.load(open('source-scripts/city/ting-kau/cables-ting-kau.json'));
fig,axes=plt.subplots(2,1,figsize=(14,7),dpi=180)
for ax,xx,yy,title in [(axes[0],long,pos[:,1],'Original infrastructure mesh only · longitudinal elevation'),(axes[1],long,cross,'Original infrastructure mesh only · plan')]:
 polys=np.stack([xx,yy],axis=1).reshape(-1,3,2);ax.add_collection(PolyCollection(polys,facecolor='#b5bac0',edgecolor='#485667',linewidth=.08));ax.autoscale();ax.set_aspect('equal');ax.set_title(title);ax.set_ylabel('Metres')
axes[1].set_xlabel('Metres from northern source tower towards Tsing Yi');fig.tight_layout();fig.savefig('docs/astra-city/ting-kau/source-infrastructure-inspection.png')
for part in cables['parts']:
 pp=np.array(part['path']);ll=(pp[:,[0,2]]-a)@u;cc=(pp[:,[0,2]]-a)@v
 axes[0].plot(ll,pp[:,1],color='#1b7185',lw=.28,alpha=.75);axes[1].plot(ll,cc,color='#1b7185',lw=.22,alpha=.5)
axes[0].set_title('Ting Kau · unchanged original structure + separately labelled illustrative cable stays')
axes[1].set_title('Four fan planes · exact individual attachment offsets and cable inventory are not reconstructed')
fig.savefig('docs/astra-city/ting-kau/source-with-illustrative-stays.png');print('Inspected source and separate illustrative fan-stay views, 2520×1260')
