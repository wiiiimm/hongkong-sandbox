"""Exact original podium projection/topology plus primary architect context.

No automatic identity, ownership, physical-role or installation approval.
"""
import argparse,json,re,sys,uuid,urllib.request,urllib.parse
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fleur-podium-projection-primary-context-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';IDENTITY='government-xl-two-passing-podium-pairs-current-identity-v1-20261023';CONTACTS='government-xl-nine-recovery-269972-0-contacts-v1-20261028';SHA='a1d429abbd61c3b5f5310ccb03090c747c8350de222dc06d3fb3a28bf5555f8b'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:landsd/23296:0','building:landsd/269972:0'}<=set(lease['resources']);assert not DOC.exists();_,pins=authenticate(BASE/IDENTITY);ip=BASE/IDENTITY/'23296:0/identity.json';assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))];identity=read(ip);assert identity['sourceSHA256']==SHA and not identity['passed'];refs=[Path(__file__),BASE/IDENTITY/'result.json',ip]
 for relative,sha in identity['exactRouteTileHashes'].items():assert digest((ROOT/'3d-viewer'/relative).read_bytes())==sha;refs.append(ROOT/'3d-viewer'/relative)
 receipt,_=authenticate(BASE/CONTACTS);refs.append(BASE/CONTACTS/'result.json');asset=next(ROOT/r['path']for r in receipt['evidenceRefs']if r['sha256']==SHA and r['path'].endswith('.glb.gz'));assert digest(asset.read_bytes())==SHA;refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==3657 and digest(tri.astype('<f8').tobytes())==identity['worldTrianglesSHA256']
 building=identity['exactCurrentComponentRoute']['source']['building'];target=shapely.GeometryCollection()
 for ring in building['rings']:target=target.symmetric_difference(shapely.Polygon(ring))
 assert target.is_valid;polys=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polys[shapely.area(polys)>0]);assert projection.is_valid;missing=target.difference(projection);excess=projection.difference(target);parts=list(missing.geoms)if hasattr(missing,'geoms')else[missing];missing_rows=[dict(areaM2=p.area,touchesTargetBoundary=bool(p.boundary.intersects(target.boundary)),bounds=list(p.bounds))for p in parts if p.area>0]
 captures=[]
 def capture(url,name):
  path=LOCAL/'primary'/name
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30)as response:
    final=response.url;assert urllib.parse.urlparse(final).hostname in['www.wongtung.com','www.fleurpavilia.com.hk','fleurpavilia.com.hk'];raw=response.read(16*1024**2+1);assert len(raw)<=16*1024**2;headers={k:v for k,v in response.headers.items()if k.lower()in['content-type','last-modified','etag']}
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);refs.append(path);captures.append(dict(url=url,finalURL=final,path=str(path.relative_to(ROOT)),sha256=digest(raw),headers=headers));return raw
  except Exception as error:captures.append(dict(url=url,errorType=type(error).__name__));return b''
 architect='https://www.wongtung.com/en/projects/fleur_pavilia/';html=capture(architect,'architect.html').decode('utf8',errors='replace');capture('https://www.fleurpavilia.com.hk/','vendor.html');urls=[]
 for u in re.findall(r'https://www\.wongtung\.com/wp-content/uploads/[^\s"<>]+',html):
  if 'fleur'in u.lower()and re.search(r'\.jpe?g$',u,re.I)and not re.search(r'-\d+x\d+\.',u)and u not in urls:urls.append(u)
 for i,url in enumerate(urls[:3]):capture(url,'architect-project-image-'+str(i+1)+'.jpg')
 def paint(ax,geometry,color,alpha=1):
  if geometry.is_empty:return
  if hasattr(geometry,'geoms'):
   for part in geometry.geoms:paint(ax,part,color,alpha)
  elif geometry.geom_type=='Polygon':
   xy=np.asarray(geometry.exterior.coords);ax.fill(xy[:,0],xy[:,1],color=color,alpha=alpha)
   for ring in geometry.interiors:
    xy=np.asarray(ring.coords);ax.fill(xy[:,0],xy[:,1],color='white')
 fig,axes=plt.subplots(1,2,figsize=(14,9),dpi=150)
 for ax in axes:
  paint(ax,target,'#cfd4d7');paint(ax,projection,'#1a8294',.55);ax.set_aspect('equal');ax.invert_yaxis();ax.set_xlabel('World easting offset (m)');ax.set_ylabel('World southward offset (m; north up)')
 paint(axes[0],missing,'#d63c30');paint(axes[1],excess,'#ff9c24');axes[0].set_title('Missing source projection within CSDI target (red)');axes[1].set_title('Original source projection outside target (orange)');fig.suptitle('Fleur Pavilia original podium: no source/target edits or registration credit');fig.tight_layout();DOC.mkdir();fig.savefig(DOC/'podium-complete-projection-2100x1350.png');plt.close(fig)
 result=dict(uids=['landsd/23296:0','landsd/269972:0'],sourceSHA256=SHA,completeOriginalFaces=len(tri),sourceProjectionM2=projection.area,targetM2=target.area,missingM2=missing.area,excessM2=excess.area,missingComponents=missing_rows,interiorMissingM2=sum(r['areaM2']for r in missing_rows if not r['touchesTargetBoundary']),boundaryConnectedMissingM2=sum(r['areaM2']for r in missing_rows if r['touchesTargetBoundary']),primaryCaptures=captures,primaryDesignContextURL=architect,primaryDesignContext='Architect describes an open central courtyard in the podium and a multi-storey entrance. This is contextual design evidence, not surveyed registration of missing areas or ownership boundaries.',sourceGeometryChanges=0,sourceIdentityAccepted=False,physicalAccepted=False,qualification='Complete pinned original projection and unchanged CSDI target geometry. All3657source facets supplied; zero-XZ-area facets add no area. Missing-area topology measured without buffers/repairs. Primary marketing/project images are not survey control. Original identity/foreign-overlap, ground, runtime and approval failures remain; do not infer acceptance merely from open-courtyard design context.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('fleur_projection_primary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-fleur-podium-projection-and-primary-context-no-approval',refs,result);print({k:result[k]for k in['missingM2','excessM2','interiorMissingM2','boundaryConnectedMissingM2']},flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('fleur-source-projection-context-'+str(uuid.uuid4()),['building:landsd/23296:0','building:landsd/269972:0'],batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
