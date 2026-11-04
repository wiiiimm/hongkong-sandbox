"""Private nested-pair terrain validation; no publication entry point."""
from pathlib import Path
from primrose_compound_foundation_v2_20261015 import module
from nested_native_terrain_validation_v1_20261027 import validate_native_mesh
from nested_coordinated_native_boundary_v1_20261027 import validate_effective_coordinated_members

_canonical = module('nested_pair_canonical_grid_validator', Path(__file__).parent.parent/'island-detail-integration/publish.py')
validate_grid = _canonical.validate_grid
check_patch_overlap = _canonical.check_patch_overlap


def validate_patch(p,parent):
 validate_grid(p)
 validate_native_mesh(p,parent)
 cells=p['coarseCells'];assert len(cells)==4 and all(type(v) is int for v in cells),'Invalid terrain coarseCells'
 x0,z0,x1,z1=cells
 assert 0<=x0<x1<parent['w'] and 0<=z0<z1<parent['h'],'Terrain patch outside parent grid'
 g=parent['meta']['georef'];f=p['meta']['georef']
 assert abs(g['bE']+x0*g['aE']-f['bE'])<1e-5 and abs(g['bN']+z0*g['aN']-f['bN'])<1e-5,'Terrain patch origin misaligned'
 assert abs((x1-x0)*g['aE']-(p['w']-1)*f['aE'])<1e-5 and abs((z1-z0)*g['aN']-(p['h']-1)*f['aN'])<1e-5,'Terrain patch extent misaligned'
 assert f['aE']<g['aE'],'Terrain patch must refine the parent grid'
 children=[]
 for child in p.get('patches',[]):
  validate_patch(child,p);check_patch_overlap(child,children);children.append(child)
 validate_effective_coordinated_members(children)
