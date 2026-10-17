"""Private conservative Float32 hull infill; existing source and terrain records unchanged."""
from pathlib import Path
from fractions import Fraction as F
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from bounded_float32_terrain_gap_boxes_v2_20261010 import bounded_boxes,down,up
from exact_original_facet_outward_float32_gap_hull_20261010 import hull
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-bounded-gap-infill-v4-20261015';DOC=BASE/BATCH;PREV=BASE/'government-xl-ets-parent-join-candidate-v3-20261015'
def main():
 assert not DOC.exists();DOC.mkdir();r=read(PREV/'result.json');refs=[Path(__file__),PREV/'result.json',HERE/'bounded_float32_terrain_gap_boxes_v2_20261010.py',HERE/'exact_original_facet_outward_float32_gap_hull_20261010.py']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 path=PREV/'private-patch.json.gz';refs.append(path);patch=read(path);m=patch['nativeMesh'];positions=copy.deepcopy(m['position']);indices=copy.deepcopy(m['index']);t=np.asarray(positions,dtype='<f4').astype(float).reshape(-1,3)[np.asarray(indices).reshape(-1,3)];p=shapely.polygons(t[:,:,[0,2]]);union=shapely.union_all(p[shapely.area(p)>1e-10]);tree=shapely.STRtree(p)
 resolution=module('stanford_infill_resolution',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer'/patch['meta']['parentTerrain'];parent=read(parentpath);refs.extend([parentpath,HERE/'resolve-pass.py']);bounds=resolution.extent(patch['coarseCells'],parent);domain=shapely.box(*bounds);missing=domain.difference(union)
 source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']=='B360171738601063C0');asset=ROOT/source['asset']['path'];refs.append(asset);assert digest(asset.read_bytes())==source['sourceSHA256'];model=decode_original_world_triangles(asset.read_bytes());norm=np.cross(model[:,1]-model[:,0],model[:,2]-model[:,0]);lens=np.linalg.norm(norm,axis=1);upids=np.flatnonzero((lens>0)&(norm[:,1]>.25*lens));upfaces=model[upids];uppolys=shapely.polygons(upfaces[:,:,[0,2]]);uptree=shapely.STRtree(uppolys);proofs=[];additions=[];accounting=[]
 for part in shapely.get_parts(missing):
  if part.geom_type!='Polygon' or not part.area:continue
  pieces,account=bounded_boxes(part);accounting.append(account)
  for record,box in pieces:
   corners=[]
   for ring in record['exactClippedRings']:
    for xx,zz in ring:
     x,z=F(xx),F(zz);x0,x1,z0,z1=down(x),up(x),down(z),up(z)
     if x0==x1:x0=float(np.nextafter(np.float32(x0),np.float32(-np.inf)));x1=float(np.nextafter(np.float32(x1),np.float32(np.inf)))
     if z0==z1:z0=float(np.nextafter(np.float32(z0),np.float32(-np.inf)));z1=float(np.nextafter(np.float32(z1),np.float32(np.inf)))
     corners.extend([(F(x0),F(z0)),(F(x0),F(z1)),(F(x1),F(z0)),(F(x1),F(z1))])
   poly=hull(corners);region=shapely.Polygon([(float(x),float(z))for x,z in poly]);assert region.area<.1 and domain.covers(region),'Infill exceeds unchanged footprint/parent-domain bounds';groundids=tree.query(region,predicate='intersects');assert len(groundids);roofs=uptree.query(region,predicate='intersects');level=float(t[groundids,:,1].min())
   if len(roofs):level=min(level,float(upfaces[roofs,:,1].min()))
   level=down(level);vs=[[float(x),level,float(z)]for x,z in poly];faces=[[vs[0],vs[k],vs[k+1]]for k in range(1,len(vs)-1)];assert np.array_equal(np.asarray(faces),np.asarray(faces,dtype='<f4').astype(float));additions.extend(faces);proofs.append({'gap':record,'hullXZ':[[str(x),str(z)]for x,z in poly],'surroundingTerrainFaces':groundids.tolist(),'originalUpwardSourceFaces':upids[roofs].tolist(),'levelHKPD':level,'addedTriangles':len(faces)})
 assert additions;offset=len(positions)//3;m['position'].extend(np.asarray(additions).reshape(-1).tolist());m['index'].extend(range(offset,offset+3*len(additions)));assert m['position'][:len(positions)]==positions and m['index'][:len(indices)]==indices
 packed=np.asarray(m['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)];q=shapely.polygons(packed[:,:,[0,2]]);valid=shapely.area(q)>1e-10;u=shapely.union_all(q[valid]);gap=float(u.symmetric_difference(domain).area);excess=float(shapely.area(q[valid]).sum()-u.area);m['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','maximumAreaM2':.25,'measuredAreaM2':gap};m['source']['numericalProjectionOverlap']={'policy':'highest-float32-surface','maximumAreaM2':.25,'measuredAreaM2':excess};patch['id']=BATCH;m['source']['privateGapInfill']={'method':'Minimal outward Float32 hulls of bounded gap pieces; conservative original source/terrain vertex levels. New terrain geometry requires full current validation.','sourceSHA256':source['sourceSHA256'],'addedTriangles':len(additions)}
 try:resolution.validate_patch(patch,parent);validation={'passed':True}
 except (AssertionError,ValueError)as e:validation={'passed':False,'error':str(e)}
 save(DOC/'private-patch.json.gz',patch);save(DOC/'construction.json.gz',{'proofs':proofs,'accounting':accounting,'originalTerrainPositionsAndIndicesPreserved':True,'priorTerrainSHA256':digest(path.read_bytes())});summary={'addedTriangles':len(additions),'candidateTriangles':len(packed),'priorGapM2':missing.area,'afterGapM2':gap,'afterExcessM2':excess,'validation':validation,'sourceGeometryChanges':0,'fullAcceptance':False,'runtimeSourceArithmeticStillRequired':True};save(DOC/'summary.json',summary)
 module('freeze_stanford_infill',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-station-bounded-conservative-float32-gap-infill-v4',refs,{'uids':['landsd/323703:0'],'summary':summary,'fullAcceptance':False});print(summary,flush=True)
if __name__=='__main__':main()
