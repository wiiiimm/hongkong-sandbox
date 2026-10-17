"""Locate actual installed original surfaces at four unresolved Langham contacts."""
import numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-four-contacts-installed-sources-v1-20261017';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-langham-current-support-v1-20261017'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 points=np.asarray([x['position']for x in r['interface']['unresolved']]);assert points.shape==(4,3);manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());refs=[Path(__file__),manifest,PRIOR/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];out=[];scanned=0
 for url in read(manifest)['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;data=read(cat);refs.append(cat)
  for e in data['models']:
   scanned+=1
   if e['uid']=='landsd/79318:0':continue
   bounds=e.get('worldBounds')
   if not bounds:continue
   lo,hi=np.asarray(bounds);near=((points[:,[0,2]]>=lo[[0,2]]-1)&(points[:,[0,2]]<=hi[[0,2]]+1)).all(1)
   if not near.any():continue
   asset=cat.parent/e['asset'];raw=asset.read_bytes();assert digest(raw)==e['sha256'];refs.append(asset);tri=decode_original_world_triangles(raw);polys=shapely.polygons(tri[:,:,[0,2]]);valid=np.flatnonzero(shapely.area(polys)>1e-10);tree=shapely.STRtree(polys[valid]);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);matches=[]
   for k,p in enumerate(points):
    ids=valid[tree.query(shapely.Point(p[[0,2]]),predicate='intersects')];hits=[]
    for i in ids:
     h=(np.dot(norm[i],tri[i,0])-norm[i,0]*p[0]-norm[i,2]*p[2])/norm[i,1];gap=float(p[1]-h);hits.append(dict(face=int(i),heightHKPD=float(h),gapM=gap,withinExistingContactBand=bool(-.1<=gap<=1)))
    matches.append(dict(point=k,allOriginalSurfaceHits=hits,withinBandFaces=[h['face']for h in hits if h['withinExistingContactBand']]))
   out.append(dict(uid=e['uid'],label=e.get('label'),sourceSHA256=e['sha256'],completeOriginalFaces=len(tri),matches=matches))
 assert digest(manifest.read_bytes())==start
 summary=[dict(point=i,possibleInstalledSupports=[dict(uid=x['uid'],faces=x['matches'][i]['withinBandFaces'])for x in out if x['matches'][i]['withinBandFaces']])for i in range(4)]
 save(DOC/'contacts.json',dict(points=points.tolist(),installedEntriesScanned=scanned,nominees=len(out),rows=out,summary=summary,qualification='Complete original vertical surfaces for current catalogue bounds nominees only. Not a support-interface certificate, new identity approval or permission to use unrelated geometry. All surface layers retained; original indexed faces unchanged.',installationApproved=False))
 job=module('langham_four_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-unresolved-langham-installed-original-surface-nominations-v1',refs,dict(uids=['landsd/79318:0'],summary=summary,nominees=len(out),fullAcceptance=False,nextStep='Validate any nominated actual support with identity and complete compound contact checks; if none exists, retain exact contact hold and investigate original source context.'))
 print(dict(jobId=job['jobId'],nominees=len(out),summary=summary),flush=True)
if __name__=='__main__':main()
