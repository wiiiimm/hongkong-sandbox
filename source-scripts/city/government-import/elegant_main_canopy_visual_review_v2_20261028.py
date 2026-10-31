"""Bounded ROOT visual review of exact existing BASIC canopy post extensions."""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('main-canopy-post-visual-review-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 uid='landsd/99061:0';owner='landsd/236170:0'
 collision=take(PREFIX+'two-canopy-collision-review-v1-20261028','99061:0-review.json');assert collision['collisionReviewApproved']and not collision['visualReviewApproved']
 fixture=PREFIX+'full-scene-preview-fixture-v2-20261028';inputs=take(fixture,'fixture-inputs.json');cfg=read(ROOT/inputs['configPath'])
 overlay=next(o for o in cfg['privateFoundationTileOverlays']if any(c['uid']==uid for c in o['changes']));change=next(c for c in overlay['changes']if c['uid']==uid)
 assert change['foundationBase']==collision['foundationBase']and change['before']['structureType']=='Open-sided Structure'
 for path,sha in [(ROOT/'3d-viewer'/overlay['url'],overlay['beforeSHA256']),(ROOT/overlay['source'],overlay['afterSHA256'])]:assert digest(path.read_bytes())==sha;refs.append(path)
 source_sha=inputs['sourceSHA256ByUid'][owner];images=[]
 focused_batch=PREFIX+'focused-post-mobile-views-v2-20261028';focused=take(focused_batch,'390/staged-browser.json');assert focused['passed']and not focused['errors']and len(focused['postDiagnostics'])==2
 for row in focused['postDiagnostics']:
  assert row['uid']==uid and row['best']['visibleLowerSamples']>0 and row['best']['cameraCollision']is None and row['best']['aboveGround']
  assert row['foundationBase']==collision['foundationBase']and len(row['exports'])==2
  for image in row['exports']:
   assert image['captureCamera']==row['best']['position']and image['captureTarget']==row['best']['target']
   assert image['selectionClosed']and image.get('basicHidden') is not True and image['privateFreeCameraObservation']and image['orbitMinDistanceUnchanged']==12
   assert image['sourceOwners']==[dict(uid=owner,active=True,sha256=source_sha)]
   path=BASE/focused_batch/'390'/image['file'];assert digest(path.read_bytes())==pins[focused_batch][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),width=390,postIndex=row['postIndex'],time=image['time'],captureCamera=image['captureCamera']))
 desktop_batch=PREFIX+'foundation-closeups-v1-20261028';desktop=take(desktop_batch,'1280/staged-browser.json');assert desktop['passed']and not desktop['errors']
 row=next(r for r in desktop['foundationDiagnostics']if r['uid']==uid)
 for image in row['exports']:
  assert image['selectionClosed']and image['basic']['foundationBase']==collision['foundationBase']
  assert dict(uid=owner,sha256=source_sha)in image['activeContext']
  path=BASE/desktop_batch/'1280'/image['file'];assert digest(path.read_bytes())==pins[desktop_batch][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),width=1280,time=image['time'],nominalRayCountsNotUsedForApproval=True))
 assert len(images)==6
 result=dict(uids=[uid],uid=uid,reviewer='Codex ROOT',reviewType='exact-existing-basic-canopy-two-post-extension-visible-appearance-only',sourceFormSHA256=collision['sourceFormSHA256'],foundationBase=collision['foundationBase'],fixture=fixture,fixtureInputSHA256=digest((BASE/fixture/'fixture-inputs.json').read_bytes()),tileSHA256=overlay['beforeSHA256'],sourceOwnerUID=owner,sourceOwnerSHA256=source_sha,imagesActuallyInspected=images,
  visualReviewApproved=True,collisionReviewPreviouslyApproved=True,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,physicalAccepted=False,originalModelPlacementApproved=False,roofPlacementApprovalTransferred=False,installationApproved=False,publication=False,
  basis=[
   'ROOT inspected both existing post feet in the four corrected mobile day/night exports and the two desktop context exports. The visible extensions continue the existing posts to the drawn ground with no apparent floating gap, added windows or selection highlight. The source podium remains active with its exact expected SHA in every export.',
   'The corrected mobile captures synchronously restore and record the exact nominated free-camera position immediately before rendering. OrbitControls minimum distance remains12m. These private free-camera observations are appearance evidence, not proof of ordinary-orbit camera accessibility or performance.',
   'The optional basicHidden field is omitted by JSON when the live BASIC record has no hidden property. Its absence is only a negative hidden-state check, not presence proof; the exact-target ray witnesses, inspected post images, fixture source bindings and active source-owner records provide the positive evidence.',
   'The earlier whole-canopy mobile view hid the lower posts behind the source podium. The aborted focusedV1used a camera nomination below the OrbitControls minimum and is rejected. Desktop close-up images remain image evidence only: their nominal ray counts were not used because the orbit-clamped actual camera position was not separately recorded.',
   'Existing exact ground coverage and collision-only evidence remain separately bound. This approves only visible appearance of the two exact BASIC post extensions on the stated private fixture. It does not approve the original assembly, all16joint context, source identity/boundary/support semantics, roof placement, ordinary navigation, availability, failure/Base-only tests or publication. The earlier publication draft remains unapproved.'])
 save(out/'review.json',result);assert reservations.owns(lease)
 module('main_canopy_visual_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-exact-existing-basic-main-canopy-post-extension-visual-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
