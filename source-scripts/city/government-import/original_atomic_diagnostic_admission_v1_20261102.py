"""Bind an already reviewed diagnostic original pair to its tested atomic fixture; no physical approval."""
import argparse,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','admission','fixture','lifecycle']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.admission,a.fixture,a.lifecycle])and not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 prior=take(a.admission,base/a.admission/'ROOT-DIAGNOSTIC-ADMISSION.json');assert prior['diagnosticOnly']and prior['sourceSpecificDiagnosticPreviewAdmitted']and prior['physicalAcceptance']is False and prior['publication']is False
 fixture=take(a.fixture,base/a.fixture/'summary.json');lifecycle=take(a.lifecycle,base/a.lifecycle/'summary.json');sources=prior['sourceSHA256ByUid'];assert fixture['sourceSHA256ByUid']==lifecycle['sourceSHA256ByUid']==sources
 assert fixture['onlyCatalogueFieldAdded']=='activationGroup'and all(fixture[k]==0 for k in ['approvalFlagChanges','supportDependencyChanges','terrainChanges','sourceGeometryChanges','sourcePoseChanges'])
 assert lifecycle['passed']and lifecycle['completeAtomicLifecyclePassed']and lifecycle['independentPerPeerFailuresPassed']and lifecycle['installationApproved']is False
 catpath=HERE/'local'/a.fixture/'catalogue.json';cat=take(a.fixture,catpath);assert {m['uid']:m['sha256']for m in cat['models']}==sources and all(m['activationGroup']==sorted(sources)for m in cat['models'])
 report=take(a.lifecycle,base/a.lifecycle/'report.json');assert report['passed']and not report['pageErrors']and len(report['cases'])==len(sources)+1
 result=copy.deepcopy(prior);result.update(requiredAtomicGroup=sorted(sources),atomicCatalogue=dict(path=str(catpath.relative_to(ROOT)),sha256=digest(catpath.read_bytes())),atomicFixture=a.fixture,atomicLifecycle=a.lifecycle,atomicLifecyclePassed=True,qualification=__doc__)
 save(out/'ROOT-DIAGNOSTIC-ADMISSION.json',result);module('atomic_diagnostic_admission_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'tested-atomic-original-private-observation-admission-only',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
