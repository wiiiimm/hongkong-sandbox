"""Exact finite original-podium coverage at every raw domain-gap hit."""
import numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_slab_projection_coverage_20261010 import slab_coverage
BATCH='government-xl-tung-sing-exact-gap-source-facets-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-tung-sing-interior-current-identity-inputs-20261010/selection.json.gz';CAND=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-v3-20261010/candidate-single-native-original-surface.json';GAP=DOC.parent/'government-xl-tung-sing-interior-domain-source-invariance-20261010/diagnostic.json.gz'
assert not DOC.exists();gap=shapely.from_wkb(read(GAP)['rawChildRectangleMissingProjectionWKB']);ground=faces(read(CAND));row=next(r for r in read(INPUT)['rows'] if r['uid']=='landsd/126434:0');asset=ROOT/row['candidate']['path'];source=decode_original_world_triangles(asset.read_bytes());poly=shapely.polygons(source[:,:,[0,2]]);ids=np.flatnonzero(shapely.intersects(poly,gap));rows=[]
for i in ids:
 proof=slab_coverage(source[i],ground);rows.append({'originalFace':int(i),'originalTriangle':source[i].tolist(),'rawGapAreaM2':float(poly[i].intersection(gap).area),'proof':proof});print({'originalFace':int(i),'exactCovered':proof['exactProjectionCovered'],'witness':proof.get('exactUncoveredInteriorWitnessXZ')},flush=True)
save(DOC/'diagnostic.json.gz',{'rows':rows,'allRawIntersectingSourceFaceIds':ids.tolist(),'completeSourceFaces':len(source),'completeGroundFacets':len(ground),'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [INPUT,CAND,GAP,asset,Path(__file__)]},'physicalAccepted':False,'modelGeometryChanges':0,'qualification':'Every original face with even line/point intersection to the raw gap is tested against ALL finite candidate ground triangles using exact Fraction slabs and closed edges. Failure is a real finite witness, never tolerance credit.'})
