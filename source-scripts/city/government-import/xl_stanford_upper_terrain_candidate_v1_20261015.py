"""Private exact upper cells for overlapping repaired terrain; no model changes."""
from pathlib import Path
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_finite_upper_surface_cells_20261011 import partition,height
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-upper-terrain-candidate-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();DOC.mkdir();prev=BASE/'government-xl-stanford-patch-overlap-context-v1-20261015';receipt=read(prev/'result.json');refs=[Path(__file__),prev/'result.json',HERE/'exact_finite_upper_surface_cells_20261011.py'];
 for q in receipt['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 path=prev/'repaired-unapproved-patch.json.gz';refs.append(path);patch=read(path);m=patch['nativeMesh'];positions=np.asarray(m['position'],dtype='<f4').astype(float).reshape(-1,3);tri=positions[np.asarray(m['index']).reshape(-1,3)];polys=shapely.polygons(tri[:,:,[0,2]]);tree=shapely.STRtree(polys);left,right=tree.query(polys,predicate='intersects');targets=set();pairs=[]
 for a,b in zip(left,right):
  if a>=b:continue
  overlap=polys[a].intersection(polys[b])
  if overlap.area<=1e-10:continue
  targets.update([int(a),int(b)]);pairs.append([int(a),int(b)])
 output=[];lineage=[];proofs=[]
 for i,t in enumerate(tri):
  if i not in targets:output.append(t.tolist());lineage.append({'originalPatchFace':i,'unchanged':True});continue
  ids=sorted(int(j)for j in tree.query(polys[i],predicate='intersects')if polys[j].area>1e-10);assert i in ids
  cells,proof=partition(t,tri[ids],max_cells=20000,max_operations=500000)
  own=ids.index(i);selected=[c for c in cells if c['faceIndex']==own];count=0
  for cell in selected:
   p=cell['polygon'];h=cell['plane']
   for k in range(1,len(p)-1):
    points=[p[0],p[k],p[k+1]];out=[[float(v[0]),float(height(v,h)),float(v[2])]for v in points];output.append(out);lineage.append({'originalPatchFace':i,'unchanged':False});count+=1
  proofs.append({'originalPatchFace':i,'competitorFaces':ids,'retainedTriangles':count,'certificate':proof})
  print(i,len(targets),'retained',count,flush=True)
 out=np.asarray(output);assert np.isfinite(out).all();candidate=copy.deepcopy(patch);candidate['id']=BATCH;candidate['nativeMesh']['position']=out.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(len(out)*3));candidate['nativeMesh']['source'].update(policy='Private repaired terrain upper cells, exact rational plane selection followed by Float32 packing; unchanged original buildings. Full runtime and neighbour acceptance pending.',privateUpperSurface={'sourceCandidate':str(path.relative_to(ROOT)),'sourceSHA256':digest(path.read_bytes()),'overlapFaces':len(targets),'originalPatchTriangles':len(tri),'candidateTriangles':len(out)})
 save(DOC/'private-patch.json.gz',candidate);save(DOC/'exact-cells.json.gz',{'proofs':proofs,'lineage':lineage,'pairs':pairs},) if False else None
 # Fraction strings preserve all exact certificate values.
 import json,gzip
 (DOC/'exact-cells.json.gz').write_bytes(gzip.compress(json.dumps({'proofs':proofs,'lineage':lineage,'pairs':pairs},default=str,separators=(',',':')).encode()))
 validator=module('stanford_upper_validator',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';refs.extend([parentpath,HERE/'resolve-pass.py']);parent=read(parentpath)
 try:validator.validate_patch(candidate,parent);validation={'passed':True}
 except (AssertionError,ValueError)as e:validation={'passed':False,'error':str(e)}
 packed=out.astype('<f4').astype(float);p=shapely.polygons(packed[:,:,[0,2]]);valid=shapely.area(p)>1e-10;union=shapely.union_all(p[valid]);bounds=validator.extent(candidate['coarseCells'],parent);summary={'originalTriangles':len(tri),'overlapFaces':len(targets),'candidateTriangles':len(out),'projectedExcessM2':float(shapely.area(p[valid]).sum()-union.area),'rectangleDifferenceM2':float(union.symmetric_difference(shapely.box(*bounds)).area),'validation':validation,'sourceGeometryChanges':0,'publication':False,'qualification':'Exact finite upper cells before Float32 conversion. Closed-boundary height jumps retained in certificates; seam, complete actor and runtime checks pending.'};save(DOC/'summary.json',summary)
 module('freeze_stanford_upper',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-upper-terrain-construction-v1',refs,{'uids':['landsd/305584:0','landsd/335875:0'],'summary':summary,'fullAcceptance':False});print(summary,flush=True)
if __name__=='__main__':main()
