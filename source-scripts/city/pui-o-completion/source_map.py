"""Export a bounded source-coverage diagnostic, not a rendered city screenshot."""
import gzip,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/hks171-matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as Patch,Patch as LegendPatch
import numpy as np
from run import HERE,DOC

def main():
 package=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()));model=json.loads(gzip.decompress((HERE/'model-geometries.json.gz').read_bytes()))['byBuildingUid'];terrain=json.loads((HERE/'terrain-pui-o.json').read_text());audit=json.loads((DOC/'terrain-audit.json').read_text());route=json.loads((DOC/'route.json').read_text());conflicts={r['uid'] for r in audit['rows'] if r['partlyBelow']}
 g=terrain['meta']['georef'];x=np.arange(terrain['w'])*5+g['bE']-834500;z=816500-g['bN']+np.arange(terrain['h'])*5;e=np.array(terrain['elev']).reshape(terrain['h'],terrain['w'])
 fig,ax=plt.subplots(figsize=(17,11),dpi=100);fig.patch.set_facecolor('#f4f3ed');ax.set_facecolor('#f4f3ed')
 ax.contourf(x,z,e,levels=[-1000,0,5,15,30,60,100,200,1000],colors=['#d4e6ed','#f2f0df','#e8ead4','#dde3c7','#d1dcb8','#c2d1a9','#aec293','#95ad7d'],alpha=.9)
 for name,color in [('fallback','#a19d96'),('model','#357269'),('conflict','#c04445')]:
  polys=[Patch(b['rings'][0],closed=True) for b in package['buildings'] if ('conflict' if b['uid'] in conflicts else 'model' if b['uid'] in model else 'fallback')==name]
  ax.add_collection(PatchCollection(polys,facecolor=color,edgecolor='#f9faf6',linewidth=.25,zorder=3))
 line=np.array(route['centreline']);ax.plot(line[:,0],line[:,1],color='#dc831f',linewidth=3.5,zorder=5)
 for xmin,xmax,zmin,zmax,title in [(-19500,-18750,4500,5100,'14-NW-1A'),(-18750,-18000,4500,5100,'14-NW-1B'),(-19500,-18750,5100,5700,'14-NW-1C'),(-18750,-18000,5100,5700,'14-NW-1D')]:
  ax.plot([xmin,xmax,xmax,xmin,xmin],[zmin,zmin,zmax,zmax,zmin],color='#344c58',linewidth=.7,linestyle='--',zorder=4)
  ax.text(xmin+18,zmin+26,title,color='#344c58',fontsize=10,va='top',bbox={'facecolor':'#f4f3ed','edgecolor':'none','alpha':.85})
 ax.annotate('Pui O Playground',(-18798.4,5085),(-19290,5220),arrowprops={'arrowstyle':'-','color':'#4c5354'},fontsize=10,zorder=6)
 ax.annotate('Pui O beach edge\n555 m continuous route',line[5],(-19060,5640),arrowprops={'arrowstyle':'-','color':'#4c5354'},fontsize=10,zorder=6)
 ax.text(-18350,4940,'Ham Tin',ha='center',fontsize=11,color='#3b4a4b')
 ax.set_xlim(-19630,-17870);ax.set_ylim(5830,4370);ax.set_aspect('equal');ax.set_xlabel('City east–west position (metres)');ax.set_ylabel('City southward position (metres)')
 ax.set_title('PUI O · FOUR OFFICIAL SOURCE SHEETS\n681 matched detailed models / 919 existing government forms',loc='left',fontsize=19,pad=18,color='#203c3b')
 ax.legend(handles=[LegendPatch(facecolor='#357269',label='Verified detailed match'),LegendPatch(facecolor='#a19d96',label='Retained outline fallback'),LegendPatch(facecolor='#c04445',label='Residual terrain conflict (2 footprints)'),LegendPatch(facecolor='#dc831f',label='Retained public footway')],loc='upper right',fontsize=9,framealpha=.95)
 fig.text(.135,.03,'Source: Lands Department 3D sheets revised 11 May 2026 (HKT); official outline snapshot v20260819; retained OSM 6 September 2026.\nTint shows staged terrain and its preserved non-positive DTM mask. It is not a surveyed tidal or wetland-inundation boundary. Staged only.',fontsize=10,color='#4c5354')
 fig.subplots_adjust(left=.10,right=.96,bottom=.13,top=.88);fig.savefig(DOC/'pui-o-source-coverage-1700x1100.png',dpi=100);plt.close(fig)
if __name__=='__main__':main()
