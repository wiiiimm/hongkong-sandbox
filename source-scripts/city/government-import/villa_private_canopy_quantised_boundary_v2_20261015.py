"""Private source-bound procedural cut with an explicit Float32 packing clearance budget."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-villa-private-canopy-source-boundary-feasibility-v1-20261015';DOC=B/'government-xl-villa-private-canopy-quantised-boundary-v2-20261015'
def main():
 assert not DOC.exists();p=OLD/'proposal.json';pins={r['path']:r['sha256'] for r in read(OLD/'result.json')['evidenceRefs']};assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];old=read(p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';tile=ROOT/'3d-viewer/city/data/tiles/-7_-9.json';assert digest(manifest.read_bytes())==old['manifestSHA256'];assert digest(tile.read_bytes())==old['tileSHA256']
 sp=B/'government-xl-villa-premiere-complete-record-projection-identity-20261010/selection.json.gz';row=read(sp)['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==old['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());source=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));rings=old['currentForm']['rings'];roof=Polygon(rings[0],rings[1:]);coords=np.asarray(rings[0]);maxabs=np.max(abs(coords),axis=0).astype(np.float32);spacing=np.spacing(maxabs).astype(float)
 # One full two-axis ULP is twice the nearest-rounding vertex displacement bound.
 # Only fallback footprint is inset from immutable source; strict collision limits unchanged.
 margin=float(np.linalg.norm(spacing));assert 0<margin<.003
 expanded=source.buffer(margin,join_style=2);candidate=roof.difference(expanded);assert candidate.is_valid and not candidate.is_empty and candidate.difference(roof).area==0
 parts=list(candidate.geoms) if candidate.geom_type=='MultiPolygon' else [candidate];assert all(g.geom_type=='Polygon' for g in parts)
 proposal={**old,'privateCandidateRings':[[list(g.exterior.coords),*[list(h.coords) for h in g.interiors]] for g in parts],'retainedFootprintAreaM2':candidate.area,'retainedFraction':candidate.area/roof.area,'candidateParts':len(parts),'residualProjectedIntersectionAreaM2':candidate.intersection(source).area,'removedSourceOccupiedProjectionAreaM2':roof.intersection(source).area,'additionalProceduralPrecisionClearanceAreaM2':roof.area-candidate.area-roof.intersection(source).area,'sourceBoundaryClearanceM':margin,'coordinateFloat32ULPsM':spacing.tolist(),'policy':'Private procedural-only correction. Full-ULP diagonal clearance from exact original podium projection bounds nearest Float32 vertex rounding. This changes estimated fallback geometry, never source geometry or collision thresholds. Fresh production and exact checks govern; no general error-proof or acceptance claim.'}
 DOC.mkdir();save(DOC/'proposal.json',proposal)
 module('villa_quantised_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'private-fallback-source-bound-float32-clearance-proposal-v2',[Path(__file__),p,OLD/'result.json',sp,asset,manifest,tile],{'uids':[old['uid'],row['uid']],'sourceBuildingGeometryChanged':False,'liveGeometryChanged':False,'proposedProceduralGeometryChange':True,'sourceBoundaryClearanceM':margin,'retainedFraction':proposal['retainedFraction'],'candidateParts':len(parts),'fullAcceptance':False,'nextStep':'Production generation and exact complete collision/witness checks; no publication until remaining full gates pass.'})
 collision=module('villa_quantised_collision',HERE/'villa_private_canopy_collision_v1_20261015.py');collision.OLD=DOC;collision.NAME='government-xl-villa-private-canopy-collision-v2-20261015';collision.DOC=B/collision.NAME;collision.main()
 witness=module('villa_quantised_witness',HERE/'villa_private_canopy_volume_witness_v1_20261015.py');witness.OLD=collision.DOC;witness.DOC=B/'government-xl-villa-private-canopy-volume-witness-v2-20261015';witness.main()
if __name__=='__main__':main()
