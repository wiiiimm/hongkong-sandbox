"""Measure explicitly selected unchanged original compound projections; no approval."""
from pathlib import Path
import argparse
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_20261009 import exact_coverage
BASE=ROOT/'docs/astra-city/government-import'
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','scope','identity']:parser.add_argument('--'+key,required=True)
    args=parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [args.batch,args.runtime,args.scope,args.identity])
    BATCH=args.batch
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(b,p):
        if b not in pins:pins[b]=authenticate(BASE/b)[1];refs.append(BASE/b/'result.json')
        assert digest(p.read_bytes())==pins[b][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=args.runtime;selection=take(runtime,BASE/runtime/'selection.json.gz');scope=args.scope;sc=take(scope,BASE/scope/'summary.json');assert sc['currentManifestSHA256']==selection['manifestSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    assert 2<=len(selection['rows'])<=40
    assert len({r['uid'] for r in selection['rows']})==len(selection['rows'])
    forms={};sources={};triangles={};raw={}
    for row in selection['rows']:
        uid=row['uid'];sources[uid]=row['sourceSHA256'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);triangles[uid]=decode_original_world_triangles(asset.read_bytes())
        for f in take(scope,BASE/scope/(uid.split('/')[1]+'-forms.json.gz')):
            path=ROOT/'3d-viewer'/f['tile'];assert digest(path.read_bytes())==f['tileSHA256'];refs.append(path);forms[f['building']['uid']]=f['building']
        b=args.identity;raw[uid]=take(b,BASE/b/(uid.split('/')[1]+'/identity.json'))
        assert raw[uid]['sourceSHA256']==row['sourceSHA256']and raw[uid]['originalOwnership']['sourceGraphVerified']and raw[uid]['exactCurrentComponentRoute']['qualified']
    polygons={u:shapely.Polygon(f['rings'][0],f['rings'][1:])for u,f in forms.items()};assembly=shapely.union_all([polygons[u]for u in sources]);tri=np.concatenate(list(triangles.values()));projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));rows=[]
    for uid in sources:
        cell=raw[uid]['geographicCell']['worldXZBounds'];x0,z0,x1,z1=cell;cellpoly=shapely.box(*cell);halves=np.asarray([[[x0,0,z0],[x1,0,z0],[x1,0,z1]],[[x0,0,z0],[x1,0,z1],[x0,0,z1]]]);proof=[exact_coverage(f,tri)for f in halves]
        outside=shapely.union_all(shapely.polygons(triangles[uid][:,:,[0,2]])).difference(assembly)
        overlaps={u:float(outside.intersection(p).area)for u,p in polygons.items()if u not in sources and outside.intersection(p).area>0}
        rows.append(dict(uid=uid,sourceSHA256=sources[uid],rawReasonsRetained=raw[uid]['reasons'],ownCoverageByWholeOriginalAssembly=float(projection.intersection(polygons[uid]).area/polygons[uid].area),wholeCellCoveredByCurrentAssembly=bool(assembly.covers(cellpoly)),wholeCellCoveredByOriginalAssembly=all(p['exactProjectionCovered']for p in proof),exactWholeCellHalves=proof,sourceMaximumExtentFromCurrentAssemblyM=float(shapely.distance(shapely.points(triangles[uid][:,:,[0,2]].reshape(-1,2)),assembly).max()),sourceExcessOverlapOutsideCurrentAssemblyByForeignUid=overlaps))
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,rows=rows,completeOriginalFaces=len(tri),identityAccepted=False,installationApproved=False,qualification='Diagnostic combined source/current projection only. Raw individual identity failures remain. Collective coverage and current aliases do not grant component identity, source-role, tower relationship, suppression, physical, browser or publication approval. No tolerance, geometry, pose or current polygon changes.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']);module('explicit_compound_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'explicit-original-compound-projection-diagnostic',refs,result)
    for r in rows:print({k:r[k]for k in ['uid','ownCoverageByWholeOriginalAssembly','wholeCellCoveredByCurrentAssembly','wholeCellCoveredByOriginalAssembly','sourceMaximumExtentFromCurrentAssemblyM','sourceExcessOverlapOutsideCurrentAssemblyByForeignUid']},flush=True)
if __name__=='__main__':main()
