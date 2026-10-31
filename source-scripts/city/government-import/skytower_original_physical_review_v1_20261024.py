"""Bind the exact unchanged Skytower to the original Elements/Suntower assembly."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from skytower_original_catalogue_scope_v1_20261024 import UID,PARENT,NEIGHBOUR,SOURCES,SUPPORTS,RETAINED,verify_native_scope
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-skytower-original-physical-review-v1-20261024';P='government-xl-next-six-after-plaza-'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'skytower_original_catalogue_scope_v1_20261024.py'];pins={}
 def take(n,f='summary.json'):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(P+'normalized-runtime-v1-20261024','selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID);assert source['sourceSHA256']==SOURCES[UID]and source['triangles']==10887
 asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[UID];refs.append(asset)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);current={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:assert e['uid']not in current;current[e['uid']]=e
 scope=take(P+'current-scope-v1-20261024');native=take(P+'current-native-contacts-v1-20261024');assert verify_native_scope(scope,native,current)
 identity=take('government-xl-skytower-connected-original-identity-v1-20261024','identity.json');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES and len(identity['rows'])==4
 assert all(r['ownTargetCoverage']>=.95 and r['extentFromConnectedAssemblyM']<=10 and r['sourceProjectionOutsideAssemblyM2']<=1 and r['allPositiveAreaSuntowerInterfacesHaveExactlyOppositeNormals']for r in identity['rows'])
 checks=take('government-xl-skytower-elements-current-support-v1-20261024');assert checks['supportedUid']==UID and checks['installedSupportUid']==PARENT and len(checks['rows'])==4
 for r in checks['rows']:
  assert r['unresolved']==r['finitePaths']==10 and r['support']['strictContacts']==251
  f=r['compoundFoundation'];assert f['triangles']==f['completeTerrainTriangles']==10887 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 ground=take('government-xl-skytower-complete-actual-ground-clearance-v1-20261024');assert len(ground['rows'])==4
 assert all(r['completeSourceFaces']==10887 and r['noAffectedFaces']and not r['exactAffectedFaces']for r in ground['rows'])
 compound=take('government-xl-skytower-elements-complete-compound-clearance-v1-20261024');assert len(compound['rows'])==4
 for r in compound['rows']:assert r['completeSourceFaces']==10887 and r['exactAffectedFaces']==[8104,8105,8501,8663,8664,9287]and r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']and r['compoundCapPathsPassed']and not r['negativeNonWallFaces']
 forms={r['building']['uid']:r['building']for r in take(P+'current-scope-v1-20261024','204146:0-forms.json.gz')};assert set(forms)=={UID,*RETAINED}
 images=[]
 for n,filenames in [('government-xl-skytower-current-source-context-v1-20261024',['whole-source-plan.png','whole-source-perspectives.png']),('government-xl-skytower-elements-six-negative-wall-views-v1-20261024',['named-faces-current-ground.png'])]:
  take(n)
  for filename in filenames:
   p=BASE/n/filename;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 result=dict(uids=[UID],reviewer='ROOT',sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,requiredRetainedOriginalSources={u:current[u]['sha256']for u in RETAINED},supportByUid=SUPPORTS,nativeSupportByUid=SUPPORTS,retainedNativeUids=sorted(RETAINED),identityAccepted=True,identityProof=identity['identityProof'],identityProofByUid={UID:identity['identityProof']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=3,leaseResources=sorted('building:'+u for u in forms),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),terrainEdits=False,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=False,installationApproved=False,publication=False,imagesActuallyViewed=images,rawSupportChecks=checks['rows'],rawCompoundClearance=compound['rows'],interpretation=[
 'Only the exact10887face original Skytower is new. Elements203738faces and Suntower12129faces retain their exact installed bytes, transformations, approval flags and dependencies. Full current6907actor bounds find these two native neighbours only; current complete source-form scope has exactlythese3 actors. There is no external BASIC actor or terrain edit.',
 'The source-specific connected-family identity review preserves root/CSUID/ObjectID/current-route/complete-cell evidence,98.889percent own coverage and the raw individual10.4517m extent hold. Its complete four-stream projection is inside the surveyed union of its measured original Elements support and adjoining original Suntower. All vertices beyond the individual10m limit belong to lower extensions below recorded base38.5m. Existing95percent/10m/1m2 bounds stay unchanged, with the exact three-source assembly pinned.',
 'All source faces have complete actual-ground and actual-ground-plus-original-Elements foundation coverage with zero whole or upward-whole burial in all4streams. Actual ground clearance has no negative face. The six negative compoundfaces8104,8105,8501,8663,8664,9287 are vertical lower walls crossing the original podium top, with exposed highest vertices and independently verified finite clear-cap paths. ROOT inspected the full two-angle source/podium/ground image. Preserve the raw minimum-.563381m; this is the exact original lower-wall/deck interface, not a horizontal-floor exemption or a changed global burial limit.',
 'The original Elements interface independently supplies251strict contacts. All10remaining vertical probes have finite original-surface paths in each stream; direct-probe failures remain archived. The new catalogue must retain the exact Elements UID/CSUID/SHA dependency. No source endpoint is raised or reconstructed.',
 'Every positive-area Skytower/Suntower interface has exactly opposite original-surface normals in all4streams. These are complementary adjoining original surfaces in the current same-parent assembly; this does not establish common property, structural engineering or zero volumeinterpenetration. All raw positive-area and line contacts remain, no existing native actor is removed, relabelled or given new dependencies. Desktop/mobile own-source, retained-source, picking/collision/failure/retry and live verification remain separate mandatory gates.' ])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result);module('skytower_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-skytower-original-retained-assembly-physical-review',refs,result)
if __name__=='__main__':main()
