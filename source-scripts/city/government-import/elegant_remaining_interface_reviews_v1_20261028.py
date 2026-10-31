"""ROOT's bounded original authored-joint and retained roof-wall interface decisions."""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
ROLES=[
 'Small raised native component meets its source podium roof and parapet; keep the authored seating surfaces.',
 'Fortune native lower tower/perimeter seats in the matching podium roof openings and edge bands.',
 'Block2 lower native facade meets the main podium edge/fascia, without changing the previously reviewed wall paths.',
 'Louis native lower facade/perimeter seats at its matching podium roof/edge.',
 'Block1 matching tower and podium roof-opening/perimeter junction in the left-associated Float32 stream; original/literal zero contacts remain zero, not a failure or a reason to shift geometry.',
 'Fortune podium and main podium meet at their adjoining lower opaque wall junction.',
 'West Grand tower lower plinth/perimeter meets the matching West Grand podium roof/edge.',
 'West Grand podium and the neighbouring registered unnamed original meet along the lower opaque facade/plinth band.',
 'West Grand tower and the registered unnamed neighbour have an adjoining vertical opaque facade junction; preserve both authored facades.',
 'Tung Wai podium and Louis podium meet at an adjoining roof edge/wall step.',
 'Tung Wai tower lower perimeter seats in the matching podium roof opening and edge band.',
 'Tung Wai podium and Grand Scholar podium meet at an adjoining stepped roof edge and wall.',
 'Grand Scholar tower lower plinth/perimeter seats in its matching podium roof opening and edge band.',
 'The retained estimated Grand Scholar BASIC canopy roof terminates at the native podium vertical wall; this is an opaque roof/wall interface, not evidence that the native source contains a replacement canopy.'
]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists();rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('root-remaining-interface-reviews-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 vb=PREFIX+'remaining-interface-views-v3-20261028';views=take(vb,'summary.json');contexts=take(vb,'contexts.json');assert views['cases']==len(contexts)==14 and views['views']==28
 assert len(views['images'])==4
 for image in views['images']:p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256'];refs.append(p)
 mb=PREFIX+'activation-interference-matrix-v1-20261028';matrix=take(mb,'summary.json');rows=take(mb,'rows.json.gz');selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']}
 identities=take(PREFIX+'identity-boundary-reviews-v1-20261028','summary.json');assert identities['allSixteenSourceAssociationsQualified']
 reviews=[]
 for i,(context,role)in enumerate(zip(contexts,ROLES)):
  left,right=context['sourceUid'],context['otherUid'];native=context['kind']=='native-native'
  raw=[r for r in rows if r['sourceUid']==left and r['otherUid']==right and r['kind']==('original-original'if native else'original-basic')]
  assert {r['mode']for r in raw}=={'original','literal','leftF32','balancedF32'}
  for r in raw:
   if native:
    if r.get('proof'):take(mb,r['proof'])
   else:
    for proof in r['contactProofs']:take(mb,proof['proof'])
  if not native:
   assert left=='landsd/257493:0'and right=='landsd/336456:0'
   assert {f['sourceFace']for f in context['sourceFacets']}=={41,160}and all(f['normal'][1]==0 for f in context['sourceFacets'])
   for mode in ['original','literal','leftF32','balancedF32']:
    before=next(r for r in raw if r['mode']==mode and r['state']=='before');after=next(r for r in raw if r['mode']==mode and r['state']=='after');assert before['contacts']==after['contacts']==4
    assert take(mb,before['contactProofs'][0]['proof'])['contacts']==take(mb,after['contactProofs'][0]['proof'])['contacts']
  source_bindings={u:sources[u]['sourceSHA256']for u in [left,right]if u in sources}
  for uid,sha in source_bindings.items():p=ROOT/sources[uid]['candidate']['path'];assert digest(p.read_bytes())==sha;refs.append(p)
  review=dict(sourceUid=left,otherUid=right,reviewer='Codex ROOT',reviewType='bounded-source-authored-opaque-interface-role'if native else'bounded-retained-BASIC-roof-native-vertical-wall-interface',interfaceRoleApproved=True,role=role,sourceSHA256ByUid=source_bindings,allCoordinateStreamContactRows=raw,viewedCoordinateStream=context['mode'],imagesActuallyInspected=views['images'],sourceFacetContext=context,requiresReviewedOriginalActivationGroup=native,basicCanopySuppressionApproved=False,requiresIndependentCollisionAndStreamingChecks=True,sourceGeometryChanges=0,sourcePoseChanges=0,evidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,installationApproved=False,publication=False,
   qualification='ROOT inspected all28local views on4pages alongside exact contact facets and current source identities. Accept only this authored bearing/opaque interface role with every point/line/area contact retained; no geometric separation, legal boundary, structural engineering, reverse-solid containment, collision-route or whole-scene acceptance is asserted. No contact tolerance or production gate changes. Native peers must activate together; BASIC roof/wall acceptance applies only to its unchanged roof and qualified post foundation.')
  save(out/(str(i)+'-interface-review.json'),review);reviews.append(dict(sourceUid=left,otherUid=right,interfaceRoleApproved=True,role=role))
 result=dict(uids=matrix['uids'],boundedInterfaceReviews=reviews,all28ViewsActuallyInspected=True,rawFloat32OnlyContactPreserved=True,retainedGrandScholarCanopyKept=True,sourceGeometryChanges=0,sourcePoseChanges=0,evidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalSupportDependencyApprovalPending=True,wholeGroupBrowserCollisionStreamingAcceptancePending=True,installationApproved=False,publication=False)
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('remaining_interface_reviews_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-thirteen-original-authored-joints-and-one-retained-canopy-wall-interface-review',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()
