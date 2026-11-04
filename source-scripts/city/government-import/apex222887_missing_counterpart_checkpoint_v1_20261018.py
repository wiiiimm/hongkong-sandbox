"""Persist exact inventory absence without declaring a source permanently unavailable."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-apex-222887-original-recovery-v1-20261018';BATCH='government-xl-apex-222887-counterpart-lookup-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();data=read(OLD/'selection.json.gz');assert not data['rows']and len(data['missing'])==1
 row=data['missing'][0];b=row['currentSource']['building'];p=ROOT/'3d-viewer'/row['currentSource']['tile'];assert digest(p.read_bytes())==row['currentSource']['tileSHA256']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');matches=c.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+b['buildingCSUID'][:10]+'%')).fetchall()
 assert not matches
 log=Path('/tmp/apex222887-original-recovery-v1-20261018.log');DOC.mkdir();(DOC/'failed-recovery.log').write_bytes(log.read_bytes())
 save(DOC/'lookup.json',dict(uid=b['uid'],buildingCSUID=b['buildingCSUID'],inventoryRun=NATIVE_RUN,matchingProfiles=matches,qualification='No exact counterpart in this indexed inventory; not proof of universal source absence or permanent non-installability.',fullAcceptance=False))
 refs=[Path(__file__),OLD/'selection.json.gz',p,HERE/'apex222887_original_recovery_v1_20261018.py'];r=module('apex_missing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-neighbour-exact-indexed-counterpart-absence-v1',refs,dict(uids=[b['uid'],'landsd/227942:0'],sourceGeometryChanges=0,newlyInstalled=0,fullAcceptance=False,nextStep='Investigate estimated basic-canopy placement and original Apex component coverage; do not suppress or mark permanently unfixable from this inventory absence.'));print(r['jobId'],flush=True)
if __name__=='__main__':main()
