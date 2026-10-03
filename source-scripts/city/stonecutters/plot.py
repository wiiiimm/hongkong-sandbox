"""CPU source geometry proof with original HKPD placement."""
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from fetch import HERE,ROOT

def plot():
    p=json.loads((HERE/'bridges-stonecutters.json').read_text());fig=plt.figure(figsize=(12.6,6.3),dpi=200);ax=fig.add_subplot(111,projection='3d');allpoints=[]
    for m in p['models']:
        tri=np.array(m['modelGeometry']['position']).reshape(-1,3,3);allpoints.extend(tri.reshape(-1,3));mapped=tri[:,:,[0,2,1]]
        ax.add_collection3d(Poly3DCollection(mapped,facecolor='#9ba9a7' if not m['suppressesBuildingUids'] else '#436a70',edgecolor='none'))
    points=np.array(allpoints);lo=points.min(axis=0);hi=points.max(axis=0)
    ax.set_xlim(lo[0]-25,hi[0]+25);ax.set_ylim(lo[2]-25,hi[2]+25);ax.set_zlim(0,320);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],320]);ax.view_init(elev=22,azim=-59)
    ax.set_xlabel('City east (m)',fontsize=8);ax.set_ylabel('City south (m)',fontsize=8);ax.set_zlabel('HKPD (m)',fontsize=8);ax.tick_params(labelsize=7)
    fig.suptitle('Stonecutters Bridge · original government deck and two tower models',x=.04,ha='left',fontsize=13,y=.97)
    fig.text(.045,.045,'Three original components · 23,634 source triangles · no coordinate/height rescaling\nSeparate tower upper extents: 305.097 m and 299.353 m HKPD; building metadata/design tower level: 298 m. Cable detail audited separately.',fontsize=8,color='#354b4d')
    fig.subplots_adjust(left=.01,right=.99,top=.94,bottom=.1);fig.savefig(ROOT/'docs/astra-city/stonecutters/original-components-2520x1260.png',dpi=200);plt.close(fig)
if __name__=='__main__':plot()
