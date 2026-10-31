"""Replay original import gates against exact current pier identity and runtime evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-original-policy-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,file):
 folder=BASE/name;_,ps=authenticate(folder);p=folder/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
selection=take('government-xl-next-twenty-current-terrain-v6-20261021','selection.json.gz')['rows'];policy=module('piers_existing_policy',HERE/'acceptance-policy.py');rows=[]
for uid,label in [('landsd/118230:0','harbourfront')]:
 row=next(r for r in selection if r['uid']==uid);source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256'];refs.append(source)
 form=row['source'];p=ROOT/'3d-viewer'/form['tile'];assert digest(p.read_bytes())==form['tileSHA256'];assert next(b for b in read(p)['buildings']if b['uid']==uid)==form['building'];refs.append(p)
 identity=take('government-xl-two-harbourfront-attached-boundary-current-identity-v3-20261021','identity-proof.json');assert identity['passed']and identity['sourceSHA256']==row['sourceSHA256']
 name='government-xl-harbourfront-tower-current-runtime-v2-20261021';report=take(name,'metrics.json');metric=next(r for r in report['rows']if r['uid']==uid);foundation=take(name,'foundation.json')
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h;refs.append(ROOT/p)
 # This state derives only from the authenticated successful runtime job above.
 reasons=policy.reasons({**row,'state':'runtime-validated-awaiting-acceptance','identityProof':identity['proof']},metric,report['profiles']['mobile'])
 if foundation['completeTerrainTriangles']!=foundation['triangles']:reasons.append('incomplete-foundation')
 if foundation['fullyBuriedTriangles']or foundation['fullyBuriedUpwardTriangles']:reasons.append('buried-foundation')
 if foundation['minimumGapM']<-.5:reasons.append('foundation-clearance')
 rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],originalPolicyPassed=not reasons,reasons=reasons,sourceGeometryChanges=0))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.append(HERE/'acceptance-policy.py');summary=dict(uids=[r['uid']for r in rows],rows=rows,installationApproved=False,qualification='Existing identity/contact/terrain/whole-foundation/mobile-budget gates only. Complete neighbour delta, all visual/browser evidence and qualified publication still required.')
save(DOC/'summary.json',summary);r=module('piers_policy_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-original-import-policy-replay',list(dict.fromkeys(refs)),summary);print(dict(jobId=r['jobId'],rows=rows),flush=True)
