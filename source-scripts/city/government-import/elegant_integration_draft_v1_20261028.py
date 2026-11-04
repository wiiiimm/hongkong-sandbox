"""Draft the exact full integration plan and exercise BASIC stagers in memory only.

No reservation, publication, source file edit, acceptance or Neon write. Pending
native replacement decisions deliberately make the canonical publisher reject it.
"""
import copy,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-';OUT=BASE/(PREFIX+'integration-draft-v1-20261028')
def main():
 refs=[];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 fixture=take(PREFIX+'supported-activation-fixture-v2-20261028','fixture-inputs.json')
 cfgpath=ROOT/fixture['configPath'];cfg=read(cfgpath);assert digest(cfgpath.read_bytes())==pins[PREFIX+'supported-activation-fixture-v2-20261028'][str(cfgpath.relative_to(ROOT))];refs.append(cfgpath)
 catpath=ROOT/cfg['stage']/'catalogue.json';assert digest(catpath.read_bytes())==pins[PREFIX+'supported-activation-fixture-v2-20261028'][str(catpath.relative_to(ROOT))];cat=read(catpath);refs.append(catpath);assert len(cat['models'])==16 and all(not m['publicationApproved']and not m['placementReviewed']for m in cat['models'])
 regression=take(PREFIX+'sixteen-original-updated-neighbours-v1-20261028','summary.json');assert len(regression['nativeRows'])==9 and all(r['passed']for r in regression['nativeRows']);checkpath=OUT/'retained-native-mesh-checks-draft.json';save(checkpath,dict(rows=regression['nativeRows'],aiCalls=0,modelGeometryChanges=0,sourceEvidence='Authenticated unchanged full native before/after terrain checks; no new source/model acceptance.'))
 ref=lambda path:dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
 terrain=[]
 for entry in cfg['terrain']:
  e=copy.deepcopy(entry);new=ROOT/e['source'];e['sha256']=digest(new.read_bytes());old=ROOT/'3d-viewer'/e['replaces']['url'];assert digest(old.read_bytes())==e['replaces']['sha256'];refs.extend([old,new]);retained=read(old)['meta']['targetUids'];assert set(retained)<=set(regression['nativeResolved'])
  reviewpath=OUT/(('west'if 'west'in e['destination']else'east')+'-native-replacement-PENDING.json');save(reviewpath,dict(status='pending-final-source-visual-integration-review',supersededURL=e['replaces']['url'],supersededSHA256=e['replaces']['sha256'],replacementSHA256=e['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=retained,replacementTargetUids=read(new)['meta']['targetUids'],fullMeshCheck=ref(checkpath),publication=False));e['nativeReview']=ref(reviewpath);terrain.append(e)
 plan=copy.deepcopy(take(PREFIX+'qualified-footing-fragment-v2-20261028','plan-fragment.json'));destination='city/data/official-models/'+PREFIX+'sixteen-original-qualified-stage-v1-20261028/catalogue.json';plan.update(status='unapproved-draft-not-publishable',areas=[dict(area='Elegant Garden and exact original support companions',catalogue=str(catpath.relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=terrain,illustrativeFoundations=[])
 for name in ['main-canopy-final-sixteen-posts-v1-20261028','grand-scholar-final-sixteen-posts-v1-20261028']:
  batch=PREFIX+name;inp=take(batch,'input.json');proposal=take(batch,'proposal.json');evidence=take(batch,'summary.json');b=inp['building'];tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(x for x in read(tile)['buildings']if x['uid']==b['uid'])==b;refs.append(tile)
  assert evidence['fullPostFootprintsMeetGround']and evidence['wholeRoofClear'];plan['illustrativeFoundations'].append(dict(uid=b['uid'],tile='city/data/tiles/'+b['tile']+'.json',tileSHA256=digest(tile.read_bytes()),before=b,foundationBase=proposal['foundationBase'],proposal=ref(BASE/batch/'proposal.json'),evidence=ref(BASE/batch/'summary.json')))
 save(OUT/'integration-plan-DRAFT.json',plan)
 # Compose all three real stagers with the exact future manifest/terrain/catalogue,
 # without invoking the publisher or writing any viewer asset.
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest_path.read_bytes())==fixture['currentManifestSHA256'];manifest=copy.deepcopy(read(manifest_path));refs.append(manifest_path);edits={};report={};encoded=lambda x:(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode()
 replaced={e['replaces']['url']for e in terrain};manifest['terrainPatches']=[e for e in manifest['terrainPatches']if e['url']not in replaced]
 for e in terrain:
  path=ROOT/'3d-viewer'/e['destination'];edits[path]=(ROOT/e['source']).read_bytes();manifest['terrainPatches'].append(dict(url=e['destination'],sha256=e['sha256']))
 edits[ROOT/'3d-viewer'/destination]=encoded(cat);manifest['officialModelCatalogues'].append(destination)
 illustr=module('elegant_draft_illustrative',HERE.parent/'island-detail-integration/illustrative_foundations.py');foot=module('elegant_draft_footing',HERE.parent/'island-detail-integration/basic_podium_footings.py');retained=module('elegant_draft_retained',HERE.parent/'island-detail-integration/retained_basic_support.py')
 sha=lambda p:digest(Path(p).read_bytes());illustr.stage_illustrative_foundations(ROOT,plan,manifest,edits,report,read,sha,encoded);foot.stage_basic_podium_footings(ROOT,plan,manifest,edits,report,read,sha,encoded);retained.stage_retained_basic_support(ROOT,manifest,edits,report,read)
 assert len(report['illustrativeFoundations'])==2 and len(report['basicPodiumFootings'])==1;assert set(report['retainedBasicOnlyFootingChecks'])=={'landsd/213586:0'};assert sum(r['uid']=='landsd/173764:0'and r['supportUid']=='landsd/228592:0'for r in report['retainedBasicSupportChecks'])==1
 tile=ROOT/'3d-viewer/city/data/tiles/-2_0.json';save(OUT/'staged-basic-tile-DRAFT.json',json.loads(edits[tile]));save(OUT/'combined-basic-stagers-report.json',report)
 for p in [Path(illustr.__file__),Path(foot.__file__),Path(retained.__file__),Path(__file__)]:refs.append(p)
 save(OUT/'draft-inputs.json',dict(inputRefs=[ref(p)for p in dict.fromkeys(refs)],inMemoryCombinedBasicStagersPassed=True,currentManifestSHA256=fixture['currentManifestSHA256'],nativeReplacementDecisionsPending=True,modelPublicationFlagsFalse=True,publicFilesWritten=0,neonWrites=0,installationApproved=False,publication=False))
 print('Full draft:16originals,2terrain replacements,2canopy foundations,1BASIC footing. All3BASIC stagers and every global retained support binding pass in memory. Native reviews PENDING; no publisher/apply/approval.')
if __name__=='__main__':main()
