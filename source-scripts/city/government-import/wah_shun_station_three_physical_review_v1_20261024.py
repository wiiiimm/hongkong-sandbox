"""Bounded interpretation of three immutable originals, with all raw failures retained."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-wah-shun-station-three-physical-review-v1-20261024'
RUNTIME='government-xl-wah-shun-station-three-union-grade-runtime-v1-20261024'
SOURCES={'landsd/237751:0':'56b84c0518e8ee0f38a8174dc1e73170076ae20b989965c8e9e516c3eb87f9da','landsd/235644:0':'0a480d0cb509ef755ba595fb98132049b1c5befed29cfb00de78e190aa641568','landsd/84271:0':'393ef38d31aeb9e515dd26c852b83f3293cc8b42e7a99549a6531e389173dd89'}

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=take(RUNTIME,'selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256']for r in rows}==SOURCES
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==read(BASE/RUNTIME/'selection.json.gz')['manifestSHA256'];refs.append(manifest)
 raw_identity={}
 for r in rows:
  uid=r['uid'];raw=take('government-xl-wah-shun-station-three-identity-v1-20261024',uid.split('/')[1]+'/identity.json');raw_identity[uid]=raw['reasons']
  assert raw['sourceSHA256']==SOURCES[uid]and raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']
  if uid!='landsd/237751:0':assert raw['passed'] and not raw['reasons']
  else:assert set(raw['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','original-source-does-not-cover-whole-georef-cell'}
  n=uid.split('/')[1].split(':')[0];foundation=take('government-xl-wah-shun-station-'+n+'-union-foundations-v1-20261024','summary.json')
  assert len(foundation['rows'])==4 and all(x['triangles']==r['triangles']==x['completeTerrainTriangles'] and x['fullyBuriedTriangles']==x['fullyBuriedUpwardTriangles']==0 for x in foundation['rows'])
 association=take('government-xl-wah-shun-two-compound-projection-v1-20261024','summary.json');assert set(association['sourceSHA256ByUid'])=={'landsd/237751:0','landsd/235644:0'}
 assert all(r['wholeCellCoveredByOriginalAssembly']and r['wholeCellCoveredByCurrentAssembly'] and r['ownCoverageByWholeOriginalAssembly']>=.95 for r in association['rows'])
 support=take('government-xl-wah-shun-two-support-followthrough-v1-20261024','summary.json');assert len(support['rows'])==1
 sr=support['rows'][0];assert sr['uid']=='landsd/237751:0'and sr['supportUid']=='landsd/235644:0'and sr['allUnresolvedHaveFinitePaths'];assert len(sr['pathCounts'])==4 and all(x['targets']==x['verified']==22 and x['remaining']==0 for x in sr['pathCounts'])
 pairs=take('government-xl-wah-shun-station-three-pairs-v1-20261024','summary.json');assert len(pairs['rows'])==12
 for r in pairs['rows']:
  if {r['uid'],r['peerUid']}=={'landsd/235644:0','landsd/84271:0'}:assert r['positiveSurfaceContacts']==0 and not r['contactDimensions']
  elif 'landsd/84271:0' in [r['uid'],r['peerUid']]:assert r['strictBoundsSeparated']
  else:assert r['positiveSurfaceContacts']>0 and set(r['contactDimensions'])=={'1'}
 exact={}
 for uid in SOURCES:
  n=uid.split('/')[1].split(':')[0];batch=('government-xl-wah-shun-station-tower-union-complete-clearance-v1-20261024'if n=='237751'else 'government-xl-wah-shun-station-'+n+'-union-complete-clearance-v1-20261024')
  c=take(batch,'summary.json');assert len(c['rows'])==4 and all(x['compoundCapPathsPassed'] and x['allAffectedWallLike']and not x['negativeNonWallFaces']for x in c['rows'])
  if n=='235644':assert all(x['exactAffectedFaces']==[1219]and not x['allAffectedHaveExposedHighestVertex']for x in c['rows'])
  else:assert all(x['allAffectedHaveExposedHighestVertex']and len(x['exactAffectedFaces'])==({'237751':22,'84271':24}[n])for x in c['rows'])
  exact[uid]=c
 podium=next(r for r in rows if r['uid']=='landsd/235644:0');asset=ROOT/podium['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[podium['uid']];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());foot=tri[1219]
 assert float(foot[:,:,] .max())>0
 assert float(foot[:,1].max()-tri[:,:,1].min())<.5 and float(np.ptp(foot[:,1]))<.14
 comparison=take('government-xl-wah-shun-podium-union-source-grade-comparison-v1-20261024','summary.json');assert comparison['comparedFaces']==29 and comparison['currentTerrainBelowLimitFaces']==comparison['originalTerrainBelowLimitFaces']==1
 forms=take('government-xl-wah-shun-station-three-union-forms-v1-20261024','summary.json');assert forms['forms']==25 and not forms['flagged']and not forms['ordinaryFlagged']
 scope=take('government-xl-wah-shun-station-union-grade-scope-v1-20261024','scope.json');assert scope['currentNativeActors']==6899 and scope['positiveAreaTerrainOverlaps']==0 and not scope['touchingNativeUids']
 images=[]
 for uid in ['237751','235644','84271']:
  batch='government-xl-wah-shun-'+uid+'-union-negative-views-v2-20261024';v=take(batch,'summary.json');assert v['sourceSHA256']==SOURCES['landsd/'+uid+':0']and v['allExactNegativeFacesShown']
  for region in v['regions']:
   p=ROOT/region['image'];assert digest(p.read_bytes())==region['imageSHA256'];refs.append(p);images.append(dict(path=region['image'],sha256=region['imageSHA256']))
 for batch,filenames in [('government-xl-wah-shun-station-three-union-context-v1-20261024',['complete-original-assembly.png','base-only-diagnostic.png']),('government-xl-wah-shun-two-identity-context-v1-20261024',['source-record-context.png'])]:
  take(batch,'summary.json')
  for f in filenames:
   p=BASE/batch/f;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,reviewer='ROOT',sourceSpecificPhysicalInterpretationAccepted=True,sourceIdentityAssemblyQualified=True,identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),identityProofByUid={u:dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)for u in SOURCES},rawIdentityReasonsRetained=raw_identity,rawCanonicalFailuresPreserved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,imagesActuallyViewed=images,completeCurrentNeighbourChecks=25,currentManifestSHA256=digest(manifest.read_bytes()),retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],installationApproved=False,publication=False,visualAcceptance=False,
  interpretation=['Exact Wah Shun tower/podium source association only: separately routed immutable tower and named podium join by original line surfaces, resolve every22rim target in all4worlds and together cover98.33percent of the tower record plus its entire GeoRef cell. Raw91.15percent tower-alone coverage remains. This is not a rule accepting arbitrary grouped sources.',
  'The exact station source passes individual identity. Its own complete surfaces do not touch either original Wah Shun actor. The former28contacts against the station BASIC are representation artefacts resolved by replacing that exact BASIC with its independently qualified original; no ownership or support relationship to the station is inferred.',
  'All22tower and24station negative facets are walllike, retain exposed highest vertices and exact finite clear-cap paths in all4worlds. ROOT inspected all9two-angle region exports per actor, the complete assembly and lower assembly. Tower long facade faces have only their lower extent embedded; no roof/walking surface is approved as a wall.',
  'Podium1219 is the specific thin lower plinth return within0.5m of the complete source minimum, with0.133m vertical range. Its slight top burial is NOT called exposed-wall clearance. Exact original-TIN comparison independently reproduces the same sole below-limit facet. ROOT inspected its full two-angle neighbourhood: this is the lower return attached by the proved1219->1220->1237->1236->1235->1234->1233->1139 original clear-cap path, below the visible upright podium wall. This named provider-authored lower plinth/grade intersection is accepted without changing its geometry, original terrain, raw3.87m column minimum, or global-.5m threshold. No generic fully-buried/source-face exemption is introduced.',
  'The bounded12353face original-TIN terrain proposal passes unchanged validators, all25current basic forms and the full6899native inventory scope. No retained native or terrain overlap is present. All3complete sources have zero whole/upward whole burial in all4representations. Original fixed1x, pose, all faces and windows-off appearance stay unchanged. Browser appearance, picking/collision, failure/retry and publication remain mandatory.'])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result)
 module('wah_shun_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-wah-shun-and-independent-station-source-physical-interpretation',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
