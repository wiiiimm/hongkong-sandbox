"""Declare only sub-2mm float32 terrain slivers within existing coverage policy."""
import hashlib,json
import shapely
from native_patch_resolution import projected_context


def geometry_sha(patch):
    mesh=patch['nativeMesh']
    return hashlib.sha256(json.dumps([mesh['position'],mesh['index']],separators=(',',':')).encode()).hexdigest()


def approve_roundoff(patch,bounds):
    before=geometry_sha(patch);_,polygons,missing,_=projected_context(patch,bounds)
    union=shapely.union_all(polygons);extent=shapely.box(*bounds);difference=union.symmetric_difference(extent)
    area=float(difference.area)
    assert 0<area<=.25,'Coverage residue exceeds existing 0.25m2 numerical allowance'
    assert missing.difference(union.buffer(.002)).area<1e-8,'Coverage hole exceeds existing 2mm float32/boundary distance'
    assert union.difference(extent.buffer(.002)).area<1e-8,'Native geometry exceeds existing 2mm boundary distance'
    proof={'policy':'parent-grid-fallback','measuredAreaM2':area,'maximumAreaM2':.25,
           'maximumRoundoffDistanceM':.002,'missingAreaM2':float(missing.area),
           'geometrySHA256':before,'qualification':'Metadata declaration only: native float32 terrain geometry is unchanged. Existing full source contact, foundation and runtime/rendered sampler checks remain mandatory.'}
    patch['nativeMesh']['source']['numericalCoverageGap']=proof
    assert geometry_sha(patch)==before
    return proof
