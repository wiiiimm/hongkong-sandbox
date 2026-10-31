"""Reject altered source identity, neighbour failures and missing terrain ownership."""
import copy
from run import ROOT,HERE,save
import kai_tak_cruise_functional_applicability_v1_20261019 as gate
real=gate.read
baseline=gate.qualify();assert baseline['sourceScopedApplicabilityAccepted']
cases=[('wrong-terminal-sha','ROOT-SOURCE-RELATIONSHIP-REVIEW.json',lambda d:d.update(sourceSHA256='0'*64)),('unaccepted-roof-interface','ROOT-INTERFACE-REVIEW.json',lambda d:d.update(sourceSpecificInterfaceInterpretationAccepted=False)),('new-neighbour-failure','neighbour-checks.json',lambda d:d['rows'][0].update(reasons=['new-ground-gap'])),('native-regression','native-neighbour-checks.json',lambda d:d['rows'][0].update(passed=False)),('lost-terrain-owner','metadata-equivalence.json',lambda d:d.update(replacementTargetUids=[])),('missing-loader-model','validation.json',lambda d:d.update(loaderAccepted=13))]
results=[]
for name,suffix,mutate in cases:
 def changed(path):
  d=copy.deepcopy(real(path))
  if path.name==suffix:mutate(d)
  return d
 gate.read=changed
 try:gate.qualify()
 except AssertionError:results.append(dict(case=name,rejected=True))
 else:raise AssertionError('Invalid evidence accepted: '+name)
 finally:gate.read=real
save(ROOT/'docs/astra-city/government-import/government-xl-kai-tak-cruise-functional-negative-checks-v1-20261019/checks.json',dict(baselinePassed=True,negativeChecks=results))
print('Baseline passes; all six altered-evidence cases reject.',flush=True)
