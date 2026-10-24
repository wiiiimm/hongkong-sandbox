"""Measure recovered unmapped originals against current footprint candidates; no approval."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-unmapped-two-original-projection-context-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    comparison='government-xl-remaining-186-exact-primary-targets-v1-20261023';summary=take(comparison,'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==summary['currentManifestSHA256'];refs.append(manifest);mapdata=read(manifest);rows=[]
    for model in ['B349971856402063C0','B352981210001063C0']:
        acquisition='government-xl-unmapped-'+model[1:11]+'-original-acquire-v1-20261023';a=take(acquisition,'summary.json');assert a['sourceRecovered']and a['viewerUid']is None;asset=ROOT/a['asset']['path'];assert digest(asset.read_bytes())==a['sourceSHA256']==a['expectedSourceSHA256'];refs.append(asset);t=decode_original_world_triangles(asset.read_bytes());assert len(t)==a['completeSourceFaces']and digest(t.tobytes())==a['originalWorldSHA256'];poly=shapely.polygons(t[:,:,[0,2]]);positive=shapely.area(poly)>0;foot=shapely.union_all(poly[positive]);assert foot.is_valid and foot.area>0
        lo,hi=t.min((0,1)),t.max((0,1));box=shapely.box(lo[0],lo[2],hi[0],hi[2]);forms=[]
        for tile in mapdata['tiles']:
            if not shapely.box(*tile['bounds']).intersects(box):continue
            p=ROOT/'3d-viewer'/tile['url'];blob=p.read_bytes();assert digest(blob)==pins[comparison][str(p.relative_to(ROOT))];refs.append(p)
            for f in read(p)['buildings']:
                target=shapely.Polygon(f['rings'][0],f['rings'][1:])
                if not target.intersects(box):continue
                overlap=foot.intersection(target);forms.append(dict(uid=f['uid'],name=f.get('name'),buildingCSUID=f.get('buildingCSUID'),structureType=f.get('structureType'),baseHeightHKPD=f.get('baseHeightHKPD'),topHeightHKPD=f.get('topHeightHKPD'),targetAreaM2=float(target.area),sourceOverlapM2=float(overlap.area),fractionOfCurrentTargetCovered=float(overlap.area/target.area),fractionOfSourceProjectionWithinTarget=float(overlap.area/foot.area),targetWKT=target.wkt,sourceGeometryChanges=0,identityAccepted=False))
        current=shapely.union_all([shapely.from_wkt(f['targetWKT'])for f in forms]);record=dict(sourceKey=a['sourceKeys'][0],modelId=model,sourceSHA256=a['sourceSHA256'],completeSourceFaces=len(t),nonzeroProjectedFaces=int(positive.sum()),zeroAreaProjectedFaces=int((~positive).sum()),sourceProjectedAreaM2=float(foot.area),sourceProjectionWKT=foot.wkt,sourceProjectionOutsideCurrentCandidateUnionM2=float(foot.difference(current).area),worldBounds=dict(min=lo.tolist(),max=hi.tolist()),currentTargets=sorted(forms,key=lambda r:r['sourceOverlapM2'],reverse=True),sourceRootNotReattributed=True,sourceIdentityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Unbuffered floating planar union of every positive-area original projected triangle, preserving holes; no convex-hull filling, movement, scaling or geometry changes. Ratios are candidate correspondence diagnostics, not exact rational coverage, an accuracy allowance, architectural ownership, support or publication approval. Current targets are complete AABB-intersecting footprint records, not a chosen replacement UID.')
        save(out/(model+'.json.gz'),record);rows.append({k:v for k,v in record.items()if k not in ['sourceProjectionWKT','currentTargets']});print(dict(modelId=model,completeSourceFaces=len(t),projectedAreaM2=record['sourceProjectedAreaM2'],candidates=[{k:f[k]for k in ['uid','name','fractionOfCurrentTargetCovered','fractionOfSourceProjectionWithinTarget','baseHeightHKPD','topHeightHKPD']}for f in record['currentTargets']]),flush=True)
    assert digest(manifest.read_bytes())==summary['currentManifestSHA256'];result=dict(uids=[],sourceKeys=[r['sourceKey']for r in rows],rows=rows,sourceGeometryChanges=0,sourceIdentityAccepted=False,installationApproved=False,newlyInstalled=0,permanentRejection=False,qualification='Both unmapped originals remain distinct source keys. Complete recovered original projected surfaces compared to current targets; no UID assigned or models declared corrupt/uninstallable.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('unmapped_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-unmapped-original-to-current-footprint-projection-context',refs,result)

if __name__=='__main__':main()
