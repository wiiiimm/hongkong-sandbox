"""Review this exact five-original assembly; raw failures remain explicit."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-royal-green8-'
BATCH=P+'five-physical-review-v1-20261024'
SOURCES={
 'landsd/235598:0':'2626e9ce4e21cd23644be8256fd0f11e229e7c3bb327931744819a445cdcbf7f',
 'landsd/233190:0':'45c6e926c3241b7738a3cbb48cd4d0861425c2f30437674ce23188871478935d',
 'landsd/7521:0':'d718999c170ec88321782577234d28b9792709107748d63f4c0a81f24d54ffcf',
 'landsd/23480:0':'9e72ef7aba8d9b68bf8c52146eb2a0b8e7410ba37f6dd30f1d9d643862584661',
 'landsd/8602:0':'ced7fd953cb5a881544bc48ec63b31bc1a86554706d3b46d8617b0c8d65eb36d'}
SUPPORTS={u:'landsd/233190:0'for u in ['landsd/235598:0','landsd/7521:0']}
MODES={'original','literal','leftF32','balancedF32'}

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 def take(n,f='summary.json'):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def part(n,f='summary.json'):return take(P+n+'-20261024',f)
 selection=part('five-current-runtime-v1','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
 assert sum(r['triangles']for r in selection['rows'])==11857
 raw_identity=[];identity_proofs={}
 extras={r['uid']:r for r in part('two-adjoining-identity-context-v1')['rows']}
 for r in selection['rows']:
  u=r['uid'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==SOURCES[u];refs.append(p)
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==u)==r['source']['building'];refs.append(tile)
  identity=part('five-current-identity-v1',u.split('/')[1]+'/identity.json');assert identity['sourceSHA256']==SOURCES[u]
  raw_identity.append(identity)
  if u not in extras:assert identity['passed']and not identity['reasons'];identity_proofs[u]=identity['proof']
  else:
   e=extras[u];route=identity['exactCurrentComponentRoute'];target=r['source']['building']
   assert set(identity['reasons'])=={'current-target-does-not-cover-whole-georef-cell','original-source-does-not-cover-whole-georef-cell'}
   assert e['sourceGraphVerified']and identity['originalOwnership']['sourceGraphVerified']and route['qualified']and not route['reasons']
   assert route['source']['building']==target and route['official']['objectId']==target['objectId']and route['official']['buildingCSUID']==target['buildingCSUID']
   assert e['sourceSHA256']==SOURCES[u]and e['ownTargetCoverage']>=.95
   assert e['symmetricOutlineHausdorffDistanceM']<(.27 if u=='landsd/7521:0'else .005)
   assert not target['name']and not e['name']
   identity_proofs[u]=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True,basis='Exact unique component route and original root graph; bounded source/current cell-corner discrepancy with near-identical outlines; raw cell flags retained.')
  n=u.split('/')[1].split(':')[0]
  f=part(('five-tower-foundations-v1'if n=='235598'else 'five-podium-foundations-v1'if n=='233190'else 'adjoining'+n+'-foundations-v1'))
  assert len(f['rows'])==4 and all(x['completeTerrainTriangles']==x['triangles']==r['triangles']and x['fullyBuriedTriangles']==x['fullyBuriedUpwardTriangles']==0 for x in f['rows'])
 scope=part('five-current-scope-v1');assert scope['currentManifestSHA256']==ref(manifest)['sha256']and set(scope['uids'])==set(SOURCES)
 forms={}
 for r in scope['rows']:
  assert r['sourceSHA256']==SOURCES[r['uid']]and r['currentNativeActorsChecked']==6902 and not r['nearbyNativeActors']
  for f in part('five-current-scope-v1',r['uid'].split('/')[1]+'-forms.json.gz'):forms[f['building']['uid']]=f['building']
 assert set(forms)==set(SOURCES)|{'landsd/154486:0','landsd/23246:0'}
 foreign=part('five-current-foreign-contacts-v1');assert foreign['foreignPairs']==len(foreign['rows'])==12
 for r in foreign['rows']:
  assert len(r['modes'])==5 and {x['mode']for x in r['modes']}==MODES|{'before-basic'}
  if r['foreignUid']not in SOURCES:assert all(x['positiveContactPairs']==0 and x['projectedOverlapAreaM2']==0 for x in r['modes'])
 pairs=part('five-current-pairs-v1');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==10 and len(pairs['rows'])==40
 counts={'landsd/235598:0':16,'landsd/7521:0':44,'landsd/23480:0':8,'landsd/8602:0':8}
 for r in pairs['rows']:
  if 'landsd/233190:0'in [r['uid'],r['peerUid']]:
   other=r['peerUid']if r['uid']=='landsd/233190:0'else r['uid'];assert r['positiveSurfaceContacts']==counts[other]and r['contactDimensions']=={'1':counts[other]}
  else:assert r['strictBoundsSeparated']and not r.get('positiveSurfaceContacts',0)
 strict=take(P+'five-support-followthrough-v1-20261024-235598-233190-strict');paths=part('five-current-strict-root-paths-v1')
 assert len(strict['rows'])==len(paths['rows'])==4
 for r in strict['rows']:assert r['support']['strictContacts']==376 and len(r['support']['unresolved'])==18
 for r in paths['rows']:
  assert r['targets']==r['finiteAttachmentPaths']==18 and r['disconnected']==r['aboveExistingEndpointCeiling']==0
  proof=part('five-current-strict-root-paths-v1',r['mode']+'.json.gz');assert proof['noIntercomponentJoins']and proof['canonicalStrictAnchorCount']==376
  assert all(x['passesExistingEndpointHeight']and x['riseAboveEndpointsM']==0 and x['maximumResidualM']<=.001 and x['terminal']['kind']=='canonical-strict-vertical-support-anchor'for x in proof['rows'])
 small=take(P+'five-support-followthrough-v1-20261024-7521-233190-strict');sp=take(P+'five-support-followthrough-v1-20261024-7521-233190-paths')
 assert sp['allUnresolvedHaveFinitePaths']and len(sp['rows'])==4 and all(r['targets']==r['verifiedPaths']==2 and r['remaining']==0 for r in sp['rows'])
 for r in small['rows']:
  f=r['compoundFoundation'];assert f['triangles']==f['completeTerrainTriangles']==54 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
  assert r['support']['strictContacts']==0 and len(r['support']['unresolved'])==2
 # Complete source clearance certificates use all faces, including global-height-pruned faces.
 for n,faces,count in [('7521',[2,3,32,33],54),('8602',list(range(8)),10),('23480',[],26)]:
  suffix='compound'if n=='7521'else 'current';c=part('adjoining'+n+'-'+suffix+'-clearance-v1');assert len(c['rows'])==4
  for r in c['rows']:
   assert r['completeSourceFaces']==count and r['exactAffectedFaces']==faces and not r['negativeNonWallFaces']
   if faces:assert r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']and r['compoundCapPathsPassed']
   else:assert r['noAffectedFaces'] # No affected faces require no cap path.
 tower=part('two-current-complete-clearance-v2');assert len(tower['rows'])==4 and all(r['completeSourceFaces']==10066 and r['noAffectedFaces']and not r['exactAffectedFaces']for r in tower['rows'])
 # Reuse the podium's ordinary certificate only after proving current source and actual-ground arrays identical.
 old=P+'two-current-runtime-v2-20261024';new=P+'five-current-runtime-v1-20261024'
 def runtime(n):
  p=HERE/'local'/n/'runtime-geometry.json.gz';take(n,'selection.json.gz');assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return next(r for r in read(p)['rows']if r['uid']=='landsd/233190:0')
 before,after=runtime(old),runtime(new)
 for k in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(before[k]),np.asarray(after[k]))
 rims=take(P+'podium-current-prephysical-v2-20261024-rims');assert len(rims['rows'])==4 and all(r['passed']and r['minimumSampleGapM']>=-.5 and r['maximumRimGapM']<=1 for r in rims['rows'])
 continuous=part('five-current-continuous-v1');assert len(continuous['rows'])==5 and all(r['wholeSourceUncoveredFaces']==0 for r in continuous['rows'])
 grade=part('adjoining8602-original-terrain-v1');f=grade['rows'][0]['originalTerrainFoundation'];assert f['completeTerrainTriangles']==10 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0 and f['minimumGapM']< -2.65
 images=[]
 for n,files in [('five-original-context-v1',['complete-original-assembly.png','base-only-diagnostic.png']),('two-adjoining-identity-context-v1',['source-record-context.png']),('adjoining7521-compound-wall-views-v1',['region-1.png','region-2.png']),('adjoining8602-current-wall-views-v1',None)]:
  part(n)
  if files is None:files=[p.name for p in (BASE/(P+n+'-20261024')).glob('*.png')];assert len(files)==4
  for f in files:
   p=BASE/(P+n+'-20261024')/f;assert digest(p.read_bytes())==pins[P+n+'-20261024'][str(p.relative_to(ROOT))];refs.append(p);images.append(ref(p))
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORTS,nativeSupportByUid=SUPPORTS,reviewer='ROOT',identityAccepted=True,identityProofByUid=identity_proofs,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},rawIdentityReasonsRetained=[dict(uid=r['uid'],reasons=r['reasons'],proof=r['proof'])for r in raw_identity],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,completeCurrentNeighbourChecks=7,leaseResources=sorted('building:'+u for u in forms),retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],currentManifest=ref(manifest),currentManifestSHA256=ref(manifest)['sha256'],terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawClearancePassed=False,rawCanonicalFailuresPreserved=True,visualAcceptance=False,installationApproved=False,publication=False,imagesActuallyViewed=images,interpretation=[
 'Exact original tower235598/podium233190 and three separately routed original adjoining structures only. All11857faces remain unchanged, at fixed1x and source pose. The two unnamed auxiliaries retain their names unchanged. Both current authoritative footprints and their near-identical original projections fail whole-cell corner containment; exact component IDs, CSUIDs, original root graphs and high individual footprint overlap independently identify these specific assets. This is not general cell-flag or identity approval.',
 'Tower376canonical strict anchors are independently reproduced; all18remaining rim samples have continuous shared-original-edge paths to those anchors under unchanged endpoint-height and1mm residual limits in all4worlds. Raw direct support failures remain. No component join, raised path, fabricated intersection or terrain edit is needed.',
 '7521is a separate54face original adjoining upright, not a floating roof. Its two low rim endpoints lie below the highest podium surface by7.384m, but the actual original surfaces have44line contacts and both endpoints have finite original-facet paths to those contacts. The four negative facets2,3,32,33are lower vertical sidewalls continuing to exposed upper caps. Full source/compound foundations show zero wholly buried or upward buried faces in all4worlds. ROOT inspected both two-angle wall regions plus the complete and lower assembly. Accept this exact provider-authored sidewall/deck interface, preserve all strict negatives, and retain dependency7521->233190; do not broaden sampled embedding limits.',
 '8602is the exact10face open-bottom original shed:8vertical lower walls,2roof faces. All8negative walls retain exposed highest vertices and finite clear-cap paths; roof clearance remains ordinary and complete foundations show zero whole/upward burial. Currentwall embedding1.807m is shallower than the authenticated originalTINminimum2.6525m. ROOT inspected all4wall-region exports. Accept this named original grade/wall relationship without changing ground, source or global-.5m threshold. No horizontal buried floor is exempted.',
 '23480has complete ordinary clearance. The main podium ordinary clearance/support certificate is reused only after exact current source arrays and drawn-ground arrays match. All5sources have complete four-world foundations. All10sourcepairs are measured: only originalpodium line joints occur, no positive-area source intersections. Both external BASIC neighbours154486/23246have zero finite contacts and zero projected overlap before/after in all4worlds; all6902native actors were screened with zero nearby native actors. Browser picking/collision, failure/retry, source appearance, final joint activation, publication and live readback remain mandatory.'])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result)
 module('royal_five_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-five-original-physical-and-identity-interpretation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
