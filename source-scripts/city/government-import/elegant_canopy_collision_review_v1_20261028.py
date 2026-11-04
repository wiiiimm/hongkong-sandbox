"""Bounded collision-only ROOT review of two exact private BASIC post extensions."""
import argparse,sys,uuid,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import'
PREFIX='government-xl-elegant-garden-'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('canopy-post-collision-review-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 reviews=[]
 for name,uid,post_count in [('main-canopy','landsd/99061:0',2),('grand-scholar','landsd/336456:0',4)]:
  proposal_batch=PREFIX+name+'-final-sixteen-posts-v1-20261028'
  b=take(proposal_batch,'input.json')['building'];proposal=take(proposal_batch,'proposal.json');geometry=take(proposal_batch,'render-proof.json');ground=take(proposal_batch,'continuous-part-ground-proof.json')
  runtime=take(PREFIX+name+'-runtime-collision-v1-20261028','runtime-collision.json');contacts=take(PREFIX+name+'-foreign-volume-v1-20261028','summary.json')
  assert b['uid']==proposal['uid']==runtime['uid']==contacts['uid']==uid
  assert b['structureType']=='Open-sided Structure'and b['kind']=='roof'and not b.get('modelGeometry')
  assert geometry['roofPartsExactlyUnchanged']and geometry['allXZExactlyUnchanged']and geometry['onlyIllustrativePostBottomVerticesChanged']and geometry['postCount']==post_count
  posts=[r for r in ground['rows']if r['kind']=='post'];assert len(posts)==post_count
  assert all(r['uncoveredAreaM2']==0 and r['foundationAtOrBelowAllGround']and r['postTopAboveAllGround']for r in posts)
  assert runtime['postCount']==post_count and runtime['probes']==post_count*1050 and runtime['unchangedRegionalForms']==155
  assert runtime['allRoofPartsExactlyRetained']and runtime['onlyPostBottomsChanged']and runtime['allPostFootprintsAndTopsExactlyRetained']and runtime['addedTargetCollisionProbes']>0
  assert contacts['candidateOriginals']==16 and contacts['originalCoordinateStreams']==4 and contacts['testedForeignBasicForms']==155
  assert len(contacts['rows'])==219 and contacts['surfaceVolumeContactRows']==0 and contacts['nativeBoundsPending']==0 and len(contacts['nativeRows'])==9
  assert all(r['closedPostExtensionVolumeContacts']==0 for r in contacts['rows'])
  for path,sha in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
  review=dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-existing-basic-canopy-downward-post-extension-collision-only',sourceFormSHA256=digest(json.dumps(b,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()),foundationBase=proposal['foundationBase'],postCount=post_count,probes=runtime['probes'],rawGroundProofRetained=ground,
   collisionReviewApproved=True,visualReviewApproved=False,physicalAccepted=False,originalModelPlacementApproved=False,installationApproved=False,publication=False,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,reverseSolidContainmentProved=False,
   basis=[
    'Only the bottoms of the existing illustrative BASIC posts extend downward. The production collision parts retain every roof, post footprint and top; all155other BASIC volumes remain unchanged. Finite production BuildingIndex probes remove no collision and attribute every sampled regional change to these extensions.',
    'The exact Float32 post-bottom cap triangles define the checked extension prisms. All16candidate originals in4captured coordinate streams and155foreign BASIC surfaces have zero closed-prism surface contacts. All9installed originals are separated by their complete four-world bounds. This is not a reverse closed-solid containment or structural proof.',
    'Every complete post footprint has current ground coverage and its proposed bottom is at/below that ground. Existing roof-ground context, including any raw uncovered area or conservative vertical contacts, is retained verbatim; this collision-only judgement grants no new roof-placement approval.',
    'Visual review, source assembly identity/boundaries/support, current runtime availability and guarded publication remain independent. The main canopy mobile lower band was obscured in the actual close-ups; no visual approval is inferred from a passing collision check. Government geometry and poses are unchanged.'])
  save(out/(uid.split('/')[1]+'-review.json'),review);reviews.append(dict(uid=uid,collisionReviewApproved=True,visualReviewApproved=False,foundationBase=proposal['foundationBase'],postCount=post_count))
 result=dict(uids=[r['uid']for r in reviews],rows=reviews,collisionReviewApproved=True,visualReviewApproved=False,physicalAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True)
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('canopy_collision_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-bounded-basic-canopy-post-extension-collision-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
