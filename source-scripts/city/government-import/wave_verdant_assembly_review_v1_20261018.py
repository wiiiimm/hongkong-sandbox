"""Consolidate exact nine-original acceptance; never install from isolated diagnostic flags."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-assembly-review-v1-20261018';DOC=BASE/BATCH
NAMES=['wave-verdant-podium-review-v1','wave-verdant-reviewed-identity-replay-v1','verdant194544-reviewed-identity-replay-v1','wave-verdant-identity-routes-v1','wave-towers-interface-review-v1','verdant195000-seam-review-v1','verdant194544-seam-review-v1','wave301562-reviewed-underside-v1','wave-verdant-current-ground-equivalence-v5','wave-verdant-current-native-scope-v2','wave-verdant-current-terrain-rebind-v5','wave-verdant-current-neighbours-v5','wave-verdant-private-browser-v5','wave-verdant-joint-scene-v3','wave-verdant-failed-downloads-v1','wave-verdant-dependency-failures-v1','wave-verdant-publication-proposal-v1','wave-verdant-retained-contacts-v3','wave-verdant-current-identity-runtime-v1']
def folder(n,date='20261018'):return BASE/('government-xl-'+n+'-'+date)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'acceptance-policy.py'];versions=set();records=[]
 archivepath=folder('apex227942-original-installed-v1')/'result.json';archive=read(archivepath)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(archive['jobId'],)).fetchone()==('complete',archive)
  for name in NAMES:
   p=folder(name)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);records.append(dict(batch=name,jobId=r['jobId']));versions.update((e['path'],e['sha256'])for e in r['evidenceRefs'])
 mapping={(e['originalPath'],e['originalSHA256']):e['savedHistoricalBytes']for e in archive['historicalMutableByteSnapshots']};pins={}
 for path,h in versions:
  p=ROOT/path
  if digest(p.read_bytes())!=h:
   old=mapping[(path,h)];assert old['sha256']==h;p=ROOT/old['path']
  assert digest(p.read_bytes())==h,path
  k=str(p.relative_to(ROOT));assert k not in pins or pins[k]==h;pins[k]=h;refs.append(p)
 refs.append(archivepath)
 cat=read(HERE/'local/government-xl-wave-verdant-publication-proposal-v1-20261018/catalogue.json');sources={m['uid']:m['sha256']for m in cat['models']};assert len(sources)==9
 for m in cat['models']:
  assert not m['publicationApproved']and not m['placementReviewed']and not m.get('suppressesBuildingUids');p=HERE/'local/government-xl-wave-verdant-publication-proposal-v1-20261018'/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p)
 routes=read(folder('wave-verdant-identity-routes-v1')/'summary.json')['rows'];identity={r['uid']for r in routes if r['identityRouteAvailable']};assert len(identity)==6
 pair=read(folder('wave-verdant-reviewed-identity-replay-v1')/'summary.json')['rows'];assert len(pair)==2 and all(x['freshReplayPassed']and len(x['rejectedChanges'])==5 for x in pair);identity.update(x['uid']for x in pair)
 one=read(folder('verdant194544-reviewed-identity-replay-v1')/'identity-proof.json');assert one['passed'];identity.add('landsd/194544:0');assert identity==set(sources)
 physical=read(folder('wave-verdant-assembly-four-worlds-v1','20261017')/'summary.json')['rows'];assert len(physical)==32 and all(x['strictFoundationAccepted']and x['buried']==0 and x['upwardBuried']==0 for x in physical)
 reviews=[('wave-towers-interface-review-v1','ROOT-INTERFACE-REVIEW.json','sourceSpecificInterfaceInterpretationAccepted'),('verdant195000-seam-review-v1','ROOT-SEAM-REVIEW.json','sourceSpecificSeamInterpretationAccepted'),('verdant194544-seam-review-v1','ROOT-SEAM-REVIEW.json','sourceSpecificSeamInterpretationAccepted'),('wave301562-reviewed-underside-v1','ROOT-UNDERSIDE-REVIEW.json','sourceSpecificInterfaceInterpretationAccepted'),('wave-verdant-podium-review-v1','ROOT-PODIUM-REVIEW.json','sourceSpecificGroundInterfaceAccepted')]
 for n,f,key in reviews:
  q=read(folder(n)/f);assert q[key]and q['sourceGeometryChanges']==q['sourcePoseChanges']==0
  if 'sourceSHA256'in q:assert q['sourceSHA256']==sources[q['uid']]
  refs.append(folder(n)/f)
 eq=read(folder('wave-verdant-current-ground-equivalence-v5')/'equivalence.json');assert eq['currentStrictExteriorUnchanged']and eq['productionModuleClosuresExactlyIdentical']and eq['basicActorsExactlyIdentical']==44 and all(x['allRelevantDrawnFacesIdentical']for x in eq['ground'])
 scope=read(folder('wave-verdant-current-native-scope-v2')/'scope.json');assert scope['allCurrentActorsNominated']and scope['currentNativeActors']==6684 and not scope['touchingNativeUids']
 basic=read(folder('wave-multicore-private-basic-estimates-v4','20261017')/'summary.json')['rows'];assert len(basic)==3 and all(x['allPartGroundChecksPass']and x['allXZExactlyUnchanged']for x in basic)
 retained=read(folder('wave-multicore-retained-basic-v4','20261017')/'summary.json')['rows'];assert len(retained)==2 and all(x['supportPassed']and x['complete']and x['compoundBuried']==0 for x in retained)
 neighbours=read(folder('wave-verdant-current-neighbours-v5')/'summary.json');assert neighbours['forms']==48 and not neighbours['nativeRows'];resolved=set(sources)|{x['uid']for x in basic+retained};assert all(x['uid']in resolved and x['reasons']==['increased-neighbour-ground-gap']for x in neighbours['basicFlags'])
 contacts=read(folder('wave-verdant-retained-contacts-v3')/'summary.json');assert contacts['actorModePairs']==1404 and contacts['retainedBasicActors']==39 and contacts['contactActorModePairs']==0
 runtime=read(folder('wave-verdant-current-identity-runtime-v1')/'validation.json');assert runtime['loaderAccepted']==runtime['checksPassed']==9 and runtime['exceptions']==0
 browser=read(folder('wave-verdant-private-browser-v5')/'staged-browser.json');assert browser['passed']and not browser['errors']and len([v for v in browser['views']if 'time'in v])==36
 joint=read(folder('wave-verdant-joint-scene-v3')/'summary.json');assert joint['passed']and not joint['errors']and joint['jointViews']==2 and joint['productionBudgetsUnchanged']
 for n,count in [('wave-verdant-failed-downloads-v1',9),('wave-verdant-dependency-failures-v1',2)]:
  q=read(folder(n)/'summary.json');assert q['passed']and q['completed']==count and all(x['passed']and not x['errors']for x in q['rows'])
 terrain=read(folder('wave-verdant-current-terrain-rebind-v5')/'terrain-candidates.json');assert len(terrain)==1;assert digest((ROOT/terrain[0]['path']).read_bytes())==terrain[0]['sha256']
 manifest=ref(ROOT/'3d-viewer/city/data/manifest.json');proposal=read(folder('wave-verdant-publication-proposal-v1')/'summary.json');assert proposal['publisherDryRunPassed']and proposal['currentManifest']==manifest
 decision=dict(reviewer='Codex ROOT',originalSourceReviewAccepted=True,sourceSHA256ByUid=sources,identityAccepted=True,placementAccepted=True,policyReasons=[],currentManifest=manifest,terrainCandidate=terrain[0],sourceReviews=[ref(folder(n)/f)for n,f,k in reviews],checkedReceipts=records,retainedNeighbours=contacts,basicCorrections=basic,retainedPodiumSupportedBasics=retained,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,newlyInstalled=0,observations=['All nine identities have exact accepted source routes; bounded exceptions retain their raw metrics and reject changed source bindings.','Complete four-mode foundations and source-specific tower seams, authored underside and podium ground interfaces have exact reviews. No generic guard was relaxed.','Current full-map native census has no touching installed actors; complete exterior remains unchanged. All48 affected forms and39 retained BASIC actors accounted for. Three BASIC-only estimates and two unchanged podium-supported forms close all coarse neighbour flags.','All nine runtime loads,36 individual day/night views, joint desktop/mobile views and9own+2support download/recovery cases pass. Mobile joint view correctly retains BASIC for two tiny sources below24pixels.','Original overlaps within the assembly retain original authoring and reviewed support semantics; no invented ownership or engineering requirement.'],limitations=['Runtime and source-specific review, not engineering certification or optimisation authorization.','Zero finite neighbour contacts does not establish generic solid containment; exact source identity, neighbour placement and visible context are reviewed together.','Images contain ordinary occlusion; full framing does not mean every face is visible.','Guarded installation, live verification and installed ledger still required.'])
 save(DOC/'ROOT-SOURCE-REVIEW.json',decision);out=module('wave_assembly_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-exact-original-full-assembly-source-review-v1',list(set(refs)),dict(uids=list(sources),originalSourceReviewAccepted=True,publication=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
