"""Bounded source-specific original interface interpretation, not publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-park-interface-review-v1-20261018';DOC=BASE/BATCH
CONTACT=BASE/'government-xl-olympian-two-park-four-world-contacts-v1-20261018';VIEWS=BASE/'government-xl-olympian-two-park-interface-views-v1-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CONTACT,VIEWS,BASE/'government-xl-olympian-two-park-podium-identity-review-v1-20261018']:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CONTACT/'contacts.json.gz')['rows'];assert len(rows)==24
 for r in rows:
  assert r['proof']['wallIntersections']==0
  for d in r['details']:
   if r['uid']=='landsd/82096:0':assert d['path']and d['path']['endpointPassed']and len(d['path']['original']['witness']['faces'])==1
   else:assert any(x['supportUid']=='landsd/72277:0'for x in d['contacts'])
 summary=read(CONTACT/'summary.json');assert summary['lowerContactChecks']==400 and summary['finiteFacePathChecks']==36 and summary['allDiagnosticContactsResolved']
 selection=read(BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018/selection.json.gz')['rows'];bindings=[]
 for row in selection:
  p=read(BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018'/(row['uid'].split('/')[1]+'-identity.json'))['proof'];bindings.append({k:p[k]for k in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']})
 review=dict(uids=summary['uids'],sourceSpecificInterfaceInterpretationAccepted=True,bindings=bindings,rawCanonicalFailuresRetained=True,reviewBasis=['ROOT inspected all six original lower-assembly plan/oblique views. Tower flagged points occur at the original lower facade edges over the original multi-level podium; lower finite podium faces, rather than the highest roof above them, provide all100 lower contacts. The same source face layers satisfy400 coordinate-mode checks.', 'Park Resort has127 direct canonical contacts and nine lower perimeter points. Each of those nine belongs to a single original wall/facade face that also has a verified podium contact; no graph path through remote upper floors is used. Both endpoints remain on that finite original face within the existing1mm membership tolerance in all four modes (36checks). Source views show the rectangular/circular clubhouse perimeter intersecting the adjoining podium levels.', 'No source wall intersections were reported in the canonical checks. Whole-source foundation evidence already passes for the six buildings against the preceding candidate; it must be renewed against the final terrain candidate.', 'Accept this exact original architectural interface only. This is not engineering certification or a general connected-mesh waiver. All raw highest-surface warnings remain recorded. Final terrain, neighbour, browser, collision and publication acceptance remain separate.'],modelGeometryChanges=0,aiGeometryModelling=False,sourceInterpretationUsedAI=True,fullAcceptance=False,publicationApproved=False,newlyInstalled=0)
 save(DOC/'ROOT-INTERFACE-REVIEW.json',review);refs.extend(ROOT/p for p in pins)
 out=module('park_interface_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-park-exact-original-interface-review-v1',list(set(refs)),review);print(out['jobId'],flush=True)
if __name__=='__main__':main()
