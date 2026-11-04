"""Stable provider lineage and original excess-face context; no approval override."""
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-namcheong244683-authoritative-identity-v1-20261017';BATCH='government-xl-namcheong244683-provider-extent-context-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];form=row['source']['building'];provider=read(CAP/'provider.json');assert len(provider['features'])==1;f=provider['features'][0];a=f['attributes'];stable=dict(active=a['Status']=='Active',csuid=a['BuildingCSUID']==form['buildingCSUID'],buildingID=a['BuildingID']==form['buildingId'],type=a['BuildingBlockType']==form['structureType'],geoRef=a['GeoRefNo']==row['modelId'][1:11],creationDate=datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==form['buildingCSUID'][11:],base=a['BaseHeight']==form['base'],top=a['TopHeight']==form['topHeightHKPD']);assert all(stable.values())
 target=shapely.Polygon(form['rings'][0],form['rings'][1:]);rings=[[(v[0]-834500,816500-v[1])for v in ring]for ring in f['geometry']['rings']];current=shapely.Polygon(rings[0],rings[1:]);tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert len(tri)==20645;dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3);ids=np.flatnonzero(dist.max(axis=1)>10);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));excess=projection.difference(target)
 save(DOC/'context.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],stableFields=stable,viewerObjectId=form['objectId'],providerObjectId=a['OBJECTID'],footprintSymmetricDifferenceM2=target.symmetric_difference(current).area,footprintHausdorffM=target.hausdorff_distance(current),extentFaces=ids.tolist(),extentFaceHeightBounds=[float(tri[ids,:,1].min()),float(tri[ids,:,1].max())],maximumExtentM=float(dist.max()),fullAcceptance=False,identityAccepted=False,qualification='Stable fields verify record continuity only. Provider OBJECTID difference retained; original spatial bounds and source-role acceptance are unresolved.'))
 fig,ax=plt.subplots(figsize=(9,10),dpi=150)
 for geom,color,label in [(projection,'#b6cdd7','Complete source projection'),(target,'#e1b650','Viewer footprint'),(excess,'#ce4d4d','Source excess')]:
  parts=list(geom.geoms)if hasattr(geom,'geoms')else[geom]
  for i,g in enumerate(parts):
   if g.geom_type=='Polygon':ax.fill(*g.exterior.xy,color=color,alpha=.5,label=label if i==0 else None)
 for i in ids:ax.plot(*tri[i][:,[0,2]].T,color='#8b0017',alpha=.25,linewidth=.4)
 ax.set_aspect('equal');ax.legend();ax.set(xlabel='Viewer east m',ylabel='Viewer south m',title='Nam Cheong: unchanged source footprint and >10m extent faces');fig.tight_layout();fig.savefig(DOC/'extent-plan.png');plt.close(fig)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('nam_extent_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong-stable-provider-lineage-and-excess-face-context-v1',[Path(__file__),CAP/'result.json',*[ROOT/p for p in pins]],dict(uids=[row['uid']],stableProviderFieldsVerified=True,identityAccepted=False,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
