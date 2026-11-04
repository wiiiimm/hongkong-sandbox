"""Bounded ROOT visual judgements for two exact BASIC foundation changes."""
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
  assert not local.exists();claim=reservations.claim('remaining-basic-foundation-visual-review-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 fixture=PREFIX+'full-scene-preview-fixture-v2-20261028';inputs=take(fixture,'fixture-inputs.json');cfg=read(ROOT/inputs['configPath'])
 reports={w:take(PREFIX+'foundation-closeups-v1-20261028',str(w)+'/staged-browser.json')for w in [1280,390]}
 take(PREFIX+'foundation-image-review-v1-20261028','root-observations.json')
 cases=[('landsd/213586:0',PREFIX+'basic-footing-collision-review-v1-20261028','review.json',['landsd/215726:0']),('landsd/336456:0',PREFIX+'two-canopy-collision-review-v1-20261028','336456:0-review.json',['landsd/255231:0','landsd/257493:0'])]
 rows=[]
 for uid,collision_batch,filename,owners in cases:
  collision=take(collision_batch,filename);assert collision['collisionReviewApproved']and not collision['visualReviewApproved']
  overlay=next(o for o in cfg['privateFoundationTileOverlays']if any(c['uid']==uid for c in o['changes']));change=next(c for c in overlay['changes']if c['uid']==uid)
  assert change['foundationBase']==collision['foundationBase']
  for path,sha in [(ROOT/'3d-viewer'/overlay['url'],overlay['beforeSHA256']),(ROOT/overlay['source'],overlay['afterSHA256'])]:assert digest(path.read_bytes())==sha;refs.append(path)
  images=[]
  for width,report in reports.items():
   assert report['passed']and not report['errors']
   row=next(r for r in report['foundationDiagnostics']if r['uid']==uid)
   assert row['foundationBase']==collision['foundationBase']and len(row['exports'])==2
   for image in row['exports']:
    assert image['selectionClosed']and image['basic']['uid']==uid and image['basic']['foundationBase']==collision['foundationBase']and image['basic'].get('hidden')is not True
    required=owners if width==390 or uid=='landsd/213586:0' else ['landsd/257493:0']
    for owner in required:assert dict(uid=owner,sha256=inputs['sourceSHA256ByUid'][owner])in image['activeContext']
    path=BASE/(PREFIX+'foundation-closeups-v1-20261028')/str(width)/image['file'];assert digest(path.read_bytes())==pins[PREFIX+'foundation-closeups-v1-20261028'][str(path.relative_to(ROOT))];refs.append(path)
    images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),width=width,time=image['time'],activeContext=image['activeContext'],nominalRayCountsNotUsedForApproval=True))
  if uid=='landsd/213586:0':
   observations=['The four inspected desktop/mobile day/night exports show the exposed narrow wall-to-ground seam continuing into the drawn ground, with no apparent floating gap, windows on the added footing or selection highlight. Adjacent walls naturally obscure most of this small footprint.',
    'The reviewed West Grand podium source215726is active with its exact SHA in all4images. The separate collision review accepts continuation along the same3vertical native-wall facets and retains all raw contacts. Complete drawn-ground coverage and unchanged original BASIC body/footprint are separate exact evidence; image visibility is not substituted for those proofs.']
  else:
   observations=['The four inspected desktop/mobile day/night exports show the exposed front post feet meeting the irregular terrain. Other posts are naturally obscured; ROOT does not claim to have seen all4feet in pixels. The complete4post geometry/ground and collision evidence covers their identical downward-extension rule without moving any footprint/top/roof.',
    'The native Grand Scholar podium257493is active in all4images; the tower255231is additionally active in both mobile images. Desktop uses its ordinary resident context and is not represented as a full original-group view. Existing roof-ground context, including its raw tiny uncovered area and conservative vertical contacts, stays recorded and receives no transferred roof-placement approval.']
  review=dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-existing-basic-foundation-visible-appearance-only',sourceFormSHA256=collision['sourceFormSHA256'],foundationBase=collision['foundationBase'],fixture=fixture,fixtureInputSHA256=digest((BASE/fixture/'fixture-inputs.json').read_bytes()),tileSHA256=overlay['beforeSHA256'],imagesActuallyInspected=images,visualReviewApproved=True,collisionReviewPreviouslyApproved=True,physicalAccepted=False,originalModelPlacementApproved=False,roofPlacementApprovalTransferred=False,installationApproved=False,publication=False,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,
   basis=observations+['ROOT uses these actual images as bounded appearance evidence, not the nominal camera ray counts: the desktop footing camera could be clamped by the unchanged OrbitControls minimum. No whole-interface visibility, universal navigation, source identity/ownership, all16joint context or original assembly acceptance is inferred. The exact geometry/ground/collision checks remain independently mandatory.',
   'This judgement approves visible appearance of this exact existing BASIC foundation change only. No public form/catalogue/terrain changes or publication follow. All original source boundary/support/availability/failure/Base-only checks and the guarded publisher still have to pass. The earlier unapproved publication draft remains unchanged.'])
  save(out/(uid.split('/')[1]+'-review.json'),review);rows.append(dict(uid=uid,visualReviewApproved=True,foundationBase=collision['foundationBase']))
 result=dict(uids=[r['uid']for r in rows],rows=rows,visualReviewApproved=True,physicalAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True)
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('remaining_foundation_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-exact-existing-basic-foundation-visible-appearance-reviews',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
