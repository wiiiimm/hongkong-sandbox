"""Candidate source-pinned parent residuals in minimum runtime representable gap cells.
No geometry acceptance: full packing, source/actor heights and all physical gates remain.
"""
from pathlib import Path
import copy,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from actual_native_parent_transition_v3_20261010 import rectangle,rational,nondegenerate
from exact_original_slab_projection_coverage_20261010 import slab_coverage
BATCH='government-xl-tung-sing-parent-residual-gap-candidate-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAND=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-v3-20261010/candidate-single-native-original-surface.json';GAP=DOC.parent/'government-xl-tung-sing-interior-domain-source-invariance-20261010/diagnostic.json.gz';PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json';FAILED=DOC.parent/'government-xl-tung-sing-exact-gap-source-facets-20261010/diagnostic.json.gz'
def enclosing_runtime_rectangle(bb):
 low=np.nextafter(np.asarray(bb[:2],np.float32),np.float32(-np.inf)).astype(float);high=np.nextafter(np.asarray(bb[2:],np.float32),np.float32(np.inf)).astype(float);return [*low,*high]
assert not DOC.exists();candidate=read(CAND);original=faces(candidate);parent=faces(read(PARENT));lo=parent[:,:,[0,2]].min(1);hi=parent[:,:,[0,2]].max(1);parts=shapely.get_parts(shapely.from_wkb(read(GAP)['rawChildRectangleMissingProjectionWKB']));added=[];records=[]
for gapid,gap in enumerate(parts):
 if gap.is_empty:continue
 bb=enclosing_runtime_rectangle(gap.bounds);ids=np.flatnonzero((hi[:,0]>=bb[0])&(lo[:,0]<=bb[2])&(hi[:,1]>=bb[1])&(lo[:,1]<=bb[3]));dispositions=[]
 for i in ids:
  poly=rectangle([rational(v) for v in parent[i]],bb);start=len(added)
  for j in range(1,len(poly)-1):
   tri=[poly[0],poly[j],poly[j+1]]
   if nondegenerate(tri):added.append(np.asarray(tri,float).astype(np.float32).astype(float))
  dispositions.append({'originalParentFace':int(i),'outputFaceRange':[start,len(added)],'originalVertices':parent[i].tolist(),'exactPrepackClipPolygon':[[str(v) for v in p] for p in poly]})
 records.append({'rawGapPiece':gapid,'rawGapBounds':list(gap.bounds),'rawGapAreaM2':gap.area,'runtimeEnclosingRectangle':bb,'rawGapWKB':shapely.to_wkb(gap,hex=True),'allCandidateParentFacetDispositions':dispositions})
combined=np.concatenate([original,np.asarray(added)]);out=copy.deepcopy(candidate);out['nativeMesh']['position']=combined.reshape(-1).tolist();out['nativeMesh']['index']=list(range(len(combined)*3));out['nativeMesh']['source']['parentResidualGapRecovery']={'policy':'candidate-original-finite-parent-facets-clipped-to-minimum-outward-Float32-enclosing-rectangles','originalParentSHA256':digest(PARENT.read_bytes()),'addedFacets':len(added),'rawStrictGapOnlyRepresentationPossible':False,'physicalAccepted':False};save(DOC/'candidate-single-native-residual-surface.json',out)
checks=[]
for r in read(FAILED)['rows']:
 p=slab_coverage(np.asarray(r['originalTriangle']),combined);checks.append({'originalFace':r['originalFace'],'proof':p});print({'originalFace':r['originalFace'],'exactCoverage':p['exactProjectionCovered']},flush=True)
save(DOC/'diagnostic.json.gz',{'originalFacets':len(original),'combinedFacets':len(combined),'allRawGapPieceDispositions':records,'addedFiniteOriginalParentFaces':np.asarray(added).tolist(),'completeFailedSourceFacetRechecks':checks,'rawStrictGapOnlyRepresentationPossible':False,'qualification':'Candidate residual footprint is explicitly larger than the raw gap because a strictly contained nonzero Float32 facet cannot represent a subquantum wedge. Every addition derives from complete unchanged finite original parent facets; existing government building meshes untouched. This grants no surface/physical/support approval; all source current ground, neighbour/native/foreign and domain/runtime gates must independently pass. No arbitrary epsilon merge or source geometry shift.','inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [CAND,GAP,PARENT,FAILED,Path(__file__)]},'modelGeometryChanges':0,'physicalAccepted':False,'candidateRuntimeTriangleSHA256':digest(combined.astype('<f8').tobytes())});print({'originalFacets':len(original),'addedFacets':len(added),'combinedFacets':len(combined)},flush=True)
