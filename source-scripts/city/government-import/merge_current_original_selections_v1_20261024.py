"""Merge explicitly named originals with fresh inventory/form/native bindings.

Selection only: never transfers old scene, physical, identity or publication approval.
"""
import argparse,copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--inventory',required=True);p.add_argument('--capture',action='append',required=True);p.add_argument('--uid',action='append',required=True);a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.inventory,*a.capture]);wanted=set(a.uid);assert 0<len(wanted)==len(a.uid)<=40
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    inventory=take(a.inventory,base/a.inventory/'complete-bounds.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert sha==pins[a.inventory][str(manifest.relative_to(ROOT))];refs.append(manifest);installed=set()
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[a.inventory][str(path.relative_to(ROOT))];refs.append(path);installed.update(m['uid']for m in read(path)['models'])
    assert installed=={r['uid']for r in inventory['rows']}and not wanted&installed
    rows=[];origins={}
    for name in a.capture:
        selected=take(name,base/name/'selection.json.gz')
        for row in selected['rows']:
            if row['uid']not in wanted:continue
            assert row['uid']not in origins,'Each requested original must have one explicit selection origin'
            origins[row['uid']]=name;rows.append(copy.deepcopy(row))
    assert set(origins)==wanted
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            uid=row['uid'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==inventory['currentFormTileHashes'][str(tile.relative_to(ROOT))]==row['source']['tileSHA256'];assert next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
            asset=(ROOT/row['candidate']['path']).resolve();assert asset.is_relative_to(ROOT)and digest(asset.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];refs.append(asset)
            native=row['native'];record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert record and record[0]==native['resultSha']and next(m for m in record[1]['models']if m['modelId']==row['modelId'])==native['model']
            assert native['model']['asset']['sha256']==row['sourceSHA256'];row['triangles']=native['model']['triangles']
            entry=row['candidate']['entry'];assert entry['uid']==uid and entry['buildingCSUID']==row['source']['building']['buildingCSUID']and entry['objectId']==row['source']['building']['objectId']
            assert not any(entry.get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
    assert digest(manifest.read_bytes())==sha
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=sha))
    result=dict(uids=sorted(wanted),sourceOrigins=origins,currentNativeActors=len(installed),currentManifestSHA256=sha,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Exact complete source forms, immutable native records and original bytes freshly rebound to current inventory. No historical scene, support, physical, identity or publication approval transferred.')
    save(out/'summary.json',result);module('merge_original_selections_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-current-original-selection-merge',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
