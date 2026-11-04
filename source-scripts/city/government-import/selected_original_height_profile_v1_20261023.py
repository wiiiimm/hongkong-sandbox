"""Bound complete unchanged-source height profiles; source-role diagnostic only."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    _,pins=authenticate(base/a.capture);path=base/a.capture/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    selection=read(path);row=next(r for r in selection['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles']
    building=row['source']['building'];top=building.get('topHeightHKPD');assert top is not None
    polygons=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polygons);assert projection.area>0
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(cross,axis=1)
    upward=(norm>0)&(cross[:,1]>.95*norm);roof={}
    for face,area in zip(tri[upward],norm[upward]/2):
        level=round(float(face[:,1].mean()),3);roof[level]=roof.get(level,0.)+float(area)
    levels=[]
    for h in sorted(set([float(top)-.5,float(top),float(top)+.5,float(top)+2,float(top)+5,float(top)+8])):
        mask=tri[:,:,1].min(1)>=h;area=float(shapely.union_all(polygons[mask]).area)if np.any(mask)else 0.
        levels.append(dict(minimumCompleteFaceY=h,projectedAreaM2=area,fractionOfCompleteSourceProjection=area/projection.area,faces=int(mask.sum())))
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(tri),recordedBase=building.get('baseHeightHKPD'),recordedTop=top,sourceMinY=float(tri[:,:,1].min()),sourceMaxY=float(tri[:,:,1].max()),sourceProjectionAreaM2=float(projection.area),largestUpwardSurfaceElevations=[dict(meanY=y,areaM2=area)for y,area in sorted(roof.items(),key=lambda v:-v[1])[:30]],elevatedCompleteFaceProjections=levels,installationApproved=False,identityApproved=False,physicalAcceptance=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Complete source triangles and current recorded heights only. Rounded height bins summarise upward areas; they are not surveyed roof heights, identity approval, clearance or physical acceptance.')
    save(out/'summary.json',result)
    refs=[Path(__file__),base/a.capture/'result.json',path,asset,HERE/'exact_packed_world_geometry_20261009.py']
    module('source_height_profile_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-source-complete-height-profile-diagnostic',refs,result)
    print(dict(sourceMaxY=result['sourceMaxY'],recordedTop=top,largestUpwardSurfaceElevations=result['largestUpwardSurfaceElevations'][:8],elevatedCompleteFaceProjections=levels),flush=True)


if __name__=='__main__':main()
