"""Explicit terrain-only proposal: restore complete actual parent facets for Villa.

Whole parent facets are copied literally. Changed native proposal fragments are
clipped on their existing planes. Tiny real source/foreign overlap is retained
in the record. No source-model edits, disjointness claim or physical acceptance.
"""
import copy,importlib.util,json,uuid
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as patch_helper
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-no1-garden-complete-current-physical-v3-20261010';BATCH='xl-terrain-recovery-20261010-no1-garden-literal-villa-parent-proposal-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
BEFORE=HERE/'local/xl-terrain-recovery-20261010-no1-garden-current-villa-before-facets-v1/diagnostic.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(PHYS/'terrain-candidates.json')[0];raw=(ROOT/old['path']).read_bytes();assert digest(raw)==old['sha256'];original=read(ROOT/old['path']);wrapper=copy.deepcopy(original);children=[p for p in wrapper['patches'] if p['meta'].get('targetUids')==['landsd/304714:0']];assert len(children)==1;child=children[0];oldfaces=patch_helper._faces(child);bounds=old['bounds'];extent=box(*bounds)
 before=read(BEFORE);assert before['bounds']==bounds
 for p,h in before['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,'Frozen literal before-state input differs:'+p
 beforefaces=np.asarray(before['completeBeforeDrawnFaces'],float);assert digest(beforefaces.tobytes())==before['completeBeforeDrawnFacesSHA256']
 form=next(r['building'] for r in read(PHYS/'neighbour-inputs.json.gz')['rows'] if r['building']['uid']=='landsd/237414:0');protected=Polygon(form['rings'][0],form['rings'][1:]).intersection(extent);assert protected.area>0
 selected=[i for i,f in enumerate(beforefaces) if Polygon(f[:,[0,2]]).intersection(protected).area>0];assert selected;retained=beforefaces[selected];polygons=[Polygon(f[:,[0,2]]) for f in retained];assert all(extent.covers(p) for p in polygons),'Complete literal parent facet would enlarge proposal bounds';region=shapely.union_all(polygons);assert region.covers(protected),'Complete existing parent facets must cover whole affected foreign footprint'
 row=read(PHYS/'selection.json.gz')['rows'][0];source=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());projection=shapely.union_all([Polygon(t[:,[0,2]]) for t in source if Polygon(t[:,[0,2]]).area>0]);overlap=projection.intersection(region);original_footprint_overlap=projection.intersection(Polygon(form['rings'][0],form['rings'][1:]))
 claim=reservations.claim('no1-parent-proposal-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  out=[];unchanged=[];clipped=[];removed=[]
  for i,(f,p) in enumerate(zip(oldfaces,shapely.polygons(oldfaces[:,:,[0,2]]))):
   if p.intersection(region).area==0:unchanged.append(i);out.append(f);continue
   remainder=p.difference(region);normal=np.cross(f[1]-f[0],f[2]-f[0]);assert normal[1]!=0;clipped.append(i)
   if remainder.is_empty:removed.append(i)
   for part in shapely.get_parts(remainder):
    if part.geom_type!='Polygon':continue
    for t in patch_helper._triangles(part):
     face=[]
     for x,z in list(t.exterior.coords)[:3]:y=f[0,1]-(normal[0]*(x-f[0,0])+normal[2]*(z-f[0,2]))/normal[1];face.append([x,float(y),z])
     out.append(face)
  native=np.asarray(out,dtype=np.float32).astype(float);new=np.concatenate([native,retained]);assert np.array_equal(new[-len(retained):],retained) and np.array_equal(new[-len(retained):].astype(np.float32).astype(float),retained),'All literal parent vertices must retain exact Float32 bits'
  child['nativeMesh']['position']=new.reshape(-1).tolist();child['nativeMesh']['index']=list(range(new.size//3));child['nativeMesh']['source']['explicitLiteralCurrentParentPreservation']=dict(parentFacetCount=len(retained),beforeDrawnFacetIds=selected,beforeStateRef=ref(BEFORE),sourceProjectionOverlapM2=float(overlap.area),disjointClaim=False,terrainProposalGeometryChanged=True)
  others=[p for p in original['patches'] if p['id']!=child['id']];assert [p for p in wrapper['patches'] if p['id']!=child['id']]==others
  asset=LOCAL/'terrain-central-no1-with-literal-villa-parent-facets-v1.json';save(asset,wrapper);candidate={**old,'path':ref(asset)['path'],'sha256':ref(asset)['sha256'],'triangles':sum(len(p['nativeMesh']['index'])//3 if p.get('nativeMesh') else (p['w']-1)*(p['h']-1)*2 for p in wrapper['patches'])};save(DOC/'terrain-candidates.json',[candidate])
  refs=[ref(p) for p in [Path(__file__),BEFORE,HERE/'xl-terrain-recovery-20261010-no1-garden-current-villa-before-facets-v1.mjs',PHYS/'terrain-candidates.json',PHYS/'selection.json.gz',PHYS/'neighbour-inputs.json.gz',ROOT/old['path'],asset,HERE/'native_patch_resolution.py']]
  result=dict(uids=[row['uid']],foreignUid=form['uid'],beforeStateManifestSHA256=before['historicalManifestSHA256'],beforeInputHashes=before['inputHashes'],originalTerrainCandidate=old,newTerrainCandidate=candidate,sourceSHA256=row['sourceSHA256'],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,completeLiteralCurrentParentFacetIds=selected,completeLiteralCurrentParentFacetsSHA256=digest(retained.tobytes()),originalNativeFaces=len(oldfaces),newNativeFaces=len(new),unchangedOriginalNativeFacetIds=unchanged,clippedOriginalNativeFacetIds=clipped,removedOriginalNativeFacetIds=removed,protectedForeignFootprintAreaWithinPatchM2=float(protected.area),restoredWholeParentFacetRegionM2=float(region.area),sourceProjectionOverlapWithWholeRestoredFacetsM2=float(overlap.area),sourceProjectionOverlapWithOriginalBasicFootprintM2=float(original_footprint_overlap.area),disjointClaim=False,otherNestedChildrenLiterallyUnchanged=True,wholeParentFacetGeometryCopiedLiterally=True,rawIdentityAndPhysicalFailuresRetained=True,currentRegionalRebindRequired=True,fullAcceptance=False,installationApproved=False,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('literal_parent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'explicit-no1-terrain-only-complete-literal-parent-facet-preservation-v1',[ROOT/r['path'] for r in refs],dict(uids=[row['uid']],foreignUid=form['uid'],terrainProposalGeometryChanged=True,sourceGeometryChanges=0,completeLiteralParentFacets=len(retained),sourceProjectionOverlapM2=float(overlap.area),disjointClaim=False,otherNestedChildrenLiterallyUnchanged=True,fullAcceptance=False));print(json.dumps(dict(literalFacets=len(retained),nativeFacesBefore=len(oldfaces),nativeFacesAfter=len(new),sourceOverlapM2=float(overlap.area),fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
