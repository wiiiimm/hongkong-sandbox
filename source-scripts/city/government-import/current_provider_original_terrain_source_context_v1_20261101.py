"""Compare an unchanged building source with separately authenticated current TIN.

Source-only diagnostics: historical native terrain identities are untouched and
no current map/placement/terrain-publication approval is transferred.
"""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','terrain-proof','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture,a.terrain_proof])
    out=BASE/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('current-provider-terrain-source-context-'+str(uuid.uuid4()),['building:'+a.uid,'immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        f=BASE/batch/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selection=take(a.capture,'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==a.uid);proof=take(a.terrain_proof,'summary.json')
    assert proof['uids']==[a.uid]and proof['currentTerrainIsDistinctSourceIdentity']and not proof['historicalNativeRecordsChanged']and proof['sourceBuildingSHA256']==source['sourceSHA256']
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==source['triangles']
    for r in proof['currentProviderOriginalTerrain']:
        f=ROOT/r['path'];assert digest(f.read_bytes())==r['sha256']==pins[a.terrain_proof][r['path']];refs.append(f)
    paths=[ROOT/p for p in proof['sourceTerrainPaths']];assert paths
    decode=module('current_original_tin_decoder',HERE/'xl-second-pass.py');ground=np.concatenate([decode.terrain_triangles(p)for p in paths]);total=len(ground)
    lo,hi=tri.min((0,1)),tri.max((0,1));keep=(ground[:,:,0].max(1)>=lo[0]-10)&(ground[:,:,0].min(1)<=hi[0]+10)&(ground[:,:,2].max(1)>=lo[2]-10)&(ground[:,:,2].min(1)<=hi[2]+10);ground=ground[keep]
    assert len(ground)>0,'The exact current TIN does not meet this source frame; no fitted offset is permitted'
    projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));domain=shapely.union_all(shapely.polygons(ground[:,:,[0,2]]));missing=float(projection.difference(domain).area)
    tool=module('current_original_tin_foundation_context',HERE/'xl-final-script-pass.py');b=source['source']['building'];foundation=tool.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
    row=dict(uid=a.uid,sourceSHA256=source['sourceSHA256'],sourceTerrainPaths=proof['sourceTerrainPaths'],sourceTerrainProof=dict(path=str((BASE/a.terrain_proof/'result.json').relative_to(ROOT)),sha256=digest((BASE/a.terrain_proof/'result.json').read_bytes())),currentProviderRevision=proof['providerRevision'],historicalNativeTerrainRestored=False,missingOriginalTerrain=[],uncoveredSourceProjectionAreaM2=missing,completeProviderTerrainFaces=total,participatingGroundFaces=len(ground),completeSourceFaces=len(tri),originalTerrainFoundation=foundation,sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),groundWorldSHA256=digest(ground.astype('<f8').tobytes()),status='separate-current-provider-original-tin-source-only-context',installationApproved=False)
    assert reservations.owns(lease)
    result=dict(uids=[a.uid],rows=[row],sourceGeometryChanges=0,sourcePoseChanges=0,currentSceneAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact separately identified current government TIN glTF/buffer bytes compared with complete unchanged building source. Raw original coordinate frame only, no offset/fitting. Historical capture supplies source bytes/form identity, not old scene approval. Original E11 cache identity remains unchanged; this E12 source needs fresh current-scene, four-world, complete native/BASIC, runtime and browser checks before any private patch or publication.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('current_provider_original_terrain_source_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-building-and-distinct-current-original-tin-source-context-no-acceptance',list(dict.fromkeys(refs)),result)
    print(dict(uid=a.uid,missingProjectionAreaM2=missing,fullyBuriedTriangles=foundation['fullyBuriedTriangles'],upwardBuriedTriangles=foundation['fullyBuriedUpwardTriangles'],sourceOnly=True),flush=True)
if __name__=='__main__':main()
