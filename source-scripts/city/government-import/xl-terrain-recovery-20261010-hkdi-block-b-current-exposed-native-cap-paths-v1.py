"""Source-only native carrier qualification for untouched HKDI Block B.

Complete original/native sources remain accounted; only carrier131/root144 may
bridge the ownedB paths. Every credited contact uses exact source AND literal
positive-dimensional intersections. All carrier cap facets must have complete
strict source/literal ground clearance. Old native128/131 clearance findings and
failed147/155 footings remain recorded without native reacceptance.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-hkdi-native-and-block-b-complete-original-support-v1';FINITE=BASE/'xl-terrain-recovery-20261010-hkdi-complete-conservative-clearance-v1';ROOTS=BASE/'government-xl-terrain-recovery-hkdi-current-native-literal-ground-roots-v3-20261010'
BATCH='government-xl-terrain-recovery-hkdi-block-b-current-exposed-native-cap-paths-v1-20261010';DOC=BASE/BATCH
UIDS=['landsd/22089:0','landsd/89613:0'];CARRIER=131;ANCHOR=144

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def receipt(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x
 return r

def recheck():
 for folder in [PHYS,GRAPH,FINITE,ROOTS]:receipt(folder)
 roots=read(ROOTS/'diagnostic.json.gz');assert roots['rootComponents']==[134,135,144,156] and roots['strictLiteralRenderedRoots']is True
 selected=read(PHYS/'selection.json.gz');g=read(GRAPH/'diagnostic.json.gz');complete=read(FINITE/'diagnostic.json.gz');runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath);pieces=[];literal=[];assets=[]
 for uid in UIDS:
  r=next(r for r in selected['rows']if r['uid']==uid);p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];assets.append(p);t=decode_original_world_triangles(raw);rt=next(r for r in runtime['rows']if r['uid']==uid);world=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];assert t.shape==world.shape;pieces.append(t);literal.append(world)
 tri=np.concatenate(pieces);actual=np.concatenate(literal);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];components=g['components'];assert len(components)==502
 owned={i for i,c in enumerate(components)if c['actorUID']==UIDS[1]};assert len(owned)==345 and components[CARRIER]['actorUID']==components[ANCHOR]['actorUID']==UIDS[0]
 allowed=owned|{CARRIER,ANCHOR};adj={i:set()for i in allowed};by_pair={}
 for c in g['contactWitnesses']:
  a,b=c['components'];assert a<b
  if a in allowed and b in allowed:adj[a].add(b);adj[b].add(a);by_pair[(a,b)]=c
 parents={ANCHOR:None};queue=[ANCHOR]
 while queue:
  a=queue.pop(0)
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;queue.append(b)
 assert set(parents)==allowed,'Every ownedB component must reach genuine root144 without any other native/source actor'
 nativefinite=next(r for r in complete['rows']if r['uid']==UIDS[0]);bfinite=next(r for r in complete['rows']if r['uid']==UIDS[1]);assert not bfinite['unprovedOriginalFaceBounds']and not bfinite['unprovedActualRenderedFaceBounds']
 paths=[];capfaces=set()
 for child,parent in sorted(parents.items()):
  if parent is None:continue
  c=by_pair[tuple(sorted([child,parent]))];faces=c['globalOriginalFaces'];first=intersection_points(rational_face(tri[faces[0]]),rational_face(tri[faces[1]]));second=intersection_points(rational_face(actual[faces[0]]),rational_face(actual[faces[1]]));assert len(first)>=2 and len(second)>=2,'A credited complete source/literal contact is not positive-dimensional'
  cap=None
  if CARRIER in c['components']:
   k=c['components'].index(CARRIER);i=faces[k];assert i in components[CARRIER]['globalOriginalFaces'];f=nativefinite['allFaces'][i];assert f['sourceFace']==i and f['completeOriginal']['existingOrdinaryClearanceBoundProved']is True and f['actualRendered']['existingOrdinaryClearanceBoundProved']is True
   for world in [tri,actual]:
    n=np.cross(world[i,1]-world[i,0],world[i,2]-world[i,0]);assert np.linalg.norm(n)>0 and n[1]/np.linalg.norm(n)>.15,'A carrier interface is not an authored upward cap'
   capfaces.add(i);cap=dict(sourceFace=i,completeSourceAndLiteralFacetProof=f)
  paths.append(dict(parent=parent,child=child,components=c['components'],globalOriginalFaces=faces,sourceIntersectionVertices=[[str(v)for v in p]for p in first],literalIntersectionVertices=[[str(v)for v in p]for p in second],completeStrictCarrierCap=cap))
 assert len(paths)==346 and capfaces=={2563,3869,3884,3885,3886,3887,3890,3892,3893}
 nativebad=nativefinite['unprovedOriginalFaceBounds'];old_components={i:sorted(set(c['globalOriginalFaces'])&set(nativebad))for i,c in enumerate(components)if c['actorUID']==UIDS[0]and set(c['globalOriginalFaces'])&set(nativebad)}
 refs=[ref(p)for p in [Path(__file__),runtimepath,PHYS/'selection.json.gz',GRAPH/'diagnostic.json.gz',FINITE/'diagnostic.json.gz',ROOTS/'diagnostic.json.gz',*[f/'result.json'for f in [PHYS,GRAPH,FINITE,ROOTS]],*assets,HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 return dict(contract='hkdi-ownedB-complete-source-literal-qualified-current-native-cap-path-diagnostic-v1',uids=UIDS,completeOriginalFaces=len(tri),completeOriginalParts=502,completeOwnedBParts=345,qualifiedGenuineRoot=ANCHOR,independentActualRoots=roots['rootComponents'],onlyCreditedCurrentNativeCarrier=CARRIER,native128NoBridgeCredit=True,uninstalledOriginalAExcluded=True,failedFootings147155NoRootOrBridgeCredit=True,completeQualifiedOwnedBPaths=paths,completeQualifiedCarrierCapFaces=sorted(capfaces),allOwnedBPartsQualified=True,rawWholeCollectionSupportAccepted=g['supportInterfaceAccepted'],rawWholeCollectionReasonsPreserved=g['reasons'],retainedNativeUnprovedOriginalFacesPreserved=nativebad,retainedNativeUnprovedComponentInventory=old_components,nativeReacceptance=False,sourceGeometryChanges=0,diagnosticOnly=True,fullAcceptance=False,publication=False,newlyInstalled=0,evidenceRefs=refs)

def main():
 assert not DOC.exists();r=recheck();save(DOC/'diagnostic.json.gz',r);s=importlib.util.spec_from_file_location('hkdi_cap_path_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);f.freeze(BATCH,'complete-source-and-literal-ownedB-qualified-exposed-current-native-cap-paths-v1',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=UIDS,completeOwnedBParts=345,allOwnedBPartsQualified=True,completeCarrierCapFaces=r['completeQualifiedCarrierCapFaces'],nativeReacceptance=False,diagnosticOnly=True,fullAcceptance=False));print(dict(all345OwnedBPartsQualified=True,sourceAndLiteralPaths=346,caps=r['completeQualifiedCarrierCapFaces']),flush=True)
if __name__=='__main__':main()
