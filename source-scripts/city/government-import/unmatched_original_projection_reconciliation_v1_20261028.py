"""Exact original projection versus pinned primary candidates, no reassignment.

Retain both unmatched fixed XL keys and all negatives; no geometry or scene edit.
"""
import argparse,subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmatched-two-projection-reconciliation-v1-20261028';PRIMARY='government-xl-unmatched-two-primary-spatial-v1-20261027'
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease);out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/PRIMARY);path=BASE/PRIMARY/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];old=read(path);assert len(old['rows'])==2;assert {'native-source:'+r['sourceKey']for r in old['rows']}<=set(lease['resources']);refs=[Path(__file__),BASE/PRIMARY/'result.json',path];rows=[]
 for row in old['rows']:
  found=subprocess.run(['rg','--files','--hidden','--no-ignore','-g',row['sourceSHA256']+'.glb.gz',str(HERE/'local'),str(ROOT/'3d-viewer/city/data/official-models')],capture_output=True,text=True);assert found.returncode in[0,1];asset=next((Path(s)for s in found.stdout.splitlines()if digest(Path(s).read_bytes())==row['sourceSHA256']),None);assert asset is not None;refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());bounds=np.array([tri.min(axis=(0,1)),tri.max(axis=(0,1))]);assert np.max(np.abs(bounds-np.asarray(row['worldBounds'])))<1e-6
  xy=tri[:,:,[0,2]].copy();xy[:,:,0]+=834500;xy[:,:,1]=816500-xy[:,:,1];polys=shapely.polygons(xy);areas=shapely.area(polys);projection=shapely.union_all(polys[areas>0]);assert projection.is_valid and projection.area>0
  rawpath=BASE/PRIMARY/(row['modelId']+'-spatial.json');assert digest(rawpath.read_bytes())==pins[str(rawpath.relative_to(ROOT))];refs.append(rawpath);features=read(rawpath)['features'];assert len(features)==row['spatialRecords'];candidates=[]
  for feature in features:
   attr=feature['attributes'];shape=shapely.GeometryCollection()
   for ring in feature['geometry']['rings']:shape=shape.symmetric_difference(shapely.Polygon(ring))
   assert shape.is_valid;overlap=projection.intersection(shape).area;lo,hi=attr.get('BaseHeight'),attr.get('TopHeight');vertical=bool(lo is not None and hi is not None and max(float(lo),bounds[0][1])<=min(float(hi),bounds[1][1]))
   candidates.append(dict(objectId=attr['OBJECTID'],name=attr.get('BuildingNameEN'),buildingCSUID=attr.get('BuildingCSUID'),geoRefNo=attr.get('GeoRefNo'),structureType=attr.get('BuildingBlockType'),baseHeightHKPD=lo,topHeightHKPD=hi,primaryFootprintM2=shape.area,exactOriginalProjectionOverlapM2=overlap,sourceProjectionCoverage=overlap/projection.area,primaryFootprintCoverage=overlap/shape.area if shape.area else None,sourceHeightIntervalOverlapsPrimary=vertical,identityAccepted=False))
  rows.append(dict(sourceKey=row['sourceKey'],uid=None,sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),sourceProjectionM2=projection.area,sourceWorldBounds=bounds.tolist(),exactGeoRefRecords=row['exactGeoRefRecords'],exactActiveGeoRefRecords=row['exactActiveGeoRefRecords'],candidates=candidates,currentRevisionIdentityEstablished=False,installationApproved=False,permanentRejection=False))
 result=dict(uids=[],sourceKeys=[r['sourceKey']for r in rows],rows=rows,unmatchedKeysRetained=2,sourceGeometryChanges=0,sourceFacesOmitted=0,qualification='Every exact original facet included in full source XZ projection; only zero projected-area vertical/degenerate facets have no area contribution. Complete pinned primary spatial polygons used without repair. Projection/height overlap is diagnostic routing evidence, never independent identity, support, corruption, permanent invalidity or installation approval. This does not claim a fresh current-scene review or transfer historical acceptance.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('unmatched_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-unmatched-original-projection-primary-reconciliation',refs,result);print([(r['sourceKey'],len(r['candidates']))for r in rows],flush=True)
if __name__=='__main__':main()
