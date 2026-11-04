"""Bind two canonical-contact-positive original assemblies for fresh current checks."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-two-passing-podium-pairs-selection-v1-20261023';out=base/batch;assert not out.exists()
    prior='government-xl-remaining-podium-canonical-contacts-v1-20261023';receipt,pins=authenticate(base/prior);p=base/prior/'support-inputs.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];data=read(p)
    positive=[r for r in receipt['rows']if r['passed']];assert {r['uid']for r in positive}=={'landsd/269972:0','landsd/136034:0'}
    wanted={u for r in positive for u in [r['uid'],r['supportUid']]};rows=deepcopy([r for r in data['sources']if r['uid']in wanted]);assert len(rows)==len(wanted)==4
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestsha=digest(manifestpath.read_bytes());refs=[Path(__file__),base/prior/'result.json',p,manifestpath]
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;assert not wanted&{m['uid']for m in read(path)['models']};refs.append(path)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in rows:
            asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
            tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert[r['source']['building']]==[f for f in read(tile)['buildings']if f['uid']==r['uid']];refs.append(tile)
            key=r['native']['cacheKey'];record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record and record[0]==r['native']['resultSha']
            assert next(m for m in record[1]['models']if m['modelId']==r['modelId'])==r['native']['model']
            for flag in ['publicationApproved','placementReviewed','sourceIdentityReviewed','identityReviewApproved']:assert not r['candidate']['entry'].get(flag)
    assert digest(manifestpath.read_bytes())==manifestsha
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha));save(out/'pairs.json',[dict(uid=r['uid'],supportUid=r['supportUid'])for r in positive])
    result=dict(uids=sorted(wanted),sources=len(rows),pairs=2,sourceGeometryChanges=0,installationApproved=False,publication=False,status='unapproved-current-original-assembly-selection',qualification='Two original-source pairs passed canonical source support contact, then exact assets/current forms/native records were rebound. No identity, independent podium ground, all-world contact/clearance, current-neighbour, visual or installation approval.')
    save(out/'summary.json',result);module('two_positive_podium_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'current-two-canonical-positive-original-podium-assemblies',refs,result);print(dict(sources=4,pairs=2),flush=True)

if __name__=='__main__':main()
