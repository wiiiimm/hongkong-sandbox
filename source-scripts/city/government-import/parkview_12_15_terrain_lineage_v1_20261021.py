"""Independently verify retained faces and original highest-surface selection."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from china_merchants_finite_inset_v4_20261021 import plane
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-12-15-terrain-lineage-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-parkview-12-15-private-terrain-v1-20261021'
assert not DOC.exists();_,pins=authenticate(SRC);refs=[Path(__file__),SRC/'result.json']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
line=take(SRC/'lineage.json.gz');candidate=take(SRC/'terrain-candidates.json')[0];patch=take(ROOT/candidate['path']);oldpath=ROOT/'3d-viewer'/candidate['replaces']['url'];old=take(oldpath)
def faces(p):return np.asarray(p['nativeMesh']['position'],dtype='<f8').reshape(-1,3)[np.asarray(p['nativeMesh']['index']).reshape(-1,3)]
oldfaces=faces(old);newfaces=faces(patch);assert len(newfaces)==len(line['outputLineage']);outer=shapely.box(*line['outerBounds']);unchanged=[];parentErrors=[]
for face,entry in zip(newfaces,line['outputLineage']):
 original=oldfaces[entry['parentFace']]
 if entry['kind']=='unchanged':assert np.array_equal(face,original);unchanged.append(entry['parentFace'])
 elif entry['kind']=='parent-fragment':
  coefficients=plane(original);parentErrors.extend(np.abs(face[:,1]-(face[:,[0,2]]@coefficients[:2]+coefficients[2])))
 else:assert shapely.Polygon(face[:,[0,2]]).difference(outer).area<1e-10
assert set(unchanged)|set(line['changedParentFaces'])==set(range(len(oldfaces))) and not set(unchanged)&set(line['changedParentFaces'])
raw=np.asarray(line['originalClippedTerrainFaces']);selected=np.asarray(line['sourceFaces']);polygons=shapely.polygons(raw[:,:,[0,2]]);tree=shapely.STRtree(polygons);coefficients=[plane(f)for f in raw];residual=[];shortfall=[];pairs=0
for face,sourceId in zip(selected,line['highestSourceLineage']):
 poly=shapely.Polygon(face[:,[0,2]]);c=coefficients[sourceId];residual.extend(np.abs(face[:,1]-(face[:,[0,2]]@c[:2]+c[2])))
 for j in tree.query(poly,predicate='intersects'):
  overlap=poly.intersection(polygons[j])
  if overlap.area<=1e-10:continue
  coords=shapely.get_coordinates(overlap);other=coefficients[j];shortfall.extend(coords@other[:2]+other[2]-(coords@c[:2]+c[2]));pairs+=1
summary=dict(uids=['landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'],unchangedParentFaces=len(unchanged),changedParentFaces=len(line['changedParentFaces']),allParentFacesAccounted=True,maximumParentPlaneResidualM=float(max(parentErrors,default=0)),maximumSourcePlaneResidualM=float(max(residual,default=0)),maximumUpperSurfaceShortfallM=float(max(shortfall,default=0)),positiveAreaPairsChecked=pairs,installationApproved=False,productionChanges=0)
save(DOC/'diagnostic.json',summary)
assert summary['maximumParentPlaneResidualM']<=1e-6 and summary['maximumSourcePlaneResidualM']<=1e-6 and summary['maximumUpperSurfaceShortfallM']<=1e-6
save(DOC/'verification.json',summary);refs.append(HERE/'china_merchants_finite_inset_v4_20261021.py');module('parkview_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-terrain-retention-and-highest-source-verification',refs,summary);print(summary,flush=True)
