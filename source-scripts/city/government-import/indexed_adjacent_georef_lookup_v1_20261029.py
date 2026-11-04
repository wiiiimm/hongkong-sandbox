"""Search the whole pinned model-size index for nominated adjacent GeoRefs."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','lookup']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    src=base/a.lookup;_,pins=authenticate(src);path=src/'lookup.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    data=read(path);refs=[Path(__file__),src/'result.json',path];rows=[]
    with connect()as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for row in data['rows']:
            f=row['currentForm'];prefix=f['buildingCSUID'][:10];assert len(prefix)==10 and prefix.isdigit()
            tile=ROOT/'3d-viewer/city/data/tiles'/(f['tile']+'.json');assert next(b for b in read(tile)['buildings']if b['uid']==f['uid'])==f;refs.append(tile)
            matches=db.execute('SELECT cache_key,model_id,sheet,source_state,viewer_uid,source_hold_reason FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s ORDER BY sheet,cache_key,model_id',(NATIVE_RUN,'B'+prefix+'%')).fetchall()
            rows.append(dict(uid=f['uid'],buildingCSUID=f['buildingCSUID'],geoRefPrefix=prefix,matches=[dict(zip(['cacheKey','modelId','sheet','sourceState','viewerUid','sourceHoldReason'],r))for r in matches]))
    result=dict(uids=[r['uid']for r in rows],nativeRun=NATIVE_RUN,rows=rows,scope='All records in the pinned native_model_sizes run, no sheet or prior shape-match filter',installationApproved=False,identityAccepted=False,permanentRejection=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Read-only indexed GeoRef nomination. An empty index match is not proof of absence from unindexed/raw government archives. No acquisition, type/identity approval, support suppression or publication.')
    save(out/'summary.json',result)
    module('indexed_georef_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'whole-pinned-index-adjacent-raw-georef-nomination',refs,result)
if __name__=='__main__':main()
