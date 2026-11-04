"""Summarise completed saved-contact evidence without claiming installation credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-saved-support-resolution-summary-v1-20261022';DOC=BASE/BATCH
PATHS={'landsd/137130:0':'government-xl-saved-support-137130-0-paths-v1-20261022','landsd/339808:0':'government-xl-saved-support-339808-0-paths-v1-20261022'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-saved-support-contact-batch-v1-20261022';batch=take(n,BASE/n/'summary.json');rows=[]
 for row in batch['rows']:
  assert row['status']=='completed';uid=row['uid'];paths=take(PATHS[uid],BASE/PATHS[uid]/'summary.json')if uid in PATHS else None;direct=row['finiteIncidentContacts'];bounded=paths['finiteEndpointBoundedPaths']if paths else 0;total=row['unresolvedWitnesses'];assert direct+bounded<=total
  rows.append(dict(uid=uid,rawUnresolvedWitnesses=total,positiveFiniteIncidentContacts=direct,finiteEndpointBoundedPaths=bounded,remainingUnexplained=total-direct-bounded,contactEvidenceComplete=total==direct+bounded,installationApproved=False,nextAction='Fresh whole-source foundation, current coordinate/support binding, identity and publication checks'if total==direct+bounded else'Investigate exact missing attachment or alternative original support; preserve current source'))
 result=dict(uids=[r['uid']for r in rows],rows=rows,totalWitnesses=sum(r['rawUnresolvedWitnesses']for r in rows),explainedWitnesses=sum(r['positiveFiniteIncidentContacts']+r['finiteEndpointBoundedPaths']for r in rows),remainingWitnesses=sum(r['remainingUnexplained']for r in rows),completeContactPairs=sum(r['contactEvidenceComplete']for r in rows),newInstallations=0,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Source-contact stage only. Exact historical captures/witnesses retained; all current identity, four-coordinate foundation/runtime, neighbour and publication obligations remain.')
 save(DOC/'summary.json',result);module('support_resolution_summary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'scripted-original-support-resolution-summary',refs,result);print({k:v for k,v in result.items()if k not in ['rows','uids','qualification']},flush=True)
if __name__=='__main__':main()
