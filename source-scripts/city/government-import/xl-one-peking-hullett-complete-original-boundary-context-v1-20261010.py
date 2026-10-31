"""Read-only complete original surface context; no identity/ownership credit."""
import importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010';DOC=BASE/BATCH
INPUT=HERE/'local/government-xl-terrain-recovery-one-peking-original-pair-current-physical-v1-20261010/frozen-inputs/check-selection.json.gz'
OWN='landsd/233985:0';FOREIGN='landsd/73140:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not DOC.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';raw_manifest=manifest.read_bytes();start=digest(raw_manifest)
 current=json.loads(raw_manifest);selection=read(INPUT)
 source_rows=selection['rows'];assert {r['uid'] for r in source_rows}=={OWN,'landsd/240487:0'}
 matches=[]
 for u in current['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/u
  for e in read(cat)['models']:
   if e['uid']==FOREIGN:matches.append((cat,e))
 assert len(matches)==1
 cat,e=matches[0];assert e['sha256']=='de03f5a51ec4b294a3e5c7d3e924324dbc21709f648f33c7d69254e19f484bc1'
 foreign_asset=cat.parent/e['asset'];foreign_raw=foreign_asset.read_bytes();assert digest(foreign_raw)==e['sha256']
 sources=[];assets=[];triangles={}
 for r in source_rows:
  asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']
  tri=decode_original_world_triangles(raw);assert len(tri)==r['triangles']
  triangles[r['uid']]=tri;assets.append(asset);sources.append(dict(uid=r['uid'],source=ref(asset),completeFaces=len(tri),worldTrianglesSHA256=digest(tri.tobytes()),metadata=r))
 foreign=decode_original_world_triangles(foreign_raw);assert len(foreign)==e['triangles']==32635
 triangles[FOREIGN]=foreign;assets.append(foreign_asset);sources.append(dict(uid=FOREIGN,source=ref(foreign_asset),catalogue=ref(cat),entry=e,completeFaces=len(foreign),worldTrianglesSHA256=digest(foreign.tobytes())))
 own=triangles[OWN];bounds=[float(own[:,:,0].min()),float(own[:,:,2].min()),float(own[:,:,0].max()),float(own[:,:,2].max())]
 final=module('one_peking_all_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);by={f['uid']:(f,p,t) for f,p,t in forms}
 assert OWN in by and FOREIGN in by and len(by)==len(forms)
 target=by[OWN][1];other=by[FOREIGN][1]
 poly=shapely.polygons(own[:,:,[0,2]]);projection=shapely.union_all(poly[shapely.area(poly)>0]);excess=projection.difference(target).intersection(other)
 ids=[];records=[]
 for i,p in enumerate(poly):
  affected=p.difference(target).intersection(other)
  if affected.area<=0:continue
  ids.append(i);t=own[i];n=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(n))
  records.append(dict(sourceFace=i,completeLiteralTriangle=t.tolist(),normal=(n/length).tolist() if length else [0,0,0],sourceYRange=[float(t[:,1].min()),float(t[:,1].max())],positiveExcessAreaM2=float(affected.area),excessWKT=shapely.to_wkt(affected,rounding_precision=-1)))
 assert ids
 # Every full foreign face is eligible; no coarse prism or distance exemption.
 contacts=exact_component_contacts(own,ids,foreign,list(range(len(foreign))))
 fpoly=shapely.polygons(foreign[:,:,[0,2]]);fprojection=shapely.union_all(fpoly[shapely.area(fpoly)>0])
 complete_overlap=projection.difference(target).intersection(fprojection)
 payload=dict(ownUID=OWN,foreignUID=FOREIGN,sources=sources,capturedManifestSHA256=start,historicalInputManifestSHA256=selection['manifestSHA256'],completeCurrentForms=[dict(building=f,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes())) for f,p,t in forms],rawCurrentForeignExcessM2=float(excess.area),completeOriginalForeignProjectedExcessM2=float(complete_overlap.area),affectedSourceFaces=records,completeOriginalForeignSurfaceContacts=contacts,ownAndForeignPrimaryCurrentFootprintIntersectionM2=float(target.intersection(other).area),ownAndForeignPrimaryCurrentSharedBoundaryM=float(target.boundary.intersection(other.boundary).length),sourceGeometryChanges=0,ownershipAccepted=False,physicalSupportAccepted=False,identityAccepted=False,publication=False,qualification='Complete original source comparison only. Current/projected overlap and exact contact are diagnostics, not property ownership, common permit, collision, support or acceptance. Installed foreign source remains unchanged and independently checked.')
 save(DOC/'captured-manifest.json',current);save(DOC/'diagnostic.json.gz',payload)
 assert digest(manifest.read_bytes())==start
 refs=[Path(__file__),INPUT,DOC/'captured-manifest.json',cat,*assets,HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']
 refs += [ROOT/'3d-viewer'/t for f,p,t in forms]
 module('one_peking_context_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-one-peking-hullett-surface-boundary-diagnostic-v1',sorted(set(refs)),dict(uids=[r['uid'] for r in sources],capturedManifestSHA256=start,completeSourceFaceCounts={r['uid']:r['completeFaces'] for r in sources},rawCurrentForeignExcessM2=payload['rawCurrentForeignExcessM2'],completeOriginalForeignProjectedExcessM2=payload['completeOriginalForeignProjectedExcessM2'],affectedOriginalFaces=len(ids),exactPositiveSurfaceContacts=sum(x['dimension']>0 for x in contacts['contacts']),sourceGeometryChanges=0,identityAccepted=False,fullAcceptance=False,publication=False))
 print(json.dumps(dict(affectedFaces=len(ids),rawForeignExcessM2=payload['rawCurrentForeignExcessM2'],fullForeignOriginalOverlapM2=payload['completeOriginalForeignProjectedExcessM2'],positiveContacts=sum(x['dimension']>0 for x in contacts['contacts']))),flush=True)
if __name__=='__main__':main()
