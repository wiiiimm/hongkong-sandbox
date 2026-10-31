"""Reuse unchanged original-source ground diagnostics with exact current bindings.

Only joins existing diagnostics; no geometry, approval or terrain generation.
"""
import argparse,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--capture',required=True);ap.add_argument('--donor',action='append',required=True);ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.capture,*a.donor]) and 0<len(a.uid)==len(set(a.uid))<=8
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/a.batch/'reservation.json';refs=[Path(__file__)]
    if not a.owned:
        assert not out.exists() and not lp.parent.exists();claim=reservations.claim('exact-ground-receipt-merge-'+str(uuid.uuid4()),['building:'+u for u in a.uid],batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease);_,cp=authenticate(base/a.capture);selection=base/a.capture/'selection.json.gz';assert digest(selection.read_bytes())==cp[str(selection.relative_to(ROOT))];selected=read(selection);sources={r['uid']:r for r in selected['rows']};assert set(a.uid)<=set(sources);refs.extend([base/a.capture/'result.json',selection]);rows={};origins={};terrain_hashes={}
    for donor in a.donor:
        _,pins=authenticate(base/donor);summary=base/donor/'summary.json';assert digest(summary.read_bytes())==pins[str(summary.relative_to(ROOT))];data=read(summary);refs.extend([base/donor/'result.json',summary])
        for row in data['rows']:
            u=row['uid']
            if u not in a.uid:continue
            assert u not in rows and row['status']=='original-terrain-checked';source=sources[u]
            assert row['sourceSHA256']==source['sourceSHA256'] and row['nativeResultSHA256']==source['native']['resultSha']
            for name in row['sourceTerrainPaths']:
                p=ROOT/name;assert digest(p.read_bytes())==pins[name];refs.append(p);terrain_hashes.setdefault(name,pins[name]);assert terrain_hashes[name]==pins[name]
                for buffer in read(p).get('buffers',[]):
                    q=p.parent/buffer['uri'];key=str(q.relative_to(ROOT));assert q.resolve().is_relative_to(p.parent.resolve()) and digest(q.read_bytes())==pins[key];refs.append(q);terrain_hashes.setdefault(key,pins[key]);assert terrain_hashes[key]==pins[key]
            rows[u]=row;origins[u]=donor
    assert set(rows)==set(a.uid) and len({tuple(r['sourceTerrainPaths']) for r in rows.values()})==1
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    for u in a.uid:
        r=sources[u];asset=ROOT/r['candidate']['path'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(asset.read_bytes())==r['sourceSHA256'];assert digest(tile.read_bytes())==r['source']['tileSHA256'] and next(f for f in read(tile)['buildings'] if f['uid']==u)==r['source']['building'];refs.extend([asset,tile])
    result=dict(uids=a.uid,rows=[rows[u] for u in a.uid],sourceOrigins=origins,currentManifestSHA256=selected['manifestSHA256'],sourceTerrainHashes=terrain_hashes,sourceGeometryChanges=0,sourcePoseChanges=0,unchangedSourceCalculationsReused=True,installationApproved=False,physicalAcceptance=False,publication=False,qualification=__doc__+' Every source SHA/native result, current form/asset and all common original terrain GLTF/buffer hashes are checked. Historical current-scene decisions are not transferred.')
    assert reservations.owns(lease);save(out/'summary.json',result);module('exact_provider_ground_merge_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-immutable-provider-ground-diagnostic-current-binding',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
