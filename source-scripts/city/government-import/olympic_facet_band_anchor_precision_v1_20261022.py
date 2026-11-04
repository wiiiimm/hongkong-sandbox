"""Account exact outer/core source-plane anchors without assuming one terrain layer."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_plane_precision_v1 import assess
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-band-anchor-precision-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-olympic-facet-band-return-v1-20261022';r,pins=authenticate(prior);path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['candidate']['sha256'];p=read(path);cp=prior/'facet-band-certificate.json.gz';assert digest(cp.read_bytes())==pins[str(cp.relative_to(ROOT))];cert=read(cp);oldpath=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(oldpath.read_bytes())==r['candidate']['replaces']['sha256'];newprior=BASE/'government-xl-olympic-narrow-retained-candidate-v1-20261022';nr,_=authenticate(newprior);newpath=ROOT/nr['candidate']['path'];assert digest(newpath.read_bytes())==nr['candidate']['sha256'];rootpath=ROOT/'3d-viewer/city/data/terrain.json';builder=module('band_precision_root_sampler',HERE/'resolve_pass_indexed_parent_clipping_v2.py');sampler=builder.terrain.fine.DemSampler(read(rootpath),rendered=True)
 def faces(node):return np.asarray(node['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(node['nativeMesh']['index']).reshape(-1,3)]
 old,new=faces(read(oldpath)),faces(read(newpath));raw=np.asarray(p['nativeMesh']['position']).reshape(-1,3)[np.asarray(p['nativeMesh']['index']).reshape(-1,3)];assert len(raw)==len(cert['outputLineage']);rows=[]
 for i,origin in enumerate(cert['outputLineage']):
  if origin['kind']!='bandFacetsGenerated':continue
  for vertex,v in enumerate(raw[i]):
   gpu=v.astype('<f4').astype('<f8')
   for kind,bounds in [('outer',cert['outer']),('core',cert['inner'])]:
    if not(bounds[0]<=gpu[0]<=bounds[2]and bounds[1]<=gpu[2]<=bounds[3]and(gpu[0]in[bounds[0],bounds[2]]or gpu[2]in[bounds[1],bounds[3]])):continue
    source=origin['sourceFace']if kind=='outer'else origin['fieldOwnerSourceFace'];row=dict(outputFace=i,vertex=vertex,boundary=kind,sourceFace=source)
    if source is not None:row.update(assess((old if kind=='outer'else new)[source],v))
    else:
     expected=sampler.ground(float(v[0]),float(v[2]));delta=abs(F(float(v[1]))-F(float(expected)));budget=sum(F(abs(float(np.spacing(np.float32(q)))))/2 for q in v);row.update(rootGeneratedGapFacet=True,rawRootHeightErrorM=str(delta),coordinateHalfULPSumM=str(budget),withinNativeCoordinatePrecision=delta<=budget)
    rows.append(row)
 assert rows;unresolved=[r for r in rows if not r['withinNativeCoordinatePrecision']];save(doc/'anchors.json.gz',rows);result=dict(uids=r['uids'],checkedBoundaryVertexOccurrences=len(rows),originalNativePlaneAnchors=sum(r['sourceFace']is not None for r in rows),generatedRootGapAnchors=sum(r['sourceFace']is None for r in rows),unresolved=unresolved,sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,qualification='Exact 3D source-plane residual upper bounds at outer/core joins, relative only to Float32 coordinate precision. Keeps authored layers separate; not a single-upper-height graph or source contact/coverage/placement approval. Root-gap anchors correspond to actual generated terrain facets, not metadata-only coverage credit.')
 save(doc/'summary.json',result);refs=[Path(__file__),prior/'result.json',cp,path,oldpath,newprior/'result.json',newpath,rootpath,HERE/'native_plane_precision_v1.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py'];module('band_precision_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-generated-band-source-plane-anchor-precision',refs,result);print(dict(anchors=len(rows),unresolved=len(unresolved),rootGapAnchors=result['generatedRootGapAnchors']),flush=True)
if __name__=='__main__':main()
