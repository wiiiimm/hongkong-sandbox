"""CPU-only, fixed-scale whole-foundation terrain comparison."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely import intersects_xy
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
from foundation_stage import HERE, ROOT, OUT, DOC

def plot():
    old=json.loads((HERE/'combined/terrain-tsing-ma-ting-kau.json').read_text());new=json.loads((OUT/'terrain-tsing-ma-ting-kau.json').read_text());h=json.loads((OUT/'hydro-tsing-ma-ting-kau.json').read_text())
    features=json.loads((OUT/'foundation-scope.geojson').read_text())['features'];islands=[(f['properties']['name'],shape(f['geometry'])) for f in features if f['properties']['role']=='mapped-foundation-island']
    land=unary_union([box(*p['bounds']) for p in h['regions']]).difference(unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in h['water']]))
    areas=islands+[('Southern Ting Kau footing',land.intersection(box(-8180,-8140,-7880,-7950)))]
    g=new['meta']['georef'];x=g['bE']+np.arange(new['w'])*5-834500;z=816500-g['bN']+np.arange(new['h'])*5;xx,zz=np.meshgrid(x,z)
    arrays=[np.array(d['elev']).reshape(new['h'],new['w']) for d in [old,new]]
    fig,axes=plt.subplots(3,2,figsize=(12,10),dpi=200);fig.patch.set_facecolor('#f5f5ef')
    for row,(name,p) in enumerate(areas):
        a,b,c,d=p.bounds;extent=(a-12,c+12,d+12,b-12)
        keep=intersects_xy(p,xx,zz)
        for col,values in enumerate(arrays):
            ax=axes[row,col];ax.set_facecolor('#9bd5e3');image=ax.pcolormesh(x,z,np.ma.array(values,mask=~keep),vmin=0,vmax=50,cmap='cividis',shading='nearest',rasterized=True)
            parts=list(p.geoms) if hasattr(p,'geoms') else [p]
            for q in parts:
                if isinstance(q,Polygon):ax.plot(*q.exterior.xy,color='#203839',lw=.65)
            ax.set_xlim(*extent[:2]);ax.set_ylim(*extent[2:]);ax.set_aspect('equal');ax.tick_params(labelsize=7)
            ax.set_title(name+' · '+('previous blend' if col==0 else 'source heights restored'),fontsize=10,loc='left')
            ax.set_xlabel('City east (m)',fontsize=8);ax.set_ylabel('City south (m)',fontsize=8)
            ax.text(.02,.03,f'Grid maximum {values[keep].max():.2f} m HKPD',transform=ax.transAxes,fontsize=8,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none','pad':3})
    fig.suptitle('Bridge foundations: retained source terrain replaces archival mask artefacts',x=.065,ha='left',fontsize=14,y=.975)
    fig.subplots_adjust(left=.07,right=.9,top=.925,bottom=.09,hspace=.42,wspace=.26)
    cbar=fig.colorbar(image,cax=fig.add_axes([.92,.2,.015,.6]));cbar.set_label('Height above Hong Kong Principal Datum (m)',fontsize=9)
    fig.text(.07,.025,'Identical 5 m grid and mapped land boundaries. Fixed 0–50 m scale; blue is mapped water.\nTerrain-only comparison: bridge meshes and cable illustrations omitted. No smoothing or invented heights.',fontsize=9,color='#34494a')
    fig.savefig(DOC/'foundation-terrain-comparison-2400x2000.png',dpi=200);plt.close(fig)
if __name__=='__main__':plot()
