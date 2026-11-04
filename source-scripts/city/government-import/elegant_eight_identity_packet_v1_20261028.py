"""Prepare exact direct-registration evidence for eight source-association reviews."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,MultiPoint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,reservations,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
UIDS=['landsd/171904:0','landsd/224123:0','landsd/236367:0','landsd/100673:0','landsd/234554:0','landsd/215726:0','landsd/255031:0','landsd/224121:0']

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('eight-exact-identity-packet-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']};official={r['uid']:r for r in take(PREFIX+'current-primary-records-v1-20261028','summary.json')['rows']};forms=take(PREFIX+'sixteen-original-updated-scope-v1-20261028','form-obligations.json.gz')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 cases={u:[]for u in UIDS}
 for path in BASE.glob(PREFIX+'*/*/identity.json'):
  r=read(path);u=r.get('uid')
  if u in cases and r.get('sourceSHA256')==sources[u]['sourceSHA256']and r.get('exactRouteManifestSHA256')==selection['manifestSHA256']:cases[u].append(path)
 rows=[]
 fig,axes=plt.subplots(4,2,figsize=(17,22),dpi=150)
 def draw(ax,shape,color,fill=False):
  if shape.is_empty:return
  if shape.geom_type=='Polygon':
   x,y=shape.exterior.xy
   if fill:ax.fill(x,y,color=color,alpha=.3)
   ax.plot(x,y,color=color,linewidth=1.1)
   for ring in shape.interiors:ax.plot(*ring.xy,color=color,linewidth=.8)
  elif hasattr(shape,'geoms'):
   for part in shape.geoms:draw(ax,part,color,fill)
  elif shape.geom_type in ['LineString','LinearRing']:ax.plot(*shape.xy,color=color,linewidth=.7)
  elif shape.geom_type=='Point':ax.scatter([shape.x],[shape.y],color=color,s=5)
 for ax,uid in zip(axes.flat,UIDS):
  assert len(cases[uid])==1;path=cases[uid][0];raw=take(path.parent.parent.name,str(path.relative_to(path.parent.parent)))
  source=sources[uid];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==raw['sourceSHA256'];refs.append(asset)
  assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['freshCurrentIdentity']['exactObjectAndCSUID']and raw['completeRecordProjection']
  b=source['source']['building'];tile=ROOT/'3d-viewer'/source['source']['tile'];assert digest(tile.read_bytes())==source['source']['tileSHA256'];refs.append(tile);actual=next(f for f in read(tile)['buildings']if f['uid']==uid);assert actual==b==raw['exactCurrentComponentRoute']['source']['building']
  assert source['modelId'][1:11]==actual['buildingCSUID'][:10]and source['modelId'][11:13]==('01'if actual['structureType']=='Tower'else'02')
  assert source['native']['model']['candidate']['uid']==uid and source['native']['model']['candidate']['buildingCSUID']==actual['buildingCSUID']
  record=official[uid];assert record['uniqueOfficialRecord'];record=record['officialRecords'][0];assert record['Status']=='Active'and record['BuildingCSUID']==actual['buildingCSUID']and record['BuildingBlockType']==actual['structureType']
  assert record['BaseHeight']==actual['base']and abs(record['TopHeight']-actual['base']-actual['height'])<1e-8
  tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==source['triangles']and digest(tri.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
  projection=shapely.union_all([MultiPoint(f[:,[0,2]]).convex_hull for f in tri]);target=Polygon(actual['rings'][0],actual['rings'][1:]);lo=np.minimum(projection.bounds[:2],target.bounds[:2])-2;hi=np.maximum(projection.bounds[2:],target.bounds[2:])+2
  for other in forms:
   poly=Polygon(other['rings'][0],other['rings'][1:])
   if other['uid']!=uid and poly.intersects(projection.envelope):draw(ax,poly,'#c3c3c3')
  draw(ax,projection,'#245f9e',True);draw(ax,target,'#c0263d')
  cell=raw['geographicCell']['worldXZBounds'];draw(ax,shapely.box(*cell),'#59616a');ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),aspect='equal',xlabel='World X / m',ylabel='World Z / m')
  ax.set_title(uid+' | '+str(record.get('BuildingNameEN'))+'\n'+source['modelId']+' | '+actual['structureType']+'\nBlue: complete original projection; red: current BASIC; grey: georef cell\nTarget coverage '+format(raw['freshCurrentIdentity']['targetCoveredBySourceProjection']*100,'.2f')+'%; native Y '+format(float(tri[:,:,1].min()),'.3f')+'..'+format(float(tri[:,:,1].max()),'.3f')+'; record '+str(actual['base'])+'..'+str(actual['topHeightHKPD']),fontsize=9);ax.grid(alpha=.2)
  row=dict(uid=uid,modelId=source['modelId'],sourceSHA256=source['sourceSHA256'],sourceFormSHA256=digest(__import__('json').dumps(actual,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()),rawPreparedSourceFormSHA256=raw['sourceFormSHA256'],tile=str(tile.relative_to(ROOT)),tileSHA256=digest(tile.read_bytes()),worldTrianglesSHA256=raw['worldTrianglesSHA256'],completeSourceFaces=len(tri),sourceYRange=[float(tri[:,:,1].min()),float(tri[:,:,1].max())],officialRecord=record,sourceEntry=source['native']['model']['sourceEntry'],nativeCacheKey=source['native']['cacheKey'],nativeResultSHA256=source['native']['resultSha'],rawIdentityPath=str(path.relative_to(ROOT)),rawIdentitySHA256=digest(path.read_bytes()),rawIdentityVerbatim=raw,sourceGraphVerified=True,exactTypedRouteQualified=True,uniqueOfficialActiveCSUID=True,identityOnlyApproved=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
  save(out/(uid.split('/')[1]+'-packet.json'),row);rows.append(row)
 fig.tight_layout();image=out/'eight-exact-source-projection-map.png';fig.savefig(image);plt.close(fig)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for key,sha in {r['nativeCacheKey']:r['nativeResultSHA256']for r in rows}.items():assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(sha,)
 result=dict(uids=UIDS,rows=[{k:v for k,v in r.items()if k!='rawIdentityVerbatim'}for r in rows],image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),currentManifestSHA256=selection['manifestSHA256'],identityOnlyApproved=False,physicalAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Eight exact registered original source units, positive complete source graph/current typed CSUID routing/unique active official records, full original projection maps and every raw spatial failure retained. This is evidence preparation only. No source-association, physical completeness, height discrepancy, boundary ownership or installation approval is inferred.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 module('eight_identity_packet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'eight-exact-original-registration-identity-evidence-packet',list(dict.fromkeys(refs)),read(out/'summary.json'))

if __name__=='__main__':main()
