"""Reject changed source scope, unreviewed failures and lost neighbour evidence."""
import copy,json
import heritage165054_joint_private_stage_v1_20261015 as s

def main():
 data,*_=s.inputs();assert s.qualify(*data)['privateStageQualified']
 cases=[('wrong-original',lambda d:d[1].update(sourceSHA256='0'*64)),('identity-negative',lambda d:d[1].update(passed=False)),('strict-foundation-negative',lambda d:d[0].update(strictFoundationAccepted=False)),('new-unreviewed-face',lambda d:d[2]['rows'][0]['worlds'][0]['findings']['candidateOrdinaryUnproved'].append(188)),('missing-source-world',lambda d:d[2]['rows'][0]['worlds'].pop()),('uncovered-source',lambda d:d[2]['rows'][0]['worlds'][0]['findings']['candidateUncovered'].append(188)),('new-neighbour-failure',lambda d:d[2]['rows'][1]['worlds'][0]['findings']['currentClearCandidateUnproved'].append(0)),('lost-original-baseline',lambda d:d[5].update(originalBeforeStatePreserved=False)),('shelter-finite-failure',lambda d:d[6]['rows'][0]['candidateUnproved'].append(0)),('exterior-changed',lambda d:d[7].update(strictOutsideParentAndActorROIDrawUnchanged=False)),('blanket-source-exemption',lambda d:d[4].update(otherFacesApproved=True))]
 for name,mutate in cases:
  d=copy.deepcopy(data);mutate(d)
  try:s.qualify(*d)
  except AssertionError:continue
  raise AssertionError('Accepted adverse case: '+name)
 out=s.BASE/(s.BATCH+'-proposal');assert not (out/'guard-tests.json').exists();s.save(out/'guard-tests.json',dict(passed=True,positiveActualCase=1,rejectedAdverseCases=[n for n,_ in cases],caller=s.ref(s.Path(s.__file__)),test=s.ref(s.Path(__file__)),noSourceGeometryOrDBChanges=True));print(json.dumps(dict(passed=True,cases=1+len(cases))))
if __name__=='__main__':main()
