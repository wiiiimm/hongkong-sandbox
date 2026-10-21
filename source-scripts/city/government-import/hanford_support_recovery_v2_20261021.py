"""Recover the exact missing Hanford support bytes; no geometry edits or approval."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hanford-support-recovery-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/203884:0'

def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
    source=BASE/'government-xl-remaining-forty-podium-identity-v1-20261021'
    _,pins=authenticate(source);p=source/'selection.json.gz'
    assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    row=next(r for r in read(p)['rows']if r['uid']==UID)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        native=db.execute('SELECT i.sheet,r.result_sha,i.input_json FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone()
    assert native[:2]==('6-SW-11B',row['native']['resultSha']); native_input=native[2]
    oldname='government-xl-hanford-plaza-terrain-continuation-v4-20261005'
    old=HERE/'local'/oldname/'sheets/6-SW-11B'
    directory=old/'directory/result.json'
    prior=read(directory)
    assert digest(json.dumps([prior['sourceURL'],prior['etag'],prior['directorySHA256']],separators=(',',':')).encode())==native_input['sourceSha256']
    download=old/'original/download.json'
    helper=module('hanford_exact_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL
    result=helper.source_sheet('6-SW-11B',[row],prior,{},[(download,read(download))])
    asset=ROOT/result['assets'][0]['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    row['candidate']=dict(path=str(asset.relative_to(ROOT)))
    save(DOC/'selection.json.gz',dict(rows=[row],nativeResultSHA256=row['native']['resultSha']))
    save(DOC/'recovery.json',result)
    save(DOC/'native-input.json',native_input)
    save(DOC/'prior-wrapper-failure.json',dict(producer='hanford_support_recovery_v1_20261021.py',terminalExit=1,leaseReleased=True,reason='Historical terrain receipt did not pin the auxiliary 6-SW-11B directory. V2 binds source URL, ETag and directory SHA to exact native-stage input instead.',modelFailure=False))
    refs=[Path(__file__),source/'result.json',p,HERE/'hanford_support_recovery_v1_20261021.py',directory,download,HERE/'xl-second-pass.py',HERE.parent/'citywide-native/download.py',HERE.parent/'citywide-native/convert.py']
    refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
    assert reservations.owns(lease)
    summary=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],recoveredExactBytes=asset.stat().st_size,sourceGeometryChanges=0,installationApproved=False,permanentRejection=False)
    module('hanford_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-missing-original-support-recovery',refs,summary)
    print(summary,flush=True)

def main():
    if '--owned'in sys.argv:return owned()
    assert not DOC.exists()and not LOCAL.exists()
    c=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID,'source-recovery:'+BATCH],batch=BATCH,ttl=3600);assert c['ok']
    lease=c['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(p),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
