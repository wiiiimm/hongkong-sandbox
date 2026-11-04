"""Combine authenticated current unchanged originals without transferring approval."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--selection',action='append',required=True);ap.add_argument('--uid',action='append',required=True);a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,*a.selection])and not out.exists()
    wanted=set(a.uid);assert 0<len(wanted)==len(a.uid)<=40;refs=[Path(__file__)];rows=[];seen=set()
    mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());manifest=read(mp);refs.append(mp);tileurls={t['url']for t in manifest['tiles']}
    for name in a.selection:
        _,pins=authenticate(base/name);p=base/name/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];selected=read(p);assert selected['manifestSHA256']==msha;refs.extend([base/name/'result.json',p])
        for original in selected['rows']:
            if original['uid']not in wanted:continue
            row=deepcopy(original);uid=row['uid'];assert uid not in seen;seen.add(uid)
            entry=row['candidate']['entry'];source=row['source'];assert source['tile']in tileurls;tp=ROOT/'3d-viewer'/source['tile'];assert digest(tp.read_bytes())==source['tileSHA256'];assert next(f for f in read(tp)['buildings']if f['uid']==uid)==source['building'];refs.append(tp)
            p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']==entry['sha256'];refs.append(p)
            assert entry['uid']==uid and entry['objectId']==source['building']['objectId']and entry['buildingCSUID']==source['building']['buildingCSUID']
            assert entry.get('rootTranslation')==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
            assert not any(entry.get(k)for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed','suppressesBuildingUids','variantId'])
            native=row['native']
            with connect()as db:
                db.execute('SET TRANSACTION READ ONLY');found=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone()
            assert found and found[0]==native['resultSha'];model=next(m for m in found[1]['models']if m['modelId']==row['modelId']);assert model==native['model']and model['asset']['sha256']==row['sourceSHA256']
            assert entry['triangles']==model['triangles']and entry['bytes']==model['asset']['bytes']
            if 'triangles'in row:assert row['triangles']==model['triangles']
            else:row['triangles']=model['triangles']
            rows.append(row)
    assert seen==wanted
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;assert not wanted&{m['uid']for m in read(p)['models']};refs.append(p)
    assert digest(mp.read_bytes())==msha
    save(out/'selection.json.gz',dict(rows=rows,manifestSHA256=msha))
    result=dict(uids=sorted(wanted),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Only exact authenticated current original inputs merged. Missing top-level face count copied from the exact native-stage model; existing counts must match. No geometry, support, identity, terrain, runtime or installation approval transferred.')
    module('merge_original_inputs_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'merged-current-unapproved-original-capture-inputs',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
