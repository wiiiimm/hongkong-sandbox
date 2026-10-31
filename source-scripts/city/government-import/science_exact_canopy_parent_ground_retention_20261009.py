"""One exact unchanged Science canopy ground-retention trial; no acceptance waiver."""
import importlib.util,json,numpy as np,shapely
from run import ROOT,HERE,read,digest
from science_attached_open_canopy_identity_20261009 import UID,RELATED,SOURCE_SHA
from science_whole_original_disjoint_parent_retention_20261009 import preserve as preserve_disjoint
INPUT=ROOT/'docs/astra-city/government-import/government-xl-science-attached-open-canopy-current-identity-20261009'
def preserve(patch,bounds,sampler,projection,current_forms,patches):
 disjoint=preserve_disjoint(patch,bounds,sampler,projection,current_forms,patches);canopy=next(b for b,_,_ in current_forms if b['uid']==RELATED);expected=read(INPUT/'identity-proof.json')['currentRelatedForm'];assert canopy==expected
 region=shapely.Polygon(canopy['rings'][0],canopy['rings'][1:]);assert region.is_valid and region.area>0
 selection=read(INPUT/'selection.json.gz');row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE_SHA
 spec=importlib.util.spec_from_file_location('science_protected_parent_exact_decode',HERE/'xl-second-pass.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.LOCAL=HERE/'local/government-xl-science-attached-canopy-complete-original-physical-20261009';t=d.glb_triangles(row);assert digest(t.astype('<f8').tobytes())==read(INPUT/'identity-proof.json')['worldTrianglesSHA256'];whole=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));assert whole.symmetric_difference(projection).area<1e-8
 face_projection=shapely.polygons(t[:,:,[0,2]]);faces=np.flatnonzero(shapely.intersects(face_projection,region)).tolist();proof=patches.preserve_parent_under_projection(patch,bounds,region,sampler)
 proof.update(uid=RELATED,exactWholeCurrentForm=canopy,exactProtectedRegionGeoJSON=json.loads(shapely.to_geojson(region)),rawOriginalProjectionIntersectionM2=region.intersection(whole).area,affectedWholeOriginalFaceIDs=faces,sourceSHA256=SOURCE_SHA,worldTrianglesSHA256=digest(t.astype('<f8').tobytes()),sourceGeometryChanges=0,currentCanopyBodyChanges=0,currentCanopyMetadataChanges=0,physicalAcceptanceExemption=False,qualified='Exact current canopy footprint only, no padding. Retain parent drawn ground as a trial; full original surface/support/foundation checks must independently reject any resulting interference. No surveyed canopy height or full physical acceptance claimed.')
 return {'disjointOriginalPolicy':disjoint,'exactCanopyGroundTrial':proof}
