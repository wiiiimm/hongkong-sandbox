"""Exact original-pool sibling review; all other publisher checks remain intact."""
from contextlib import contextmanager
from run import ROOT, read, digest, connect
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-sham-shui-po-pool-sibling-surface-review-v1-20261017'
CANDIDATE='9497e8aa17213aa7e2242907398e73e34f4d9e0a8d3b15411cc9993934033311'
RETAINED='4e4f39f73d876a4a533b3fcc924ac5b61ff1d503833c69008d70e77f2a958de2'

def verify():
 result=read(DOC/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 pins={}
 for ref in result['evidenceRefs']:
  assert ref['path'] not in pins or pins[ref['path']]==ref['sha256']
  pins[ref['path']]=ref['sha256']
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha,path
 review=read(DOC/'ROOT-SIBLING-SURFACE-REVIEW.json')
 assert str((DOC/'ROOT-SIBLING-SURFACE-REVIEW.json').relative_to(ROOT)) in pins
 assert review['status']=='reviewed-exact-native-sibling-overlap'
 assert review['candidate']['sha256']==CANDIDATE and review['retained']['sha256']==RETAINED
 assert review['intersectionCells']==[481,380,482,382]
 assert review['combinedUncoveredAreaM2']<1e-8 and review['maxRayPlaneAgreementErrorM']<.004
 assert review['completeBasicActors']==84 and review['retainedPatchByteUnchanged']
 assert set(review['completeNativeResolved'])=={'landsd/113733:0','landsd/138091:0','landsd/99395:0'}
 models=review['retainedTargetActors'];assert len(models)==8 and [m['uid']for m in models if m['touchesCandidateDomain']]==['landsd/99395:0']
 for name,sha in [('candidate',CANDIDATE),('retained',RETAINED)]:
  assert digest((ROOT/review[name]['path']).read_bytes())==sha
 return read(ROOT/review['candidate']['path']),read(ROOT/review['retained']['path'])

def checked_overlap(delegate,candidate,retained,p,others):
 # Equality covers every vertex/index and all placement metadata, not just extent.
 if p!=candidate:return delegate(p,others)
 matches=[q for q in others if q==retained]
 assert len(matches)==1,'Exact reviewed retained sibling must appear once'
 assert p['coarseCells']==[481,376,488,382] and retained['coarseCells']==[476,380,482,384]
 return delegate(p,[q for q in others if q!=retained])

@contextmanager
def reviewed_publisher(pub):
 candidate,retained=verify();original=pub.check_patch_overlap
 pub.check_patch_overlap=lambda p,others:checked_overlap(original,candidate,retained,p,others)
 try:yield
 finally:pub.check_patch_overlap=original
