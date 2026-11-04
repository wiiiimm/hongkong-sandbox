"""Find pinned cached government originals for exact current nearby source forms.

Availability nominations only: no source identity, placement or installation credit.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,NATIVE_RUN,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--uid',action='append',required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.scope])and not doc.exists()
    receipt,pins=authenticate(base/a.scope);sp=base/a.scope/'summary.json';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
    scope=read(sp);mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==scope['currentManifestSHA256']
    refs=[Path(__file__),base/a.scope/'result.json',sp,mp];wanted=set(a.uid);assert len(wanted)==len(a.uid);forms={}
    for row in scope['rows']:
        p=base/a.scope/(row['uid'].split('/')[1]+'-forms.json.gz');assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
        for item in read(p):
            f=item['building']
            if f['uid']in wanted:
                tp=ROOT/'3d-viewer'/item['tile'];assert digest(tp.read_bytes())==item['tileSHA256'];assert next(b for b in read(tp)['buildings']if b['uid']==f['uid'])==f;refs.append(tp)
                assert f['uid']not in forms or forms[f['uid']]==f;forms[f['uid']]=f
    assert set(forms)==wanted;rows=[];queries=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');db.execute("SET LOCAL statement_timeout='120s'")
        for uid,f in sorted(forms.items()):
            prefix='B'+f['buildingCSUID'][:10]
            profiles=db.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,prefix+'%')).fetchall()
            queries.append(dict(uid=uid,prefix=prefix,preparedProfiles=len(profiles)))
            for key,sheet in profiles:
                found=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone();assert found
                sha,result=found
                for model in result['models']:
                    if model['modelId'].startswith(prefix):
                        candidates=[v for v in model.get('matching',{}).get('officialCandidates',[])if v.get('objectId')==f['objectId']and v.get('buildingCSUID')==f['buildingCSUID']]
                        rows.append(dict(uid=uid,source=f,nativeStageKey=key,nativeStageSHA256=sha,sheet=sheet,model=model,exactOfficialCandidates=candidates,identityApproved=False))
    assert digest(mp.read_bytes())==scope['currentManifestSHA256']
    result=dict(uids=sorted(wanted),candidateOwners=receipt['uids'],rows=rows,queries=queries,nativeRun=NATIVE_RUN,missingPreparedPrefixes=sorted(wanted-{r['uid']for r in rows}),sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Exact current source-form and pinned native-run GeoRef-prefix nominations only. Positive exact official candidates are recorded separately; neither names nor prefix availability grants identity/physical acceptance. Missing prepared prefixes do not establish provider absence.')
    save(doc/'nominations.json',result)
    module('companion_availability_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-companion-cached-original-availability',list(dict.fromkeys(refs)),result)
    print([(r['uid'],r['model']['modelId'],r['model']['triangles'],len(r['exactOfficialCandidates']))for r in rows],flush=True)

if __name__=='__main__':main()
