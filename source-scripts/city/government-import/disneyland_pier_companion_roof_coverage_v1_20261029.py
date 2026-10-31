"""Measure conservative roof coverage only; never approve duplicate suppression."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH='government-xl-disneyland-piers-companion-roof-coverage-v1-20261029'
RESTORE='government-xl-disneyland-pier-74189-archive-restore-v1-20261029'
FOREIGN='government-xl-disneyland-pier-75643-foreign-contacts-v1-20261029'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=take(RESTORE,base/RESTORE/'summary.json');asset=ROOT/source['assetPath'];assert digest(asset.read_bytes())==source['sourceSHA256']==pins[RESTORE][str(asset.relative_to(ROOT))];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==source['sourceFaces']==6705
    building=next(r for r in take(FOREIGN,base/FOREIGN/'basic.json')['rows']if r['uid']=='way/334029318:0')
    basic=np.asarray(building['position']).reshape(-1,3)[np.asarray(building['index']).reshape(-1,3)]
    polygons=[shapely.Polygon(t[:,[0,2]])for t in basic];footprint=shapely.union_all([p for p in polygons if p.area>1e-8]);assert footprint.is_valid and footprint.area>0
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=normal[:,1]>.25*np.linalg.norm(normal,axis=1);rows=[]
    for height in [5,6,7,8,9]:
        selected=tri[up&(tri[:,:,1].min(1)>=height)];roof=shapely.union_all([shapely.Polygon(t[:,[0,2]])for t in selected]);area=roof.intersection(footprint).area
        rows.append(dict(minimumWholeFacetHeightM=height,selectedUpwardFacets=len(selected),projectedRoofCoverageM2=area,footprintCoverageFraction=area/footprint.area))
    result=dict(uids=['landsd/75642:0','landsd/75643:0','landsd/74189:0'],companionUid='landsd/74189:0',companionSourceSHA256=source['sourceSHA256'],completeCompanionFaces=len(tri),basicUid=building['uid'],basicFootprintAreaM2=footprint.area,rows=rows,duplicateSuppressionApproved=False,installationApproved=False,identityAccepted=False,physicalAccepted=False,qualification='Conservative union of upward complete source facets wholly above each height threshold. Measures source coverage only; it neither proves the BASIC identity nor grants source/terrain/contact acceptance. Preserve the neighbouring BASIC model. All three source components remain uninstalled.')
    save(doc/'summary.json',result)
    module('companion_roof_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-pier-companion-roof-coverage-no-suppression',refs,result)

if __name__=='__main__':main()
