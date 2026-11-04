"""Adapt an exact raw adjacent nomination for the existing cached-only selector."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser()
    for k in ['batch','lookup','scope','owner']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    lookup=take(a.lookup,base/a.lookup/'lookup.json');items=take(a.scope,base/a.scope/(a.owner.split('/')[1]+'-forms.json.gz'))
    forms={r['building']['uid']:r for r in items};rows=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        current=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(lookup['nativeCacheKey'],)).fetchone()
        assert current and current[0]==lookup['nativeResultSHA256']
        for row in lookup['rows']:
            uid=row['uid'];source=forms[uid];assert row['currentForm']==source['building']and len(row['matchedOriginalModels'])==1
            model=row['matchedOriginalModels'][0];assert next(m for m in current[1]['models']if m['modelId']==model['modelId'])==model
            assert model.get('candidate')and model['candidate']['uid']==uid
            tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256'];refs.append(tile)
            assert next(r for r in read(tile)['buildings']if r['uid']==uid)==source['building']
            match=dict(nativeCacheKey=lookup['nativeCacheKey'],nativeResultSHA256=lookup['nativeResultSHA256'],sourceKey=lookup['nativeCacheKey']+'/'+model['modelId'],model=model)
            rows.append(dict(uid=uid,source=source,matches=[match]))
    result=dict(uids=[r['uid']for r in rows],rows=rows,identityAccepted=False,physicalAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Only exact current form, candidate UID and complete native cached-record equality are bound. This is a nomination for existing packed byte recovery, not source/placement/support acceptance.')
    save(out/'lookup.json',result)
    module('raw_adjacent_nomination_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-raw-adjacent-nomination-for-cached-only-selection',refs,result)


if __name__=='__main__':main()
