"""Bind both available exact Sung Fung originals to current forms; no approval."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-three-original-selection-v1-20261024';out=base/batch;assert not out.exists()
    prior='government-xl-next-repairs-sung-fung-lee-man-original-family-discovery-v1-20261024';_,pins=authenticate(base/prior);path=base/prior/'source-families.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];family=read(path)['rows'];assert {r['uid']for r in family}=={'landsd/79098:0','landsd/45779:0','landsd/47160:0'}
    refs=[Path(__file__),base/prior/'result.json',path]
    recovered='government-xl-next-repairs-lee-man-original-asset-recovery-v2-20261024';_,rpins=authenticate(base/recovered);recoverypath=base/recovered/'summary.json';assert digest(recoverypath.read_bytes())==rpins[str(recoverypath.relative_to(ROOT))];recovery=read(recoverypath);assert recovery['sourceRecovered']and recovery['uids']==['landsd/47160:0'];refs.extend([base/recovered/'result.json',recoverypath])
    for member in family:
        if not member['verifiedLocalOriginals']:
            assert member['uid']=='landsd/47160:0'and recovery['asset']['sha256']==member['model']['asset']['sha256']and member['resultSHA256']==recovery['nativeResultSHA256'];member['verifiedLocalOriginals']=[recovery['asset']]
    mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);sha=digest(mp.read_bytes());refs.append(mp);wanted={r['uid']for r in family}
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;assert not wanted&{m['uid']for m in read(p)['models']};refs.append(p)
    tile=ROOT/'3d-viewer/city/data/tiles/1_-1.json'
    # Resolve through manifest, never guess a file layout from the spatial tile label.
    matches=[]
    for t in manifest['tiles']:
        if t['bounds'][0]<=3242.039<=t['bounds'][2]and t['bounds'][1]<=-59.684<=t['bounds'][3]:
            p=ROOT/'3d-viewer'/t['url'];data=read(p)
            if wanted<={f['uid']for f in data['buildings']}:matches.append(p)
    assert len(matches)==1;tile=matches[0];forms={f['uid']:f for f in read(tile)['buildings']if f['uid']in wanted};refs.append(tile);rows=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in family:
            m=r['model'];form=forms[r['uid']];assert form==r['currentBasicForm'];asset=r['verifiedLocalOriginals'];assert len(asset)==1;p=ROOT/asset[0]['path'];assert digest(p.read_bytes())==m['asset']['sha256'];refs.append(p)
            record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['cacheKey'],)).fetchone();assert record and record[0]==r['resultSHA256']and next(x for x in record[1]['models']if x['modelId']==m['modelId'])==m
            entry=deepcopy(m['candidate']);assert entry['uid']==form['uid']and entry['buildingCSUID']==form['buildingCSUID']and entry['objectId']==form['objectId'];assert not any(entry.get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
            entry.update(sourceTile=r['sheet'],rootTranslation=[-834500,0,816500],proceduralWindows=False,priority='unreviewed',recordedBaseHeight=form['baseHeightHKPD'],recordedTopHeight=form['topHeightHKPD'])
            rows.append(dict(uid=form['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],originalGeometryOnly=True,source=dict(building=form,tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes())),native=dict(cacheKey=r['cacheKey'],resultSha=r['resultSHA256'],model=m),candidate=dict(path=asset[0]['path'],entry=entry)))
    assert digest(mp.read_bytes())==sha;save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=sha))
    result=dict(uids=sorted(wanted),installationApproved=False,publication=False,identityApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Current forms, native result records and complete original assets rebound. No prior source/assembly/placement approval transferred.')
    module('sung_pair_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unapproved-current-sung-fung-original-pair-selection',refs,result)


if __name__=='__main__':main()
