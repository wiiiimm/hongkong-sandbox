"""Look up complete cached government records for exact current nearby form prefixes.

Discovery only: no acquisition, absence/corruption conclusion or approval transfer.
"""
from pathlib import Path
import argparse
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    _,pins=authenticate(base/a.scope);refs=[Path(__file__),base/a.scope/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take(base/a.scope/'summary.json');assert a.uid in scope['uids']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==scope['currentManifestSHA256'];refs.append(manifest)
    forms=take(base/a.scope/(a.uid.split('/')[1]+'-forms.json.gz'))
    by={f['building']['uid']:f['building'] for f in forms}
    assert a.uid in by and len(by)==len(forms)
    prefixes=sorted({str(f['buildingCSUID'])[:10] for f in by.values() if f.get('buildingCSUID')})
    assert prefixes and all(len(v)==10 and v.isdigit() for v in prefixes)
    for tile in {f['tile'] for f in forms}:
        path=ROOT/'3d-viewer'/tile;take(path)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        rows=db.execute("""SELECT i.sheet,r.cache_key,r.result_sha,model
          FROM astra_modelling.native_stage_members m
          JOIN astra_modelling.native_stage_results r USING(cache_key)
          JOIN astra_modelling.native_stage_inputs i USING(cache_key)
          CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') model
          WHERE m.run_id=%s AND substring(model->>'modelId' from 2 for 10)=ANY(%s)
          ORDER BY i.sheet,r.cache_key,model->>'modelId'""",(NATIVE_RUN,prefixes)).fetchall()
    records=[];seen=set()
    for sheet,key,sha,model in rows:
        identity=(key,model['modelId']);assert identity not in seen;seen.add(identity)
        records.append(dict(sheet=sheet,cacheKey=key,nativeResultSHA256=sha,model=model))
    grouped=[]
    for uid,form in sorted(by.items()):
        prefix=str(form.get('buildingCSUID') or '')[:10]
        matches=[r for r in records if r['model']['modelId'][1:11]==prefix]
        grouped.append(dict(uid=uid,name=form.get('name'),buildingCSUID=form.get('buildingCSUID'),prefix=prefix,modelIds=[r['model']['modelId'] for r in matches],records=len(matches),maximumCachedFaces=max((r['model']['triangles'] for r in matches),default=None)))
    save(out/'complete-cached-records.json.gz',dict(nativeRun=NATIVE_RUN,rows=records))
    result=dict(uids=[a.uid],currentManifestSHA256=scope['currentManifestSHA256'],nativeRun=NATIVE_RUN,queriedPrefixes=prefixes,currentForms=grouped,matchedCachedRecords=len(records),sourceGeometryChanges=0,acquisitionPerformed=False,identityApproved=False,installationApproved=False,permanentRejection=False,qualification='Complete cached records for every exact ten-digit geographic prefix nominated by the authenticated current source scope. Current cached run only; no claim of complete current provider availability, source ownership, missing companion coverage or source corruption. Every prospective companion still needs exact UID/ObjectID/CSUID routing and original geometry/current scene checks.')
    save(out/'summary.json',result)
    module('companion_index_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-nearby-prefix-cached-companion-discovery',refs,result)
    print(dict(matchedCachedRecords=len(records),currentForms=grouped),flush=True)


if __name__=='__main__':main()
