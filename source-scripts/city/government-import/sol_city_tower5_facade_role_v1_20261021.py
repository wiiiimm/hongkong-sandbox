"""Bounded original-facade role review; rendered attachment verification remains required."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-tower5-facade-role-v1-20261021';DOC=BASE/BATCH
VIEW=BASE/'government-xl-sol-city-tower5-facade-view-v1-20261021';ROUTE=BASE/'government-xl-sol-city-tower5-route-heights-v1-20261021';SOURCE=BASE/'government-xl-sol-city-complete-capture-v1-20261021'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [VIEW,ROUTE,SOURCE]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
context=read(VIEW/'context.json');routes=read(ROUTE/'268424:0.json.gz');source=next(r for r in read(SOURCE/'selection.json.gz')['rows']if r['uid']=='landsd/268424:0')
assert len(routes['rows'])==context['witnessCount']==17 and routes['uid']==source['uid']
assert all(r['bestRoute'] and r['bestRoute']['excessAboveOwnEndpointM']==0.11099624633789062 for r in routes['rows'])
assert sorted({i for r in routes['rows']for i in r['incidentFaces']})==context['incidentFaceIds']
image=VIEW/'original-rim-context.png'
review=dict(uid=source['uid'],sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=routes['sourceWorldSHA256'],reviewer='Codex ROOT',reviewType='bounded-original-facade-functional-context',roleInterpretationAccepted=True,reviewedRole='Lower closure strip of a projecting facade feature attached to the tower body',witnesses=routes['rows'],exactIncidentFaceIds=context['incidentFaceIds'],rawEndpointBoundFailureRetained=True,rawStrictInterfaceFailureRetained=True,imagesActuallyInspected=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],basis=[
'ROOT inspected the exact seventeen flagged witnesses and all their incident original faces from four angles, with the surrounding tower facade and podium shown at unchanged coordinates. Visual-only plane clipping removes occluding context; no source asset is edited.',
'The flagged faces form the lower closure strip of a projecting facade feature. The source continues into vertical tower faces, and similar projecting features repeat higher on the facade. They are not independently identified ground-bearing footings. This is an architectural source-context interpretation, not structural certification or a precise balcony/equipment label.',
'The existing exact graph already connects every witness to a positive finite podium contact, but its lowest known gateway rises 0.11099624633789062m above the chosen endpoint-height bound. Preserve that numerical failure. The review does not increase the bound, turn those failed paths into passing bounded paths, or use small distance alone as acceptance.',
'For these exact original witness faces, an attachment proof may follow their actual authored tower connection above the witness rather than demand direct ground contact. It must independently verify the complete path inside original faces, exact finite joins, positive terminal contact, unchanged source identity and each actual rendered arithmetic representation. No general permission is granted to waive support failures on other faces or sources.'
],requiredNextChecks=['Verify exact attached-feature paths and corresponding witness/face bindings in literal, left-associated Float32 and balanced Float32 coordinates','Account separately for all other raw support witnesses and wall intersections','Retain whole-foundation, original source collision, neighbour, runtime, browser and publication checks'],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,publicationApproved=False)
save(DOC/'role-review.json',review)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
module('sol_facade_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-facade-role-interpretation',list(dict.fromkeys(refs)),dict(uids=[source['uid']],roleInterpretationAccepted=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0))
