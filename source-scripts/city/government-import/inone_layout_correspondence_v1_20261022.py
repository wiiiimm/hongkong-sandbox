"""North-up current footprint context for primary layout comparison."""
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-inone-layout-correspondence-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists()
 prior=BASE/'government-xl-inone-original-pair-overlap-v1-20261022'
 _,pins=authenticate(prior);p=prior/'comparison.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 pair=read(p);domain=shapely.from_wkt(pair['overlapWKT'])
 tile=ROOT/'3d-viewer/city/data/tiles/1_-2.json';rows=[]
 fig,ax=plt.subplots(figsize=(12,12))
 for b in read(tile)['buildings']:
  x,z=b['centre']
  if not (2200<x<2600 and -2800<z<-2300):continue
  if not b['uid'].startswith('landsd/'):continue
  rows.append(b)
  for ring in b['rings']:
   r=np.array(ring);ax.plot(r[:,0],-r[:,1],color='gray',lw=.6)
  label=b['uid'].split('/')[1].split(':')[0]+' '+(b.get('name')or b.get('kind',''))
  ax.text(x,-z,label,fontsize=5,ha='center')
 for source,color in zip(pair['sources'],['blue','orange']):
  foot=shapely.from_wkt(source['sourceFootprintWKT'])
  x,z=foot.exterior.xy;ax.plot(x,-np.array(z),color=color,lw=2,label=source['uid'])
 for part in shapely.get_parts(domain):
  if part.geom_type=='Polygon':
   x,z=part.exterior.xy;ax.fill(x,-np.array(z),color='red',alpha=.5)
 ax.set_aspect('equal');ax.legend();ax.set_xlabel('World X (east)');ax.set_ylabel('-World Z (north)');ax.set_title('Current government footprints; red = exact flagged overlap, not approval')
 doc.mkdir();fig.savefig(doc/'north-up-context.png',dpi=180);plt.close(fig)
 summary=dict(uids=['landsd/277890:0','landsd/277973:0'],rows=rows,overlapAreaM2=domain.area,identityReviewApproved=False,installationApproved=False,qualification='North-up footprint context only; primary brochure is not georeferenced.')
 save(doc/'context.json',summary)
 module('layout_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'primary-layout-footprint-correspondence-context',[Path(__file__),p,prior/'result.json',tile],summary)
if __name__=='__main__':main()
