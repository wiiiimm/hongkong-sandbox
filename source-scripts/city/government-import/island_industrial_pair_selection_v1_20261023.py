"""Bind two unchanged Island Industrial originals to current unapproved capture inputs."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    batch='government-xl-after-fu-tor-loy-island-industrial-pair-selection-v1-20261023'
    out=base/batch
    assert not out.exists()
    names=['government-xl-all-200-original-terrain-batch-v2-20261022','government-xl-island-industrial-podium-acquire-v1-20261023','government-xl-fu-tor-loy-five-source-retained-original-installed-v9-20261023']
    refs=[Path(__file__)];pins={}
    for name in names:
        _,bound=authenticate(base/name);pins.update(bound);refs.append(base/name/'result.json')
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    owner=deepcopy(next(r for r in take(base/names[0]/'selection.json.gz')['rows']if r['uid']=='landsd/20270:0'))
    acquired=take(base/names[1]/'summary.json');assert acquired['sourceRecovered']and len(acquired['rows'])==1
    podium=acquired['rows'][0];m=podium['model'];assert m['modelId']=='B348962051702063C0'and m['triangles']==537
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());refs.append(manifest)
    assert sha==read(base/names[2]/'result.json')['manifest']['sha256']
    tile=ROOT/'3d-viewer'/owner['source']['tile'];tilebytes=tile.read_bytes();refs.append(tile)
    forms={f['uid']:f for f in read(tile)['buildings']}
    assert owner['source']['building']==forms[owner['uid']]
    other=forms['landsd/159422:0'];assert podium['currentForm']==other
    assert other['buildingCSUID']=='3489620517P20060311'
    owner['source']['tileSHA256']=digest(tilebytes)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        resultsha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(acquired['nativeCacheKey'],)).fetchone()
        assert resultsha==acquired['nativeResultSHA256']==owner['native']['resultSha']
        assert next(v for v in native['models']if v['modelId']==m['modelId'])==m
        assert next(v for v in native['models']if v['modelId']==owner['modelId'])==owner['native']['model']
    matching=next(v for v in m['matching']['viewerMatches']if v['uid']==other['uid']and v['buildingCSUID']==other['buildingCSUID'])
    entry=dict(m['asset'],uid=other['uid'],buildingCSUID=other['buildingCSUID'],label=matching['label'],objectId=matching['objectId'],modelId=m['modelId'],triangles=m['triangles'],worldBounds=m['worldBounds'],rootTranslation=[-834500,0,816500],sourceTile=owner['candidate']['entry']['sourceTile'],sourceBaseHeight=other['baseHeightHKPD'],sourceTopHeight=other['topHeightHKPD'],overlapOfSmallerFootprint=matching['overlapOfSmallerFootprint'],footprintCentroidDistanceMetres=matching['footprintCentroidDistanceMetres'],proceduralWindows=False,priority='unreviewed',placementReviewed=False,publicationApproved=False)
    new=dict(uid=other['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=podium['sourceSHA256'],originalGeometryOnly=True,source=dict(building=other,tile=owner['source']['tile'],tileSHA256=digest(tilebytes)),native=dict(cacheKey=acquired['nativeCacheKey'],resultSha=resultsha,model=m),candidate=dict(path=podium['asset']['path'],entry=entry),sourceAttributionPending=True)
    rows=[owner,new]
    for row in rows:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];refs.append(path)
        assert not any(row['candidate']['entry'].get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;assert not {r['uid']for r in rows}&{v['uid']for v in read(path)['models']};refs.append(path)
    assert digest(manifest.read_bytes())==sha and tile.read_bytes()==tilebytes
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=sha))
    result=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},currentManifestSHA256=sha,sourceGeometryChanges=0,installationApproved=False,identityAccepted=False,publication=False,qualification='Exact original pair nominated for current capture only. Podium native record remains source-match-held with both broad matches retained. Candidate UID is an explicit unapproved investigation route, not disambiguation/acceptance. No previous physical/identity/terrain approval transferred.')
    module('island_pair_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unapproved-current-original-pair-capture-selection',refs,result)
    print(dict(uids=result['uids'],installationApproved=False),flush=True)


if __name__=='__main__':main()
