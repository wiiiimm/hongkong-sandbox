"""Recover the exact 15KB original station model for podium-interface investigation."""
import argparse,sys,uuid,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,NATIVE_RUN,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-station-original-recovery-v1-20261028';LOOKUP='government-xl-southside-station-original-lookup-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/300867:0'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and 'building:'+UID in lease['resources']and not DOC.exists()and shutil.disk_usage(ROOT).free>=3*1024**3;_,pins=authenticate(BASE/LOOKUP);p=BASE/LOOKUP/'lookup.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];lookup=read(p);matches=[(s,x)for s in lookup['sheetsChecked']for x in s['matches']];assert len(matches)==1 and not lookup['stationCurrentlyInstalled'];sheet,row=matches[0];entry=row['candidate'];source=lookup['currentStationForm'];b=source['building'];assert b['uid']==entry['uid']==UID and entry['bytes']<=1024**2 and entry['glbBytes']<=20*1024**2
 tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==UID)==b
 for a,c in [('objectId','objectId'),('buildingCSUID','buildingCSUID'),('recordedBaseHeight','baseHeightHKPD'),('recordedTopHeight','topHeightHKPD')]:assert entry[a]==b[c]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(sheet['nativeCacheKey'],)).fetchone()==(sheet['nativeResultSHA256'],)
 inp=LOCAL/'recovery-inputs.json.gz';save(inp,dict(nativeRun=NATIVE_RUN,rows=[UID],sources={UID:source},native=[dict(sheet=sheet['sheet'],cacheKey=sheet['nativeCacheKey'],resultSha=sheet['nativeResultSHA256'],model=row['model'])]));prepared=shape_prepare.prepare(inp,LOCAL/'recovered',allow_source=True,workers=1,env_file=ROOT/'.env.modelling',reservation_receipt=lease);asset=LOCAL/'recovered/assets'/(entry['sha256']+'.glb.gz');recovered=not prepared['errors']and asset.exists()
 if recovered:assert digest(asset.read_bytes())==entry['sha256']and asset.stat().st_size==entry['bytes']
 result=dict(uids=[UID],recoveredCount=int(recovered),errors=prepared['errors'],methods=prepared['methods'],sourceKey=row['sourceKey'],nativeResultSHA256=sheet['nativeResultSHA256'],sheet=sheet['sheet'],candidate=entry,sourceAsset=dict(path=str(asset.relative_to(ROOT)),sha256=entry['sha256'])if recovered else None,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,qualification='Exact current record bindings and immutable indexed packed original bytes only. Source acquisition/conversion via existing guarded pipeline; no AI modelling, guard changes, identity/support/placement approval or catalogue writes.')
 save(DOC/'summary.json',result);refs=[Path(__file__),BASE/LOOKUP/'result.json',p,tile,inp,Path(shape_prepare.__file__)];refs.extend(f for f in(LOCAL/'recovered').rglob('*')if f.is_file()and f.suffix not in ['.zip']);assert reservations.owns(lease);module('southside_station_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-indexed-original-station-recovery-no-approval',refs,result);print(dict(recovered=recovered,errors=prepared['errors']),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-station-original-recovery-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
