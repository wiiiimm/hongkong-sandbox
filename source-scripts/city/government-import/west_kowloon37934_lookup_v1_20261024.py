"""Bind the newly nominated shaft to its exact pinned prepared original."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';prior=base/(prefix+'foreign-original-discovery-v2-20261024');_,pins=authenticate(prior);p=prior/'source-families.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];matches=[r for r in read(p)['rows']if r['uid']=='landsd/37934:0'];assert len(matches)==1;r=matches[0];m=r['model'];assert m['candidate']['uid']==r['uid']and m['candidate']['buildingCSUID']==r['currentBasicForm']['buildingCSUID']
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['cacheKey'],)).fetchone();assert record and record[0]==r['resultSHA256']and next(v for v in record[1]['models']if v['modelId']==m['modelId'])==m
    batch=prefix+'37934-lookup-v1-20261024';out=base/batch;assert not out.exists();result=dict(uids=[r['uid']],relatedUIDs=['landsd/255415:0','landsd/231056:0'],nativeCacheKey=r['cacheKey'],nativeResultSHA256=r['resultSHA256'],rows=[dict(uid=r['uid'],currentForm=r['currentBasicForm'],matchCount=1,matchedOriginalModels=[m])],identityApproved=False,installationApproved=False,sourceGeometryChanges=0)
    save(out/'lookup.json',result);module('west_37934_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-additional-original-shaft-lookup',[Path(__file__),prior/'result.json',p],result)

if __name__=='__main__':main()
