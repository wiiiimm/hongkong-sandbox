"""Append exact acquired originals as explicit unapproved current-capture inputs."""
import argparse
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture','acquired']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)]
    def take(batch,filename):
        _,pins=authenticate(base/batch);p=base/batch/filename;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([base/batch/'result.json',p]);return read(p)
    selected=take(a.capture,'selection.json.gz');rows=deepcopy(selected['rows']);acquired=take(a.acquired,'summary.json');assert acquired['sourceRecovered']
    assert rows and 0<len(acquired['rows'])and len(rows)+len(acquired['rows'])<=8
    mp=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(mp.read_bytes());assert manifestsha==selected['manifestSHA256'];refs.append(mp)
    tiles={}
    for tile in {r['source']['tile']for r in rows}:
        p=ROOT/'3d-viewer'/tile;tiles[tile]=read(p);refs.append(p)
    for row in rows:
        assert [f for f in tiles[row['source']['tile']]['buildings']if f['uid']==row['uid']]==[row['source']['building']]
        row['source']['tileSHA256']=digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())
    for recovered in acquired['rows']:
        uid=recovered['uid'];assert uid not in {r['uid']for r in rows}
        found=[(tile,f)for tile,data in tiles.items()for f in data['buildings']if f['uid']==uid];assert len(found)==1
        tile,form=found[0];assert form==recovered['currentForm'];m=recovered['model']
        matches=[v for v in m['matching']['viewerMatches']if v['uid']==uid and v['buildingCSUID']==form['buildingCSUID']and v['objectId']==form['objectId']];assert len(matches)==1;matching=matches[0]
        entry=dict(m['asset'],uid=uid,buildingCSUID=form['buildingCSUID'],label=matching['label'],objectId=form['objectId'],modelId=m['modelId'],triangles=m['triangles'],worldBounds=m['worldBounds'],rootTranslation=[-834500,0,816500],sourceTile=rows[0]['candidate']['entry']['sourceTile'],sourceBaseHeight=form['baseHeightHKPD'],sourceTopHeight=form['topHeightHKPD'],proceduralWindows=False,priority='unreviewed',placementReviewed=False,publicationApproved=False)
        assert acquired['nativeResultSHA256']==rows[0]['native']['resultSha']and acquired['nativeCacheKey']==rows[0]['native']['cacheKey']
        rows.append(dict(uid=uid,modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=recovered['sourceSHA256'],originalGeometryOnly=True,sourceAttributionPending=True,source=dict(building=form,tile=tile,tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes())),native=dict(cacheKey=acquired['nativeCacheKey'],resultSha=acquired['nativeResultSHA256'],model=m),candidate=dict(path=recovered['asset']['path'],entry=entry)))
    for row in rows:
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];refs.append(p)
        assert not any(row['candidate']['entry'].get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
    for url in read(mp)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;assert not {r['uid']for r in rows}&{m['uid']for m in read(p)['models']};refs.append(p)
    assert digest(mp.read_bytes())==manifestsha
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha))
    result=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceGeometryChanges=0,installationApproved=False,identityAccepted=False,qualification='Explicit acquired-source investigation routes bound to current complete source forms and unchanged original bytes. Raw native matching records retained. No assembly, identity, support or publication approval.')
    module('append_original_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'expanded-unapproved-original-capture-selection',refs,result)
    print(dict(uids=result['uids'],installationApproved=False),flush=True)


if __name__=='__main__':main()
