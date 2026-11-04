"""DRAFT current native complex + surviving BASIC finite context; no qualification."""
import json,subprocess,numpy as np
from pathlib import Path
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
BASE=ROOT/'docs/astra-city/government-import';SCRIPTS=ROOT/'source-scripts/city/government-import'
PROPOSAL=BASE/'government-xl-polyu-sports305582-current-surviving-neighbour-geometry-proposal-v1-20261012'
DOC=BASE/'government-xl-polyu-sports305582-current-surviving-neighbour-finite-region-context-v2-20261012'
CAP=BASE/'government-xl-polyu-sports305582-current-surviving-neighbour-geometry-context-v1-20261012'
CONTEXT=BASE/'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012/context.json'
EXPECTED='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
JS=SCRIPTS/'polyu_sports305582_actual_surviving_neighbour_attributes_draft_v1_20261012.mjs'
UID='landsd/305582:0';NATIVE='landsd/305793:0';BASIC=['landsd/72322:0','landsd/258852:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins=read(PROPOSAL/'input-pins.json')['refs']
 def fence():
  for e in pins:assert ref(ROOT/e['path'])==e
 fence();context=read(CONTEXT);assert context['sourceOnly']and context['completeOriginalFaces']==10536 and not context['identityAccepted'];source=ROOT/context['source']['path'];t=decode_original_world_triangles(source.read_bytes());assert t.shape==(10536,3,3)and digest(t.astype('<f8').tobytes())==context['completeOriginalWorldSHA256'];labels={f:i for i,b in enumerate(context['originalTopology']['sharedEdgeConnectedComponents'])for f in b}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==EXPECTED;m=read(manifest);cats=[];entries={};entrypaths={}
 for url in m['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cats.append(ref(p))
  for entry in read(p)['models']:assert entry['uid']not in entries;entries[entry['uid']]=entry;entrypaths[entry['uid']]=p.parent/entry['asset']
 assert len(entries)==6649 and NATIVE in entries and all(u not in entries for u in BASIC);e=entries[NATIVE];assert e['sha256']=='c45253aeb258f6ffa8e56a069a7ed03e2ecf153a75ad0435370a008e525703f5'and e['triangles']==59527 and e['buildingCSUID']=='3655618355P20060311';assert 'landsd/305600:0'in e['suppressesBuildingUids'];assert all(u not in n.get('suppressesBuildingUids',[])for u in BASIC for n in entries.values())
 forms={};tiles={}
 # Exact two historical relevant cells cover all four named forms; no derived BASIC approximation.
 for tile in ['city/data/tiles/1_-1.json','city/data/tiles/1_-2.json']:
  p=ROOT/'3d-viewer'/tile;tiles[tile]=ref(p)
  for f in read(p)['buildings']:
   if f['uid']in forms:assert forms[f['uid']][0]==f
   forms[f['uid']]=(f,tile)
 assert all(u in forms for u in [UID,NATIVE,*BASIC,'landsd/305600:0']);assert forms[NATIVE][0]['buildingCSUID']==e['buildingCSUID']
 allrefs=pins+cats+list(tiles.values())+[ref(entrypaths[NATIVE])];assert ref(entrypaths[NATIVE])['sha256']==e['sha256'];DOC.mkdir()
 input=dict(rows=[dict(uid=NATIVE,entry=e,building=forms[NATIVE][0],path=str(entrypaths[NATIVE].relative_to(ROOT)),role='installed-native-context')],nativeContextRows=[],basicContextRows=[dict(building=forms[u][0],tile=forms[u][1],tileSHA256=tiles[forms[u][1]]['sha256'])for u in BASIC],completeCurrentForms=[f for f,_ in forms.values()],expectedNativeCount=6649,currentManifest=ref(manifest),currentCatalogueRefs=cats,evidenceRefs=allrefs)
 assert read(CAP/'current-neighbour-input.json.gz')==input;assert ref(CAP/'actual-surviving-neighbour-attributes.json.gz')['sha256']=='9a68a4719cd2b8d3c5ed04d6afbe31fbf27014187256731d1b788ac645f99210';actual=read(CAP/'actual-surviving-neighbour-attributes.json.gz');audit=read(PROPOSAL/'actual-v1-resource-failure-terminal-release-audit.json');assert audit['exitCode']==1 and audit['actualNeighbourCaptureCompleted']and not audit['numericalContactResultExists']
 for p,h in actual['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 native=actual['nativeContextRows'][0];idx=np.asarray(native['completeOriginalIndex']).reshape(-1,3);worlds={k:np.asarray(native[v],float).reshape(-1,3)[idx]for k,v in [('nativeLiteral','completeLiteralWorldPosition'),('nativeLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('nativeBalancedF32','completeExplicitBalancedFloat32WorldPosition')]};original=decode_original_world_triangles(entrypaths[NATIVE].read_bytes());assert original.shape==(59527,3,3);worlds['nativeProviderOriginal']=original
 actors={NATIVE:worlds}
 for row in actual['basicContextRows']:actors[row['uid']]={'actualProductionBasicF32':np.asarray(row['position'],float).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)]}
 proofs={};bindings=[]
 for region in context['completeSavedFourForeignRegionAttribution']:
  from shapely.geometry import shape
  poly=shape(region['originalSavedPlanarOverlap']['geometry']);x0,z0,x1,z1=poly.bounds;actor=NATIVE if region['uid']=='landsd/305600:0'else region['uid'];assert actor in actors
  def selected(a):
   lo=a.min(1);hi=a.max(1);return np.flatnonzero((lo[:,0]<=x1)&(hi[:,0]>=x0)&(lo[:,2]<=z1)&(hi[:,2]>=z0)).tolist()
  sa=selected(t)
  for mode,w in actors[actor].items():
   assert np.isfinite(w).all();sb=selected(w);key=digest(t.astype('<f8').tobytes()+w.astype('<f8').tobytes()+json.dumps([sa,sb]).encode());bindings.append(dict(namedHistoricalRegion=region['uid'],actualSurvivingActor=actor,arithmetic=mode,wholeActorFaces=len(w),wholeActorWorldSHA256=digest(w.astype('<f8').tobytes()),proofKey=key))
   if key in proofs:continue
   # Existing complete closed3D broadphase retains point/touch candidates; unchanged1m ACTUAL tested-pair cap.
   contacts=exact_finite_contacts(t,sa,w,sb);out=[]
   for c in contacts['contacts']:
    a,b=rational_face(t[c['sourceFaceA']]),rational_face(w[c['sourceFaceB']]);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));cop=bool(any(na)and any(nb)and not any(cross(na,nb))and dot(na,sub(b[0],a[0]))==0);out.append(dict(**c,originalSourceBody=labels.get(c['sourceFaceA']),nonzeroExactCoplanarPlanes=cop))
   proofs[key]=dict(regionClosedXZBounds=[x0,z0,x1,z1],sourceWholeFacetIDs=sa,actorWholeFacetIDs=sb,contacts=out,finiteKernel=contacts,scope='Complete whole facets touching the named closed region AABB; contact may extend outside that box. Neither whole-actor collision clearance nor identity/mount/support qualification.')
 fence()
 for r in allrefs:assert ref(ROOT/r['path'])==r
 for p,h in actual['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 save(DOC/'diagnostic.json.gz',dict(uid=UID,sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,completeOriginalSourceFaces=10536,sourceWholeWorldSHA256=context['completeOriginalWorldSHA256'],originalSourceBodiesPreserved=21,zeroFacesPreserved=4,currentManifest=ref(manifest),currentNativeCount=6649,actualNativeComplexEntry=e,suppressedLeeSourceRemainsHistoricalContextOnly=True,survivingBasicUIDs=BASIC,bindings=bindings,distinctExactProofs=proofs,rawProjectionAndIdentityNegativesPreserved=context['originalHistoricalProjectionStatsRetained'],pointAndProperSurfaceCrossingsNotRootOrSolidCredit=True,evidenceRefs=allrefs+[ref(JS),ref(Path(__file__)),ref(CAP/'current-neighbour-input.json.gz'),ref(CAP/'actual-surviving-neighbour-attributes.json.gz'),ref(PROPOSAL/'actual-v1-resource-failure-terminal-release-audit.json'),ref(PROPOSAL/'FINITE_ONLY_V2_DIFF.patch'),ref(PROPOSAL/'METHOD-finite-only-v2.md')]))
 print(json.dumps(dict(bindings=len(bindings),proofs=len(proofs),sourceFaces=10536,nativeComplexFaces=59527,acceptance=False)),flush=True)
if __name__=='__main__':main()
