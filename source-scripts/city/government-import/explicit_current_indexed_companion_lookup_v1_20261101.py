"""Bind one explicit indexed companion to an unchanged current source form.

Nomination only: no acquisition, conversion, identity/placement or publication approval.
"""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','uid','model-id','cache-key']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/a.batch/'reservation.json';assert not out.exists()
    resources=sorted({'building:'+a.uid,'native-model:'+a.cache_key+'/'+a.model_id})
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('explicit-indexed-companion-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=1800);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    _,pins=authenticate(base/a.capture);selection_path=base/a.capture/'selection.json.gz';assert digest(selection_path.read_bytes())==pins[str(selection_path.relative_to(ROOT))]
    refs=[Path(__file__),base/a.capture/'result.json',selection_path];found=[]
    for tile in sorted({r['source']['tile']for r in read(selection_path)['rows']}):
        path=ROOT/'3d-viewer'/tile;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
        found += [dict(building=b,tile=tile,tileSHA256=digest(path.read_bytes()))for b in read(path)['buildings']if b['uid']==a.uid]
    assert len(found)==1;source=found[0];b=source['building']
    with connect()as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        record=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members n USING(cache_key) WHERE n.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,a.cache_key)).fetchone()
        assert record;sha,native=record;models=[m for m in native['models']if m['modelId']==a.model_id];assert len(models)==1;model=models[0]
        matches=[m for m in model.get('matching',{}).get('viewerMatches',[])if m['uid']==a.uid and m['objectId']==b['objectId']and m['buildingCSUID']==b['buildingCSUID']];assert len(matches)==1
        entry=model['candidate'];assert entry['uid']==a.uid and entry['objectId']==b['objectId']and entry['buildingCSUID']==b['buildingCSUID']and entry['recordedBaseHeight']==b['baseHeightHKPD']and entry['recordedTopHeight']==b['topHeightHKPD']
        assert entry['sha256']==model['asset']['sha256']and entry['bytes']==model['asset']['bytes']and entry['publicationApproved']is False and entry['placementReviewed']is False
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes());refs.append(manifest)
    current=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert not any(m['uid']==a.uid for m in current),'Already installed; reuse current original instead of acquisition'
    result=dict(uids=[a.uid],nativeRun=NATIVE_RUN,currentManifestSHA256=manifest_sha,rows=[dict(uid=a.uid,source=source,matches=[dict(sourceKey=a.cache_key+'/'+a.model_id,nativeCacheKey=a.cache_key,nativeResultSHA256=sha,model=model)])],nominationOnly=True,identityAccepted=False,sourceGeometryChanges=0,sourcePoseChanges=0,acquisition=False,conversion=False,installationApproved=False,publication=False,qualification=__doc__+' Exact current tile bytes and unique UID/ObjectID/CSUID/source-height tuple match the pinned native run. Historical owner capture nominates its tile only; no old scene/terrain approval transfers.')
    assert reservations.owns(lease)and digest(manifest.read_bytes())==manifest_sha;save(out/'lookup.json',result)
    module('explicit_current_indexed_companion_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-indexed-original-companion-nomination',refs,result)
    print(dict(uid=a.uid,modelId=a.model_id,triangles=model['triangles'],identityAccepted=False),flush=True)
if __name__=='__main__':main()
