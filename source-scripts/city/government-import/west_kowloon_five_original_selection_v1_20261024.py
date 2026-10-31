"""Bind exact terminus and four companion originals; no approval transfer."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'five-original-selection-v1-20261024';out=base/batch;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(n,f):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected=take(prefix+'protected-return-runtime-v1-20261024','selection.json.gz');rows=deepcopy(selected['rows']);assert len(rows)==1 and rows[0]['uid']=='landsd/255415:0'
    family=take(prefix+'foreign-original-discovery-v1-20261024','source-families.json.gz')['rows'];acquired=take(prefix+'three-companion-acquire-v1-20261024','summary.json');assert acquired['sourceRecovered']and len(family)==4
    assets={r['uid']:r['asset']for r in acquired['rows']}
    for r in family:
        if r['verifiedLocalOriginals']:assert len(r['verifiedLocalOriginals'])==1;assets[r['uid']]=r['verifiedLocalOriginals'][0]
    assert set(assets)=={r['uid']for r in family};mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);assert digest(mp.read_bytes())==selected['manifestSHA256'];refs.append(mp)
    tiles={}
    for t in manifest['tiles']:
        p=ROOT/'3d-viewer'/t['url'];box=t['bounds']
        if box[0]<=531 and box[2]>=427 and box[1]<=-2129 and box[3]>=-2458:
            data=read(p);tiles[t['url']]={f['uid']:f for f in data['buildings']};refs.append(p)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in family:
            m=r['model'];form=r['currentBasicForm'];found=[(tile,fs[r['uid']])for tile,fs in tiles.items()if r['uid']in fs];assert len(found)==1 and found[0][1]==form;tile=found[0][0];asset=assets[r['uid']];p=ROOT/asset['path'];assert digest(p.read_bytes())==m['asset']['sha256'];refs.append(p)
            record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['cacheKey'],)).fetchone();assert record and record[0]==r['resultSHA256']and next(x for x in record[1]['models']if x['modelId']==m['modelId'])==m
            entry=deepcopy(m['candidate']);assert entry['uid']==form['uid']and entry['buildingCSUID']==form['buildingCSUID']and entry['objectId']==form['objectId'];assert not any(entry.get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
            entry.update(sourceTile=r['sheet'],rootTranslation=[-834500,0,816500],proceduralWindows=False,priority='unreviewed',recordedBaseHeight=form['baseHeightHKPD'],recordedTopHeight=form['topHeightHKPD'])
            rows.append(dict(uid=r['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],originalGeometryOnly=True,source=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes())),native=dict(cacheKey=r['cacheKey'],resultSha=r['resultSHA256'],model=m),candidate=dict(path=asset['path'],entry=entry)))
    wanted={r['uid']for r in rows};assert len(wanted)==5
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;assert not wanted&{m['uid']for m in read(p)['models']};refs.append(p)
    assert digest(mp.read_bytes())==selected['manifestSHA256'];save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=selected['manifestSHA256']))
    result=dict(uids=sorted(wanted),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceGeometryChanges=0,sourcePoseChanges=0,identityApproved=False,installationApproved=False,publication=False,qualification='Exact current forms, pinned native records and all five immutable original assets bound for assembly investigation. No original identity, contact, terrain, neighbour or publication approval transferred.')
    module('west_five_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-unapproved-five-original-terminus-selection',refs,result)

if __name__=='__main__':main()
