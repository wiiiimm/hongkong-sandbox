"""Bind an exact recovered source sheet to current forms, without approval."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','acquire','inventory']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.acquire,a.inventory]) and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    recovered=take(a.acquire,base/a.acquire/'summary.json');assert recovered['sourceRecovered']
    inventory=take(a.inventory,base/a.inventory/'complete-bounds.json.gz')
    mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(a.inventory,mp);tiles={t['id']:t['url'] for t in manifest['tiles']}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        key=recovered['nativeCacheKey'];assert db.execute('SELECT 1 FROM astra_modelling.native_stage_members WHERE run_id=%s AND cache_key=%s',(NATIVE_RUN,key)).fetchone()
        sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==recovered['nativeResultSHA256']
        sheet=db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
    rows=[]
    for item in recovered['rows']:
        form=item['currentForm'];uid=form['uid'];tile=ROOT/'3d-viewer'/tiles[form['tile']]
        assert digest(tile.read_bytes())==inventory['currentFormTileHashes'][str(tile.relative_to(ROOT))]
        assert [f for f in read(tile)['buildings'] if f['uid']==uid]==[form];refs.append(tile)
        model=next(m for m in native['models'] if m['modelId']==item['model']['modelId']);assert model==item['model']
        assert any(v['uid']==uid and v.get('buildingCSUID')==form['buildingCSUID'] and v.get('objectId')==form['objectId'] for v in model['matching']['viewerMatches'])
        entry=deepcopy(model['candidate']);assert entry['uid']==uid and entry['buildingCSUID']==form['buildingCSUID'] and entry['objectId']==form['objectId']
        assert not any(entry.get(k) for k in ['identityReviewApproved','sourceIdentityReviewed','placementReviewed','publicationApproved','variantId','suppressesBuildingUids'])
        entry.update(proceduralWindows=False,rootTranslation=[-834500,0,816500],sourceTile=sheet,
                     sourceBaseHeight=form['baseHeightHKPD'],sourceTopHeight=form['topHeightHKPD'])
        path=ROOT/item['asset']['path'];assert digest(path.read_bytes())==item['sourceSHA256']==entry['sha256']==model['asset']['sha256'];refs.append(path)
        assert path.stat().st_size==entry['bytes']==model['asset']['bytes'] and item['completeSourceFaces']==model['triangles']
        rows.append(dict(uid=uid,modelId=model['modelId'],triangles=model['triangles'],sourceSHA256=entry['sha256'],originalGeometryOnly=True,
             source=dict(building=form,tile=tiles[form['tile']],tileSHA256=digest(tile.read_bytes())),
             native=dict(cacheKey=key,resultSha=sha,model=model),candidate=dict(path=str(path.relative_to(ROOT)),entry=entry)))
    wanted={r['uid'] for r in rows};assert wanted and len(wanted)==len(rows)
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[a.inventory][str(path.relative_to(ROOT))];refs.append(path)
        assert not wanted & {m['uid'] for m in read(path)['models']}
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(mp.read_bytes())))
    result=dict(uids=sorted(wanted),sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in rows},sourceGeometryChanges=0,
                identityAccepted=False,installationApproved=False,publication=False,
                qualification='Exact recovered sheet/model bytes and immutable native records rebound to exact current UID/CSUID/ObjectID/forms. No source-role, support, terrain, identity or publication approval transferred.')
    save(out/'summary.json',result)
    module('acquired_original_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-recovered-source-sheet-current-form-selection',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
