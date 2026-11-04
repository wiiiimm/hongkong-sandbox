"""Complete detached original component surface context; no support approval."""
import collections,importlib.util,json,re,uuid
from urllib.parse import urljoin,quote
from urllib.request import Request,urlopen
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-yoho-eight-detached-original-surface-context-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-yoho-eight-complete-original-component-graph-20261009/diagnostic.json.gz'
SOURCE=HERE/'local/government-xl-spatial-surface-roles-20261009/assets/fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08.glb.gz'
URL='https://www.general-aircon.com/en/about-us/past-project/detail/yoho-town'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def get(url):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r:return r.read(),dict(r.headers),r.status
def main():
 assert not (DOC/'result.json').exists() and not (DOC/'diagnostic.json.gz').exists();claim=reservations.claim('yoho-eight-surface-context-'+str(uuid.uuid4()),['building:landsd/146396:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  d=read(INPUT);assert digest(SOURCE.read_bytes())==d['sourceSHA256'];tri=decode_original_world_triangles(SOURCE.read_bytes());assert digest(tri.astype('<f8').tobytes())==d['completeWorldSHA256'];spec=importlib.util.spec_from_file_location('yoho_closest_original',HERE/'xl-popcorn-original-panel-distance-20261009.py');distmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(distmod)
  detached=[r for r in d['originalComponentOutcomes'] if not r['exactPositiveContactPathToOriginalPodium']];attached_ids=sorted(i for r in d['originalComponentOutcomes'] if r['exactPositiveContactPathToOriginalPodium'] for i in r['originalFaces']);attached=tri[attached_ids];rows=[]
  DOC.mkdir(parents=True,exist_ok=True)
  cache=DOC/'complete-original-nearest-vertices.json.gz'
  previous=read(cache) if cache.exists() else None
  if previous:
   assert previous['inputSHA256']==digest(INPUT.read_bytes()) and previous['sourceSHA256']==d['sourceSHA256'];rows=previous['rows']
  for r in ([] if previous else detached):
   ids=r['originalFaces'];vertices=np.unique(tri[ids].reshape(-1,3),axis=0);witness=[]
   for p in vertices:
    distances,points=distmod.closest(p,attached);k=int(np.argmin(distances));witness.append({'originalVertex':p.tolist(),'attachedOriginalFace':attached_ids[k],'nearestOriginalPoint':points[k].tolist(),'floatingDiagnosticDistanceM':float(distances[k])})
   rows.append({**r,'everyOriginalVertexNearestCompleteAttachedSource':witness,'minimumVertexDistanceM':min(w['floatingDiagnosticDistanceM'] for w in witness),'maximumVertexDistanceM':max(w['floatingDiagnosticDistanceM'] for w in witness),'vertexOnlyDiagnostic':True,'exactNoContactRetained':True,'supportAccepted':False})
  if not previous:save(cache,{'inputSHA256':digest(INPUT.read_bytes()),'sourceSHA256':d['sourceSHA256'],'rows':rows,'qualification':'Unfenced interrupted-stage computational cache; exact source and complete input must match. No support or continuous proximity credit.'})
  html,headers,status=get(URL);(DOC/'manufacturer-primary-page.html').write_bytes(html);records=[{'url':URL,'path':str((DOC/'manufacturer-primary-page.html').relative_to(ROOT)),'sha256':digest(html),'statusCode':status,'etag':headers.get('ETag'),'lastModified':headers.get('Last-Modified')}]
  image_urls=[]
  for tag in re.findall(r'<img\b[^>]*>',html.decode('utf-8'),re.I):
   if not re.search(r'yoho',tag,re.I):continue
   for match in re.finditer(r'(?:src|data-src)=["\']([^"\']+)["\']',tag,re.I):
    u=quote(urljoin(URL,match.group(1)),safe=':/?=&%')
    if u not in image_urls:image_urls.append(u)
  for k,u in enumerate(image_urls):
   content,h,status=get(u);ext='.png' if 'png' in h.get('Content-Type','') else '.jpg';p=DOC/('manufacturer-primary-image-'+str(k)+ext);p.write_bytes(content);records.append({'url':u,'path':str(p.relative_to(ROOT)),'sha256':digest(content),'statusCode':status,'etag':h.get('ETag'),'lastModified':h.get('Last-Modified')})
  save(DOC/'primary-requests.json',{'requests':records,'qualification':'Public manufacturer first-party project description and images; project-context only, not georeferenced Tower8/component identity, not surveyed mounting geometry. Manufacturer unit-count statement differs from developer records and is not used for identity.'})
  import matplotlib;matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d.art3d import Poly3DCollection
  lo,hi=tri.min(axis=1),tri.max(axis=1);plots=[]
  for count in sorted(set(len(r['originalFaces']) for r in detached)):
   r=next(r for r in rows if len(r['originalFaces'])==count);part=tri[r['originalFaces']];a,b=part.min(axis=(0,1)),part.max(axis=(0,1));centre=(a+b)/2;radius=max(1.2,float(np.max(b-a))*.8)
   neighbours=[i for i in attached_ids if np.all(hi[i]>=centre-radius) and np.all(lo[i]<=centre+radius)];fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(tri[neighbours],facecolor='#889ba9',edgecolor='#4c6575',linewidth=.25,alpha=.3));ax.add_collection3d(Poly3DCollection(part,facecolor='#d06b34',edgecolor='#822a0b',linewidth=.8,alpha=.9));ax.set(xlim=(centre[0]-radius,centre[0]+radius),ylim=(centre[2]-radius,centre[2]+radius),zlim=(centre[1]-radius,centre[1]+radius))
   # Matplotlib axis order is X/Y/Z, so swap the exact source world Y and Z only for display.
   ax.cla();other=tri[neighbours][:,:,[0,2,1]];view=part[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(other,facecolor='#889ba9',edgecolor='#4c6575',linewidth=.25,alpha=.3));ax.add_collection3d(Poly3DCollection(view,facecolor='#d06b34',edgecolor='#822a0b',linewidth=.8,alpha=.9));ax.set(xlim=(centre[0]-radius,centre[0]+radius),ylim=(centre[2]-radius,centre[2]+radius),zlim=(centre[1]-radius,centre[1]+radius));ax.set_box_aspect((1,1,1));ax.view_init(elev=20,azim=35);ax.set_xlabel('Original world X');ax.set_ylabel('Original world Z');ax.set_zlabel('Original HKPD Y');ax.set_title(f'Yoho Tower8: complete original {count}-face detached component {r["component"]}\nOrange component; blue exact nearby attached source surfaces; diagnostic crop');p=DOC/f'original-{count}-face-component-context-2400x1800.png';fig.savefig(p,dpi=200);plt.close(fig);plots.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes()),'completeDetachedOriginalFaces':r['originalFaces'],'nearbyOriginalAttachedFacesShown':neighbours,'sourceGeometryChanges':0})
  result={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'completeWorldSHA256':d['completeWorldSHA256'],'completeOriginalFaceCount':len(tri),'completeDetachedComponents':rows,'completeAttachedOriginalFaces':attached_ids,'originalSourceHierarchySemantics':'Single provider named root B217913364901063C0, one unnamed mesh with default material and vertex colours; no component-specific authored names or structural labels.','primaryManufacturerContext':URL,'primaryImages':records,'plots':plots,'evidenceRefs':[ref(p) for p in [Path(__file__),INPUT,SOURCE,HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-popcorn-original-panel-distance-20261009.py']],'supportAccepted':False,'identityAccepted':False,'publication':False,'installationApproved':False,'sourceGeometryChanges':0,'qualification':'Every detached original vertex measured against all exact attached original source surfaces. Floating closest-point diagnostics cannot overturn exact no-contact proofs, certify continuous surface proximity, identify a mounting bracket, or confer physical support. Public primary imagery is contextual unless independently registered; no component function is presumed from triangle count.'};save(DOC/'diagnostic.json.gz',result);summary={'detachedComponents':len(rows),'maximumVertexDistanceM':max(r['maximumVertexDistanceM'] for r in rows),'byFaceCount':{n:{'components':len([r for r in rows if len(r['originalFaces'])==n]),'minDistanceM':min(r['minimumVertexDistanceM'] for r in rows if len(r['originalFaces'])==n),'maxDistanceM':max(r['maximumVertexDistanceM'] for r in rows if len(r['originalFaces'])==n)} for n in sorted(set(len(r['originalFaces']) for r in rows))},'primaryImages':len(records)-1,'supportAccepted':False};save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
