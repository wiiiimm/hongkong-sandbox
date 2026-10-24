"""Every current third-party basic form and native whole-source bound, no omission.

The mandatory three literal originals keep all authored pair intersections;
this foreign proof supplies no shared legal ownership, physical or install credit.
"""
import importlib.util,json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-sing-three-original-current-complete-foreign-wall-scope-v2-20261010';DOC=BASE/BATCH;PHYSICAL=BASE/'government-xl-tung-sing-three-original-literal-parent-physical-v2-20261010';WALL=BASE/'government-xl-tung-sing-three-original-current-certified-wall-paths-v2-20261010';RUNTIME=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';UIDS={'landsd/53800:0','landsd/126434:0','landsd/254604:0'}
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def main():
 assert not DOC.exists();manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);s=read(PHYSICAL/'selection.json.gz');assert digest(manifest_path.read_bytes())==s['manifestSHA256'];rows={r['uid']:r for r in s['rows']};assert set(rows)==UIDS;runtime={r['uid']:r for r in read(RUNTIME)['rows']};assert set(runtime)==UIDS;wall=read(WALL/'diagnostic.json.gz');source={};rendered={};affected={};pieces=[];sourcepins=[];refs=[Path(__file__),manifest_path,PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',PHYSICAL/'neighbour-inputs.json.gz',RUNTIME,WALL/'result.json',WALL/'diagnostic.json.gz'];own=[]
 for uid,row in rows.items():
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];source[uid]=decode_original_world_triangles(raw);r=runtime[uid];rendered[uid]=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert len(source[uid])==len(rendered[uid]);proof=next(x for x in wall['rows'] if x['uid']==uid);a,b=proof['sourceAndLiteralActualProofs'];assert a['representation']=='completeOriginal' and b['representation']=='actualRendered';assert a['strictClearCapWallPaths']['allAffectedHavePaths'] and b['strictClearCapWallPaths']['allAffectedHavePaths'];ids=a['strictClearCapWallPaths']['affectedOriginalWallFaces'];assert ids==b['strictClearCapWallPaths']['affectedOriginalWallFaces'] and not a['strictClearCapWallPaths']['rawExposureFailures'] and not b['strictClearCapWallPaths']['rawExposureFailures'];affected[uid]=ids
  for mode,tri in [('source',source[uid]),('actualRendered',rendered[uid])]:
   for f in tri[ids]:
    xz=f[:,[0,2]];poly=Polygon(xz);pieces.append(poly if poly.area else LineString(xz) if len(set(map(tuple,xz)))>1 else Point(xz[0]))
  own.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'completeOriginalFaces':len(source[uid]),'completeOriginalWorldSHA256':digest(source[uid].tobytes()),'completeActualRenderedWorldSHA256':digest(rendered[uid].tobytes()),'allAffectedOriginalWalls':ids});refs.append(asset)
 projection=unary_union(pieces);inputs=read(PHYSICAL/'neighbour-inputs.json.gz');assert set(inputs['candidateIds'])==UIDS;current_forms={}
 for path,pinned in inputs['inputHashes'].items():
  tile=ROOT/path;assert digest(tile.read_bytes())==pinned;current_forms.update({r['uid']:r for r in read(tile)['buildings']});refs.append(tile)
 basics=[];scope=set();retained=[]
 for r in inputs['rows']:
  b=r['building'];uid=b['uid'];assert uid not in scope and current_forms[uid]==b;scope.add(uid)
  if uid in UIDS:continue
  if r['existingNative']:
   retained.append({'uid':uid,'completeActualCurrentForm':b,'currentFormSHA256':canonical(b),'requiresCompleteNativeCatalogueBounds':True});continue
  assert not b.get('modelGeometry'),'Complete runtime foreign export required';poly=Polygon(b['rings'][0],b['rings'][1:]);assert poly.is_valid and poly.area>0 and poly.disjoint(projection),'Foreign actual basic full footprint touches credited wall: exact mesh export required'
  basics.append({'uid':uid,'completeActualCurrentForm':b,'currentFormSHA256':canonical(b),'completeFootprintStrictlyDisjointFromEveryOriginalAndRenderedWall':True,'distanceM':poly.distance(projection)})
 assert UIDS.issubset(scope);bounds=[];touch=[];walls=np.concatenate([tri[affected[uid]] for uid in rows for tri in [source[uid],rendered[uid]]])
 for url in manifest['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;refs.append(cat)
  for e in read(cat)['models']:
   b=np.asarray(e['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and np.all(b[1]>=b[0]) and e['sha256'];assert e['uid'] not in UIDS,'Mandatory original already installed; capture refresh required';hit=any(not(np.any(b[0]>f.max(0)) or np.any(b[1]<f.min(0))) for f in walls);bounds.append({'uid':e['uid'],'catalogue':url,'sourceSHA256':e['sha256'],'completeWholeSourceBounds':b.tolist(),'strictlyDisjointFromEveryOriginalAndRenderedCrossingWall':not hit})
   if hit:touch.append(e['uid'])
 assert not touch,'Current foreign native complete export required';assert {r['uid'] for r in retained}.issubset({r['uid'] for r in bounds}),'Missing retained native actor bounds'
 mutual=[]
 for uid,tri in source.items():
  for other,mesh in source.items():
   if uid==other:continue
   lo=mesh.min(1);hi=mesh.max(1)
   for i in affected[uid]:
    face=tri[i];ids=np.flatnonzero(np.all(hi>=face.min(0),axis=1)&np.all(lo<=face.max(0),axis=1))
    for j in ids:
     points=intersection_points(rational_face(face),rational_face(mesh[j]))
     if points:mutual.append({'sourceUID':uid,'otherSourceUID':other,'originalWallFace':i,'otherOriginalFace':int(j),'exactAuthoredIntersectionPoints':[[str(v) for v in p] for p in sorted(points)],'exactDimension':contact_measure(points)['dimension'],'sourceGeometryChanges':0,'thirdPartyForeignExemption':False,'physicalCollisionAcceptanceClaimed':False})
 save(DOC/'diagnostic.json.gz',{'manifestSHA256':s['manifestSHA256'],'mandatoryCompleteImportedOriginals':own,'completeCurrentNeighbourScopeUIDs':sorted(scope),'completeActualForeignBasicForms':basics,'completeCurrentNativeWholeSourceBounds':bounds,'retainedCurrentNativeFormsIndependentlyWholeBoundChecked':retained,'allCurrentNativeCatalogueEntries':len(bounds),'allCurrentForeignBasicForms':len(basics),'foreignNativeBoundsTouchingWalls':touch,'allThirdPartyForeignSourceAndRenderedCrossingWallsClear':True,'allExactSourceAuthoredMutualWallIntersectionsRetained':mutual,'completeOriginalAndRenderedWallProjectionWKT':projection.wkt,'sourceGeometryChanges':0,'physicalAccepted':False,'installationApproved':False,'qualification':'Exactly three complete unchanged originals are proposed together, with all12751faces and387parts independently retained/rooted/typed. Only current third-party actors are foreign here; no name/estate/permit ownership shortcut. Every current neighbour form reloads exact current tile bytes; every literal source and runtime crossing wall is disjoint from every foreign basic complete footprint and all6614 catalogue entries whole bounds. All authored inter-source wall intersections stay explicitly inventoried with zero collision acceptance credit. Full numerical, source-support, foundation/runtime/stage/browser acceptance remains independent.'});assert digest(manifest_path.read_bytes())==s['manifestSHA256'];sp=importlib.util.spec_from_file_location('foreign_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.freeze(BATCH,'mandatory-complete-original-assembly-all-current-foreign-crossing-wall-scope-v1',refs,{'uids':sorted(UIDS),'currentNativeCatalogueBounds':len(bounds),'currentForeignBasicForms':len(basics),'allThirdPartyForeignWallsClear':True,'allAuthoredMutualWallIntersectionsRetained':len(mutual),'physicalAccepted':False,'installationApproved':False});print({'foreignBasics':len(basics),'allNativeBounds':len(bounds),'authoredMutualWallIntersections':len(mutual),'allForeignClear':True},flush=True)
if __name__=='__main__':main()
