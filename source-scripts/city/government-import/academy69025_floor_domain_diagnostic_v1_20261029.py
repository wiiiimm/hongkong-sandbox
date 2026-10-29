"""Preserve the exact private floor-return coverage failure; no approval or edits."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from bounded_original_upward_floor_domains_v1_20261029 import inset
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-academy69025-floor-domain-diagnostic-v1-20261029'
BASE=ROOT/'docs/astra-city/government-import'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    patch='government-xl-academy69025-complete-tin-current-v1-20261029-69025-0-inset'
    runtime='government-xl-academy69025-complete-tin-current-v1-20261029-69025-0-runtime'
    packet='government-xl-academy69025-upward-low-packet-v1-20261029'
    r=take(patch,BASE/patch/'summary.json');mesh=take(patch,ROOT/r['candidate']['path'])['nativeMesh']
    row=take(runtime,BASE/runtime/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    nominated=take(packet,BASE/packet/'summary.json');ids=[r['face']for r in nominated['rows']]
    source=decode_original_world_triangles(asset.read_bytes())[ids]
    terrain=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
    after,proof=inset(terrain,source);outer=shapely.from_wkt(proof['outerWKT']);domain=shapely.union_all(shapely.polygons(terrain[:,:,[0,2]]));missing=outer.difference(domain)
    assert not missing.is_empty,'Previously observed failure changed; investigate'
    centre=np.mean(outer.bounds[:2]+outer.bounds[2:])
    # A second coordinate origin is diagnostic only; it grants no coverage credit.
    from shapely.affinity import translate
    localterrain=terrain[:,:,[0,2]]-np.array([float(outer.centroid.x),float(outer.centroid.y)])
    localdomain=shapely.union_all(shapely.polygons(localterrain));localouter=translate(outer,xoff=-outer.centroid.x,yoff=-outer.centroid.y)
    localmissing=localouter.difference(localdomain)
    save(out/'missing-domain.wkt',missing.wkt) if False else None
    out.mkdir();(out/'missing-domain.wkt').write_text(missing.wkt+'\n');save(out/'inset-proof.json.gz',proof)
    result=dict(uids=['landsd/69025:0'],sourceSHA256=row['sourceSHA256'],sourceFaces=ids,sourcePatch=r['candidate'],proposedTerrainFaces=len(after),missingSetEmpty=False,missingAreaM2=float(missing.area),missingBounds=list(missing.bounds),missingGeometryType=missing.geom_type,localOriginMissingSetEmpty=bool(localmissing.is_empty),localOriginMissingAreaM2=float(localmissing.area),floorReturnAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,terrainEdits=False,qualification='Reproduces existing strict coverage failure from exact production Float32 input and six exact original upward facets. No tolerance, domain clipping, source change, guard waiver or installation. Local-origin comparison is diagnostic only; full source-domain proof or a genuinely covered bounded domain is required.')
    save(out/'summary.json',result);refs.extend([HERE/'bounded_original_upward_floor_domains_v1_20261029.py',HERE/'bounded_original_upward_floor_return_v1_20261029.py',HERE/'selected_original_upward_floor_terrain_return_v2_20261029.py'])
    module('academy_floor_domain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-academy-private-floor-return-uncovered-domain-diagnostic',refs,result);print(result,flush=True)
if __name__=='__main__':main()
