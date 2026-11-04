"""DRAFT separate exactly-two-source held ledger snapshot; never update main pointer/J.
Default is pure local preflight. Root must review/authorize --apply before DB writes.
"""
import argparse,importlib.util,json,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
sys.path.insert(0,str(ROOT/'source-scripts/city/model-review-ledger'))
import ledger
BATCH='government-xl-beverly-k-p-separate-held-source-review-plan-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;INVENTORY=DOC/'source-review-inventory.json';DECISION=DOC/'held-source-decision.json';POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';UIDS=['landsd/233218:0','landsd/255543:0'];J='landsd/255939:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def protected(main):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE snapshot_id=%s OR uid=%s ORDER BY snapshot_id,uid',(main,J)).fetchall()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');parser.add_argument('--expected-main-snapshot');args=parser.parse_args();report=read(INVENTORY);decision=read(DECISION);parts=report['parts'];assert [p['uid']for p in parts]==UIDS and decision['uids']==UIDS;snapshot=digest(json.dumps(parts,sort_keys=True,separators=(',',':')).encode())[:16];assert snapshot==report['snapshotId']==decision['snapshotId'];sources={p['uid']:p['candidate']['sha256']for p in parts};assert sources=={'landsd/233218:0':'5fd92d6e2e691795087421f5a528eb2d641cc82141f8960da319a4072281abef','landsd/255543:0':'a780f09a03f515f9baf33d7d0408f663fe82080d51c1b4290f02dd4121124667'};assert all(p['candidate']['uid']==p['uid']and p['candidate']['objectId']==p['objectId']and p['candidate']['buildingCSUID']==p['csuid']for p in parts)
 for r in decision['evidenceRefs']:assert ref(ROOT/r['path'])==r
 if not args.apply:print(json.dumps(dict(draftSnapshot=snapshot,plannedHeldUIDs=UIDS,mainPointerChanges=0,installedJChanges=0,dbWrites=0)));return
 assert args.expected_main_snapshot;pointer=POINTER.read_bytes();main_id=json.loads(pointer)['snapshotId'];assert main_id==args.expected_main_snapshot and main_id!=snapshot;capture=ROOT/'docs/astra-city/government-import/government-xl-beverly-podium233218-complete-current-ground-capture-v1-20261011';scope=read(capture/'capture-scope.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';before_manifest=manifest.read_bytes();assert digest(before_manifest)==scope['currentManifest']['sha256'];before=protected(main_id)
 def fence():
  assert POINTER.read_bytes()==pointer and manifest.read_bytes()==before_manifest
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
  for r in decision['evidenceRefs']:assert ref(ROOT/r['path'])==r
 fence();receipts=[ROOT/r['path']for r in decision['evidenceRefs']if r['path'].endswith('/result.json')];assert len(receipts)==6
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for path in receipts:
   r=read(path);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  own=c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(snapshot,)).fetchall();assert not own or (set(r[0]for r in own)==set(UIDS)and all(r[1]in('pending','held')and r[2]==sources[r[0]]for r in own))
 claim=reservations.claim('beverly-k-p-separate-held-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  fence();ledger.seed(INVENTORY);assert protected(main_id)==before;entries=[]
  for row in decision['rows']:
   observation='Source-only evidence-supported held scope: '+json.dumps(dict(reasons=row['reasons'],revisitConditions=row['revisitConditions'],inProcess=False,installationApproved=False),sort_keys=True);entries.append((row['uid'],'held',str(DECISION),observation,None))
  recorded=ledger.record_many(snapshot,LOCAL/'reservation.json',entries,effort={'method':'scripted','reasoning_effort':'not-applicable','output_ref':str(DECISION.relative_to(ROOT))},request_id=BATCH+'-'+snapshot);fence();assert protected(main_id)==before
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');actual=c.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s ORDER BY uid',(snapshot,)).fetchall();assert [r[0]for r in actual]==UIDS and all(r[1]=='held'and r[2]==sources[r[0]]and r[3]['sha256']==ref(DECISION)['sha256']for r in actual)
  save(DOC/'held-ledger-neon.json',dict(snapshotId=snapshot,actualHeldRows=[dict(uid=r[0],review_state=r[1],source_sha256=r[2],result=r[3])for r in actual],recorded=recorded,mainSnapshotId=main_id,mainPointerBeforeAfterSHA256=digest(pointer),protectedMainAndAllJRows=len(before),protectedMainAndAllJRowSHA256=digest(json.dumps(before,sort_keys=True,separators=(',',':')).encode()),mainSnapshotAndAllJHistoryExactBeforeAfter=True,sourceOnly=True,newlyInstalled=0,currentAcceptance=False))
  spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);paths={INVENTORY,DECISION,DOC/'held-ledger-neon.json'};m.local_imports(Path(__file__),paths);paths.update([ROOT/'source-scripts/city/model-review-ledger/ledger.py',POINTER]);m.declared_refs(decision,paths);m.F.freeze(BATCH,'separate-exact-original-k-p-held-ledger-no-main-pointer-or-installed-j-change',sorted(paths),dict(uids=UIDS,snapshotId=snapshot,sourceOnly=True,newlyInstalled=0,currentAcceptance=False,installationApproved=False,mainSnapshotAndAllJHistoryUnchanged=True));print(json.dumps(dict(separateHeldSnapshot=snapshot,heldUIDs=UIDS,mainSnapshotUnchanged=True,installedJUnchanged=True,jobId=read(DOC/'result.json')['jobId'])))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
