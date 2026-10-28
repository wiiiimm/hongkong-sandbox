"""Prepare and stage one qualified BASIC footing entirely in memory; never publish."""
import argparse,copy,json,sys,uuid,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
from basic_podium_footings import stage_basic_podium_footings,canonical,value_sha,terrain_geometry_sha,POLICY
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('qualified-basic-footing-fragment-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp,HERE.parent/'island-detail-integration/basic_podium_footings.py'];pins={};live_hashes={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 def tracked_read(path):
  path=Path(path);sha=digest(path.read_bytes());assert str(path)not in live_hashes or live_hashes[str(path)]==sha
  live_hashes[str(path)]=sha;refs.append(path);return read(path)
 old_batch=PREFIX+'basic-footing-publication-draft-v1-20261028';old=take(old_batch,'footing-review-draft.json');old_plan=take(old_batch,'plan-fragment.json')
 proposal_batch=PREFIX+'unnamed-basic-podium-footing-v1-20261028';b=take(proposal_batch,'input.json')['building'];proposal=take(proposal_batch,'proposal.json');ground=take(proposal_batch,'continuous-ground.json.gz');geometry=take(proposal_batch,'geometry.json.gz')
 coverage=take(PREFIX+'basic-podium-native-owner-coverage-v2-20261028','summary.json')
 collision=take(PREFIX+'basic-footing-collision-review-v1-20261028','review.json');visual=take(PREFIX+'remaining-foundation-visual-reviews-v1-20261028','213586:0-review.json')
 assert old['status']=='private-pending-collision-and-visual'and not old['collisionReviewApproved']and not old['visualReviewApproved']
 assert b['uid']==old['uid']==collision['uid']==visual['uid']=='landsd/213586:0'
 assert value_sha(b)==old['sourceFormSHA256']==collision['sourceFormSHA256']==visual['sourceFormSHA256']
 assert proposal['foundationBase']==old['foundationBase']==collision['foundationBase']==visual['foundationBase']==ground['foundationBottom']
 assert ground['uncoveredAreaM2']==0 and not ground['verticalOrDegenerateContacts']and ground['groundRange']==old['groundRange']
 assert geometry['after']['position'][:len(geometry['before']['position'])]==geometry['before']['position']and geometry['after']['index'][:len(geometry['before']['index'])]==geometry['before']['index']
 assert coverage['nativeCoverageMatchesActualDrawnGround']and coverage['nativeCoverageUncoveredAreaM2']==0 and not coverage['missingDrawnFaces']and coverage['bitExactMatchedFaces']==coverage['drawnPositiveAreaFaces']==58
 assert collision['collisionReviewApproved']and visual['visualReviewApproved']and visual['fixtureInputSHA256']
 inputs=take(PREFIX+'full-scene-preview-fixture-v2-20261028','fixture-inputs.json');cfg=tracked_read(ROOT/inputs['configPath'])
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=tracked_read(manifest_path);assert digest(manifest_path.read_bytes())==inputs['currentManifestSHA256']
 edits={};removed={r['url']for t in cfg['terrain']for r in t.get('replacesMany',([t['replaces']]if t.get('replaces')else []))}
 manifest['terrainPatches']=[t for t in manifest.get('terrainPatches',[])if t['url']not in removed]
 for terrain in cfg['terrain']:
  path=ROOT/terrain['source'];assert digest(path.read_bytes())==pins[PREFIX+'full-scene-preview-fixture-v2-20261028'][str(path.relative_to(ROOT))];refs.append(path)
  edits[(ROOT/'3d-viewer'/terrain['destination']).resolve()]=path.read_bytes();manifest['terrainPatches'].append(dict(url=terrain['destination'],resolution=terrain['resolution'],area=terrain['area']))
 catalogue=ROOT/cfg['stage']/'catalogue.json';assert digest(catalogue.read_bytes())==pins[PREFIX+'full-scene-preview-fixture-v2-20261028'][str(catalogue.relative_to(ROOT))];refs.append(catalogue)
 edits[(ROOT/'3d-viewer'/cfg['catalogueURL']).resolve()]=catalogue.read_bytes();manifest['officialModelCatalogues'].append(cfg['catalogueURL'])
 actual_tile=ROOT/'3d-viewer'/old_plan['basicPodiumFootings'][0]['tile'];actual_b=next(r for r in tracked_read(actual_tile)['buildings']if r['uid']==b['uid'])
 assert actual_b==b
 audit_rebound=copy.deepcopy(actual_b);assert audit_rebound['terrainAudit']['resolutions']==b['terrainAudit']['resolutions'];audit_rebound['terrainAudit']['resolutions']=copy.deepcopy(b['terrainAudit']['resolutions'])
 assert canonical(audit_rebound)==canonical(b),'Only audit resolution JSON number spelling may differ'
 proposal_input=BASE/proposal_batch/'input.json';eq_input=out/'audit-number-equivalence-input.json';eq_output=out/'audit-number-equivalence.json'
 save(eq_input,dict(uid=b['uid'],tile=str(actual_tile.relative_to(ROOT)),proposalInput=str(proposal_input.relative_to(ROOT)),foundationBase=proposal['foundationBase'],inputHashes={str(actual_tile.relative_to(ROOT)):digest(actual_tile.read_bytes()),str(proposal_input.relative_to(ROOT)):digest(proposal_input.read_bytes())}))
 eq_tool=HERE/'basic_footing_audit_number_equivalence_v1_20261028.mjs';refs.append(eq_tool)
 subprocess.run(['node',str(eq_tool),str(eq_input.relative_to(ROOT)),str(eq_output.relative_to(ROOT))],cwd=ROOT,check=True)
 eq=read(eq_output);assert eq['exactJavaScriptSourceFormValuesEqual']and eq['exactAllProductionGeometryAttributesBeforeAndAfterEqual']
 for path,sha in eq['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 fresh=copy.deepcopy(old);fresh.update(sourceFormSHA256=value_sha(actual_b),upstreamPreparedFormSHA256=old['sourceFormSHA256'],exactAuditNumberEquivalenceEvidence=dict(path=str(eq_output.relative_to(ROOT)),sha256=digest(eq_output.read_bytes())),sourceFormRebindingReviewedBy='Codex ROOT: exact live tile form; only terrainAudit.resolutions number spelling differs; all production geometry attributes are bit-identical before and after footing',status='approved-for-integration',collisionReviewApproved=True,visualReviewApproved=True,integrationOnlyConditionalOnExactNativeOwners=True,installationApproved=False,publication=False,
  collisionReviewEvidence=dict(path=str((BASE/(PREFIX+'basic-footing-collision-review-v1-20261028')/'review.json').relative_to(ROOT)),sha256=digest((BASE/(PREFIX+'basic-footing-collision-review-v1-20261028')/'review.json').read_bytes())),
  visualReviewEvidence=dict(path=str((BASE/(PREFIX+'remaining-foundation-visual-reviews-v1-20261028')/'213586:0-review.json').relative_to(ROOT)),sha256=digest((BASE/(PREFIX+'remaining-foundation-visual-reviews-v1-20261028')/'213586:0-review.json').read_bytes())))
 assert fresh['policy']==POLICY and fresh['proposalSHA256']==old_plan['basicPodiumFootings'][0]['proposal']['sha256']
 save(out/'qualified-footing-review.json',fresh)
 plan=copy.deepcopy(old_plan);plan['basicPodiumFootings'][0]['before']=copy.deepcopy(actual_b);plan['basicPodiumFootings'][0]['evidence']=dict(path=str((out/'qualified-footing-review.json').relative_to(ROOT)),sha256=digest((out/'qualified-footing-review.json').read_bytes()));save(out/'plan-fragment.json',plan)
 rejected=False
 try:stage_basic_podium_footings(ROOT,old_plan,copy.deepcopy(manifest),copy.deepcopy(edits),{},tracked_read,lambda p:digest(Path(p).read_bytes()),canonical)
 except AssertionError:rejected=True
 assert rejected,'Old unapproved draft must remain rejected'
 report={};stage_basic_podium_footings(ROOT,plan,manifest,edits,report,tracked_read,lambda p:digest(Path(p).read_bytes()),canonical)
 assert report['retainedBasicOnlyFootingChecks']==[b['uid']]and len(report['basicPodiumFootings'])==1
 tile_path=(ROOT/'3d-viewer'/plan['basicPodiumFootings'][0]['tile']).resolve();staged=json.loads(edits[tile_path]);changed=next(f for f in staged['buildings']if f['uid']==b['uid']);assert changed['foundationBase']==proposal['foundationBase']and changed['foundationPolicy']==POLICY
 original=copy.deepcopy(changed);original.pop('foundationBase');original.pop('foundationPolicy');assert original==b
 save(out/'staged-basic-tile.json',staged);save(out/'stager-report.json',report)
 for path,sha in live_hashes.items():assert digest(Path(path).read_bytes())==sha
 result=dict(uids=[b['uid']],status='qualified-basic-only-footing-fragment-staged-in-memory',qualifiedFootingReview=True,realFootingStagerPassed=True,oldUnapprovedDraftStillRejected=True,stagerReport=report,inMemoryOnly=True,publicFilesWritten=0,fullPublisherPassed=False,originalAssemblyAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,
  qualification='Fresh exact-input BASIC-only footing integration review combines existing authenticated whole-body/ground/native-owner evidence with separate collision and actual-image visual reviews. The unchanged real stager accepts it and still rejects the old draft. Only in-memory manifest/terrain/catalogue/tile bytes were staged; no deployable file was written. Exact native terrain ownership and future BASIC-only activation/suppression guards remain mandatory. Full original-model assembly, source boundaries/support, availability/failure/Base-only and full publisher acceptance remain pending.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('qualified_basic_footing_fragment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'qualified-basic-only-footing-integration-fragment-real-stager-check',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
