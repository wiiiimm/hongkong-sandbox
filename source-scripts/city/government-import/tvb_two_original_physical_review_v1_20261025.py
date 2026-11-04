"""Bounded original TVB assembly review for private preview; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from tvb_two_original_spatial_wall_context_v1_20261025 import SOURCES,RUNTIME,ATTRS
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tvb-two-original-physical-review-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'tvb_two_original_spatial_wall_context_v1_20261025.py'];pins={}
 def take(n,name='summary.json'):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/name;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(RUNTIME,'selection.json.gz');rows={r['uid']:r for r in selection['rows']}
 assert {u:r['sourceSHA256']for u,r in rows.items()}==SOURCES
 assert {u:r['triangles']for u,r in rows.items()}=={'landsd/9778:0':11081,'landsd/132578:0':116}
 helper=module('tvb_review_canonical',HERE/'xl-next-support-recovery-20261005.py');refs.append(HERE/'xl-next-support-recovery-20261005.py')
 forms={};identities={}
 for u,r in rows.items():
  f=forms[u]=r['source']['building'];tile=ROOT/'3d-viewer'/r['source']['tile'];refs.append(tile)
  assert next(x for x in read(tile)['buildings']if x['uid']==u)==f
  entry,_=helper.diagnostic_entry(r['native'],f);entry['asset']=r['candidate']['entry']['asset']
  assert entry==r['candidate']['entry'] and entry['rootTranslation']==[-834500,0,816500]
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[u];refs.append(asset)
  d=take('government-xl-tvb-two-original-current-identity-v1-20261025',u.split('/')[1]+'/identity.json')
  assert d['sourceSHA256']==SOURCES[u] and d['originalOwnership']['sourceGraphVerified'] and d['exactCurrentComponentRoute']['qualified'] and d['freshCurrentIdentity']['exactObjectAndCSUID']
  assert set(d['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','original-source-does-not-cover-whole-georef-cell'}
  identities[u]=d
 assert {f['parent']for f in forms.values()}=={'way/186639172'} and len({f['name']for f in forms.values()})==1
 primary='government-xl-tvb-two-original-primary-records-v1-20261025';p=take(primary);assert p['footprints']==2 and not p['missingRequestedCSUIDs']
 official={r['attributes']['BuildingCSUID']:r['attributes']for r in take(primary,'footprints.json')['features']}
 for f in forms.values():
  r=official[f['buildingCSUID']];assert r['Status']=='Active' and r['BuildingBlockType']==f['structureType'] and r['BaseHeight']==f['base'] and abs(r['TopHeight']-f['base']-f['height'])<1e-8
 context=take('government-xl-tvb-two-original-identity-context-v1-20261025');assert context['requiredOriginalAssembly']==SOURCES
 assert all(r['completeAssemblyTargetCoverage']>=.95 and r['completeAssemblyWholeCellCovered']for r in context['rows'])
 spatial=take('government-xl-tvb-two-original-spatial-wall-context-v1-20261025');assert spatial['sourceSHA256ByUid']==SOURCES
 assert len(spatial['compoundSpatialMeasures'])==len(spatial['wallContext'])==4
 assert all(r['compoundTargetCoverage']>=.95 and r['maximumExtentM']<=10 and r['unrelatedExcessM2']<=1 for r in spatial['compoundSpatialMeasures'])
 assert all(r['face']==60 and r['absNormalYRatio']==0 and r['finitePaths']==2 and r['pathsEntirelyOnFace60'] and r['rawDirectRimFailuresPreserved']for r in spatial['wallContext'])
 take(ATTRS,'attributes.json.gz')
 for number,count in [('9778',11081),('132578',116)]:
  f=take(f'government-xl-tvb{number}-private-foundations-v2-20261025')
  assert len(f['rows'])==4 and all(r['triangles']==r['completeTerrainTriangles']==count and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['minimumGapM']>=-.5 for r in f['rows'])
  c=take(f'government-xl-tvb{number}-complete-ground-clearance-v1-20261025');assert len(c['rows'])==4 and all(not r['exactAffectedFaces']for r in c['rows'])
 rims=take('government-xl-tvb9778-private-exact-rims-v2-20261025');assert len(rims['rows'])==4 and all(r['passed']for r in rims['rows'])
 diagnostic=take('government-xl-tvb132578-four-world-rim-diagnostic-v1-20261025');assert len(diagnostic['rows'])==4
 for r in diagnostic['rows']:
  assert r['failedSamples']==2 and r['predicates']==dict(hasLowSamples=True,completeSampleClearance=True,minimumGradeContact=True,maximumLowRimGap=False)
 paths=take('government-xl-tvb132578-ground-root-paths-v1-20261025');assert paths['allTargetsHaveFiniteEndpointBoundedPaths']
 assert all(r['strictGroundRoots']==97 and r['targets']==r['finitePaths']==r['endpointCeilingPassed']==2 for r in paths['rows'])
 continuous=take('government-xl-tvb-two-original-private-continuous-v2-20261025');assert all(not r['continuousAffectedFaces'] and not r['wholeSourceUncoveredFaces']for r in continuous['rows'])
 coverage=take('government-xl-tvb-two-original-private-exact-coverage-v2-20261025');assert all(not r['stillUncoveredFaces']for r in coverage['rows'])
 pair=take('government-xl-tvb-two-original-complete-pair-context-v1-20261025');assert pair['sourceSHA256ByUid']==SOURCES and len(pair['rows'])==4 and all(r['positiveSurfaceContacts']==101 for r in pair['rows'])
 foreign=take('government-xl-tvb-two-original-current-foreign-contacts-v1-20261025');assert foreign['foreignPairs']==4
 assert all(not m['allFiniteContactPairs'] and m['projectedOverlapAreaM2']==0 for r in foreign['rows']if r['foreignUid']=='way/186639167:0'for m in r['modes'])
 scope='government-xl-tvb-two-original-bounded-grade-scope-v1-20261025';s=take(scope,'scope.json');obligations={f['uid']:f for f in take(scope,'form-obligations.json.gz')}
 assert len(obligations)==s['intersectingForms']==8 and s['currentNativeActors']==6924 and not s['touchingNativeUids'] and not s['terrainContacts'] and s['positiveAreaTerrainOverlaps']==0
 assert all(obligations[u]==f for u,f in forms.items()) and 'way/186639167:0'in obligations
 neighbours=take('government-xl-tvb-two-original-bounded-grade-form-checks-v1-20261025');assert neighbours['forms']==8 and neighbours['flagged']==[] and neighbours['ordinaryFlagged']==0
 images=[]
 for batch,names in [('government-xl-tvb-two-original-source-views-v1-20261025',['complete-original-assembly.png']),('government-xl-tvb-two-original-identity-context-v1-20261025',['source-record-context.png'])]:
  take(batch)
  for name in names:
   p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 resources={('building:'if u.startswith('landsd/')else'source-form:')+u for u in obligations}|{'terrain:city/data/terrain.json'}
 proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid={},retainedNativeUids=[],retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],reviewer='ROOT',identityAccepted=True,identityProof=proof,identityProofByUid={u:proof for u in SOURCES},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=8,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),leaseResources=sorted(resources),imagesActuallyViewed=images,rawIdentity=identities,compoundSpatialMeasures=spatial['compoundSpatialMeasures'],rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,terrainEdits=True,visualAcceptance=False,installationApproved=False,publication=False,interpretation=[
 'Exact current object/CSUID, unique component route and original source graph identify both originals at this named transmitter site. The original mast is routed to the Podium record and the low perimeter/plinth to the Tower record; these semantic height labels do not authorize modifying either original. ROOT inspected the complete source assembly and record projections. Both required source hashes jointly cover each complete GeoRef cell and pass existing compound spatial limits. Raw individual coverage/cell failures remain. Only one current structure relation is available; complete two-CSUID permit membership is not claimed.',
 'Both sources retain fixed1x/root/source placement and every original face. Authenticated bounded original-TIN grade passes full-source four-world foundation/continuous/finite all-drawn-ground checks and all8 surrounding forms. No whole/upward whole source burial occurs. Unrelated way186639167 is retained and has zero finite source contacts or projected overlap. No current native actor or patch contact is involved.',
 'Smaller source has97 strict low ground roots in every representation. Its only two direct-rim failures are on exactly vertical original face60: bottom-edge gaps3.1472735549m and1.5674163908m over a terrain notch. Both are on the same unchanged authored wall with exact finite paths entirely within that face to its grounded lower vertex, with zero rise/residual. ROOT accepts this bounded original wall span as source-role context; direct-rim failures remain verbatim. This does not change the1m direct-rim limit or create an engineering, arbitrary floating-face or terrain-burial exemption.',
 'The original pair has101 finite interfaces in each stream; this authored same-site contact is retained rather than edited. Neither failed roof-support direction is credited as dependency. Each original has its own actual-TIN roots, so supportByUid is empty. Both source hashes are mandatory identity assembly members.',
 'Private preview only. Eight actual own-source desktop/mobile day/night exports, pick/collision/failure/retry and joint activation, then guarded publication and fresh live export inspection/full old assets/full521/globalBASIC readback remain mandatory.'
 ])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result)
 module('tvb_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-tvb-two-original-physical-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
