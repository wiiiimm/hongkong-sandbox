import sys,json,argparse,subprocess
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'source-scripts/city/government-import'))
from run import read,save,connect
import citywalk134332_freeze_saved_source_orientation_context_v2_20261013 as Q
p=Path(__file__).parent;r=read(Q.C.OUT/'result.json');assert r['jobId']=='43fd031e415b5527e04304114689ef8d72cca6b19d1acc6e8484328598952197';assert Q.C.ref(Q.C.OUT/'result.json')['sha256']=='a5ce9824eeda21c8623b216944228d827b0792eac5cdd12cfa0204e517e1a711'
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 groups=db.execute('SELECT row_to_json(g) FROM astra_modelling.reservation_groups g WHERE batch=%s',(Q.BATCH,)).fetchall()
 assert len(groups)==1 and groups[0][0]['released_at']is not None
 group=groups[0][0];retainedRows=db.execute('SELECT resource FROM astra_modelling.reservations WHERE token=%s',(group['token'],)).fetchall();assert not db.execute('SELECT 1 FROM astra_modelling.reservations r JOIN astra_modelling.reservation_groups g USING(token) WHERE r.token=%s AND g.released_at IS NULL AND g.lease_until>clock_timestamp()',(group['token'],)).fetchone()
assert not Q.G.reservations.owns(group)
for e in r['evidenceRefs']:assert Q.C.ref(R/e['path'])==e
before=read(Q.C.OUT/'protected-current-state-for-source-context-freeze.json');assert Q.G.inputs(argparse.Namespace(expected_manifest=Q.C.MANIFEST))==before
raw=subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True);hits=[x for x in raw.splitlines()if '/tmp/astra-city-venv/bin/python source-scripts/city/government-import/citywalk134332_freeze_saved_source_orientation_context_v2_20261013.py' in x and not ('/bin/bash' in x or 'python3 -' in x)]
assert not hits,hits
save(p/'independent-Neon-all283refs-current-release-audit-v3.json',dict(jobId=r['jobId'],result=Q.C.ref(Q.C.OUT/'result.json'),exactNeonComplete=True,allLiteralRefsVerified=len(r['evidenceRefs']),current19UID1704RowsUnchanged=True,releasedReservationGroup=group,releasedTokenResourceRowsRetained=len(retainedRows),noActiveTokenResourceRows=True,ownsFalse=True,noKnownFreezerPIDs=True,terminalSession16919Exit0=True,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
print(json.dumps(dict(jobId=r['jobId'],allLiteralRefsVerified=len(r['evidenceRefs']),released=True,noPIDs=True,audit=Q.C.ref(p/'independent-Neon-all283refs-current-release-audit-v3.json'))),flush=True)
