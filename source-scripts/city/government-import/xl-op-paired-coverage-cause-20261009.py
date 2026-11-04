"""Preserve complete original paired source projections and exact uncovered geometry.
Cause analysis only: no area omission, source editing or identity approval.
"""
import importlib.util,json,shutil,sys
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-op-paired-coverage-cause-20261009';LOCAL=HERE/'local/government-xl-op-paired-coverage-cause-20261009'
def mod(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def polygons(x):
 if x.geom_type=='Polygon':return [x]
 return [p for p in x.geoms if p.geom_type=='Polygon'] if hasattr(x,'geoms') else []
def draw(ax,shape,color,label,alpha=.5):
 for i,p in enumerate(polygons(shape)):
  x,y=p.exterior.xy;ax.fill(x,y,color=color,alpha=alpha,label=label if i==0 else None)
  for ring in p.interiors:x,y=ring.xy;ax.fill(x,y,color='white',alpha=1)
def main():
 old=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';paired=read(old/'paired-original-op-group-recovered-measures.json.gz')['rows'];native=read(HERE/'local/government-xl-identity-search-op-structures-20261009/paired-physical-source-candidates.json.gz')['rows'];bykey={r['sourceKey']:r['model'] for r in native};decode=mod('causal_pair_exact_source','xl-second-pass.py');decode.LOCAL=LOCAL;final=mod('causal_pair_current_forms','xl-final-script-pass.py');out=[]
 for r in paired:
  tri=[];sourceShapes=[];formshapes=[Polygon(b['rings'][0],b['rings'][1:]) for b in r['groupForms']]
  for source in r['sourceProofs']:
   p=ROOT/source['originalPath'];raw=p.read_bytes();assert digest(raw)==source['sourceSHA256'];asset=LOCAL/'assets'/(source['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,asset);m=bykey[source['sourceKey']];t=decode.glb_triangles({'sourceSHA256':source['sourceSHA256'],'modelId':source['modelId'],'triangles':m['triangles'],'native':{'model':m}});assert digest(t.astype('<f8').tobytes())==source['worldTrianglesSHA256'];tri.append(t);sourceShapes.append(shapely.union_all(shapely.polygons(t[:,:,[0,2]])))
  tri=np.concatenate(tri);projection=shapely.union_all(sourceShapes);target=shapely.union_all(formshapes);missing=target.difference(projection);excess=projection.difference(target);bounds=projection.bounds;context=final.load_forms([bounds[0]-2,bounds[1]-2,bounds[2]+2,bounds[3]+2]);groupuids={b['uid'] for b in r['groupForms']};others=[(b,p) for b,p,_ in context if b['uid'] not in groupuids];components=[]
  for p in sorted(polygons(missing),key=lambda p:p.area,reverse=True):
   components.append({'areaM2':float(p.area),'bounds':list(p.bounds),'touchesTargetExterior':bool(p.intersects(target.boundary)),'boundaryContactLengthM':float(p.boundary.intersection(target.boundary).length),'distanceToTargetExteriorM':float(p.distance(target.boundary)),'geometry':mapping(p)})
  overlaps=[{'uid':b['uid'],'name':b.get('name'),'areaM2':float(excess.intersection(p).area),'geometry':mapping(excess.intersection(p)),'building':b} for b,p in others if excess.intersection(p).area>1e-9]
  uid=r['uid'];prefix=uid.split('/')[1].replace(':','-');DIR=DOC/prefix;DIR.mkdir(parents=True,exist_ok=True)
  features=[{'type':'Feature','properties':{'role':'complete-original-projection'},'geometry':mapping(projection)},{'type':'Feature','properties':{'role':'complete-current-target'},'geometry':mapping(target)},{'type':'Feature','properties':{'role':'uncovered-target'},'geometry':mapping(missing)},{'type':'Feature','properties':{'role':'source-excess'},'geometry':mapping(excess)}]+[{'type':'Feature','properties':{'role':'unrelated-overlap','uid':x['uid'],'areaM2':x['areaM2']},'geometry':x['geometry']} for x in overlaps];save(DIR/'exact-projection-difference.geojson',{'type':'FeatureCollection','features':features,'coordinateFrame':'viewer metres x=easting-834500,y=816500-northing'})
  fig,axs=plt.subplots(1,2,figsize=(12,6));ax=axs[0]
  for i,s in enumerate(sourceShapes):draw(ax,s,['#2a9d8f','#457b9d'][i],r['sourceProofs'][i]['modelId'],.5)
  for p in formshapes:x,y=p.exterior.xy;ax.plot(x,y,color='#101010',linewidth=1.2)
  draw(ax,missing,'#e63946','Exact uncovered target',.85);draw(ax,excess,'#e9c46a','Source excess',.8)
  for x in overlaps:draw(ax,shapely.geometry.shape(x['geometry']),'#8f2d95','Unrelated overlap',.9)
  ax.set_aspect('equal');ax.invert_yaxis();ax.legend(fontsize=7);ax.set_title(uid+' / '+', '.join(r['structureIds'].__str__() for _ in [0]));ax.set_xlabel('Easting relative to834500(m)');ax.set_ylabel('Southward relative to816500(m)')
  # Unchanged source triangle wireframe oblique view, every triangle included.
  ax=axs[1];view=tri.reshape(-1,3);ax.scatter(view[:,0]-.4*view[:,2],view[:,1]+.3*view[:,2],s=.03,c= view[:,1],cmap='viridis',rasterized=True);ax.set_aspect('equal');ax.set_title('All original vertices, oblique diagnostic');ax.set_xlabel('x−0.4z');ax.set_ylabel('HKPD height+0.3z')
  fig.tight_layout();fig.savefig(DIR/'original-coverage-cause.png',dpi=200);plt.close(fig)
  lon,lat=Transformer.from_crs(2326,4326,always_xy=True).transform(target.centroid.x+834500,816500-target.centroid.y)
  item={'uid':uid,'groupForms':r['groupForms'],'sourceProofs':r['sourceProofs'],'targetAreaM2':float(target.area),'sourceProjectionAreaM2':float(projection.area),'uncoveredTargetAreaM2':float(missing.area),'uncoveredInteriorAreaM2':sum(p['areaM2'] for p in components if not p['touchesTargetExterior']),'uncoveredBoundaryConnectedAreaM2':sum(p['areaM2'] for p in components if p['touchesTargetExterior']),'uncoveredComponents':components,'unrelatedOverlaps':overlaps,'gps':{'latitude':lat,'longitude':lon},'sourceProjectionHoles':[mapping(Polygon(ring)) for p in polygons(projection) for ring in p.interiors],'identityAccepted':False,'installationApproved':False,'qualification':'Exact unchanged full-original projection and target differences retained. Boundary contact and interior holes are geometry diagnostics, not courtyard/openvoid ownership semantics. No uncovered area omitted or identity threshold waived.'};save(DIR/'cause.json.gz',item);out.append(item);print(json.dumps({k:item[k] for k in ['uid','targetAreaM2','uncoveredTargetAreaM2','uncoveredInteriorAreaM2','uncoveredBoundaryConnectedAreaM2','gps']}|{'largestComponents':[{k:p[k] for k in ['areaM2','touchesTargetExterior','bounds']} for p in components[:8]],'overlaps':[{k:p[k] for k in ['uid','areaM2','name']} for p in overlaps]}),flush=True)
 save(DOC/'causal-diagnostics.json.gz',{'rows':out})
if __name__=='__main__':main()
