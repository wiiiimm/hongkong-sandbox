"""Validate exact duplicate OLD review-routing rows; never exempt the new source.
The original inventory documents already have the inherited routing-metadata
contract. This binds duplicate old rows to those exact documents, not geometry.
"""
import gzip,hashlib,json
from lippo_exact_pending_embedded_geometry_reference_v1_20261011 import CAPTURE_PATH,CAPTURE_SHA,canonical,at
PREVIOUS_PATH='docs/astra-city/model-integration-20260909/source-review-inventory-0063f9701137947c.json'
PREVIOUS_SHA='118411c01674cb08bcc4b78888f65f68dbd6bfb0db5e6f358f9d45329ae511d9'
PENDING_PATH='docs/astra-city/model-integration-20260909/source-review-inventory-8d35b6f1d6f6bcdc.json'
PENDING_SHA='7ef3a395af02e6e0d97780ed847e269a7fd72886ea08c10328f38740b01f7ee4'
NEW_UID='landsd/239465:0'
NEW_RECORD=dict(candidate=dict(sha256='2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c'),
 classification='verified-unchanged-original-complete-source-and-current-terrain-roles',csuid='3551817554T20050430',knownHold=False,
 landmarkIds=[],name='Lippo Sun Plaza',objectId=239465,sourceProgress='prepared-for-review',uid=NEW_UID)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def verify_copies(context,previous,pending):
 assert context['fixtureFiles']['previousInventory']==previous and context['fixtureFiles']['pendingInventory']==pending
 assert context['exactLiveFiles']['previousInventory']==dict(path=PREVIOUS_PATH,sha256=PREVIOUS_SHA)
 assert context['exactLiveFiles']['pendingInventory']==dict(path=PENDING_PATH,sha256=PENDING_SHA)
 assert set(previous)==set(pending)=={'derivedFrom','inputs','issue','parts','qualification','snapshotId'}
 assert previous['snapshotId']=='0063f9701137947c' and previous['derivedFrom']=='2f36b4bc4b956c31'
 assert pending['snapshotId']=='8d35b6f1d6f6bcdc' and pending['derivedFrom']==previous['snapshotId']
 assert pending['inputs']==previous['inputs'] and pending['issue']==previous['issue']=='HKS-214'
 old=previous['parts'];new=pending['parts']
 assert len(old)==4944 and len(new)==4945
 assert len({r['uid'] for r in old})==len(old) and len({r['uid'] for r in new})==len(new)
 oldmap={r['uid']:r for r in old};newmap={r['uid']:r for r in new}
 assert NEW_UID not in oldmap and set(newmap)==set(oldmap)|{NEW_UID}
 assert newmap[NEW_UID]==NEW_RECORD and set(newmap[NEW_UID])==set(NEW_RECORD)
 assert all(newmap[uid]==r for uid,r in oldmap.items())
 assert canonical(old)==canonical([r for r in new if r['uid']!=NEW_UID])
 # Both copies are duplicates of their complete byte-pinned metadata documents.
 # Only OLD per-part routing rows inherit the existing inventory contract.
 pointers={f'/fixtureFiles/previousInventory/parts/{i}' for i in range(len(old))}
 pointers.update(f'/fixtureFiles/pendingInventory/parts/{i}' for i,r in enumerate(new) if r['uid']!=NEW_UID)
 newindex=next(i for i,r in enumerate(new) if r['uid']==NEW_UID)
 assert len(pointers)==9888 and f'/fixtureFiles/pendingInventory/parts/{newindex}' not in pointers
 return pointers,newindex
class BoundRoutingCopies:
 def __init__(self,capture_raw,previous_raw,pending_raw):
  assert sha(capture_raw)==CAPTURE_SHA and sha(previous_raw)==PREVIOUS_SHA and sha(pending_raw)==PENDING_SHA
  self.context=json.loads(gzip.decompress(capture_raw));self.previous=json.loads(previous_raw);self.pending=json.loads(pending_raw)
  self.pointers,self.newindex=verify_copies(self.context,self.previous,self.pending)
 def handles(self,document_path,pointer):return document_path==CAPTURE_PATH and pointer in self.pointers
 def verify_value(self,document_path,pointer,value):
  assert self.handles(document_path,pointer)
  assert value==at(self.context,pointer)
  return dict(pointer=pointer,completeDuplicateRoutingRowVerified=True,newCandidateGeometryExcluded=False)
 def proof(self):return dict(documentPath=CAPTURE_PATH,documentSHA256=CAPTURE_SHA,
  previousInventory=dict(path=PREVIOUS_PATH,sha256=PREVIOUS_SHA),pendingInventory=dict(path=PENDING_PATH,sha256=PENDING_SHA),
  completeOldRecordsExactlyPreserved=4944,completeDuplicateOldRoutingRows=9888,
  newCandidateUID=NEW_UID,newCandidatePointer=f'/fixtureFiles/pendingInventory/parts/{self.newindex}',
  newCandidateRemainsOrdinaryRecursive=True,allCurrentRoleStageAndGeometrySiblingsRemainOrdinaryRecursive=True,
  oldRoutingDuplicateCreatesNoIdentityPhysicalOrInstalledCredit=True,newNumericGeometryExclusions=0)
