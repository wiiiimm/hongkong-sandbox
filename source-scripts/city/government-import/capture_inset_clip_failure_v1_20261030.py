"""Record a rejected exact-clip operand; original algorithm and guards unchanged."""
import sys
from pathlib import Path
import shapely
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_affine_halfplane_clip_v1_20261024 import lower_region
batch=sys.argv[sys.argv.index('--batch')+1]
assert batch.startswith('government-xl-')and'/'not in batch
out=ROOT/'docs/astra-city/government-import'/batch
original=module('diagnostic_original_inset',HERE/'selected_original_local_inset_v15_20261028.py')
def capture(region,difference):
 try:return lower_region(region,difference)
 except AssertionError:
  path=out/'rejected-clip-input.json';assert not path.exists()
  save(path,dict(regionWKB=region.wkb_hex,difference=list(map(float,difference)),regionArea=float(region.area),regionValid=bool(region.is_valid),regionType=region.geom_type,canonicalKernelSHA256=digest((HERE/'exact_affine_halfplane_clip_v1_20261024.py').read_bytes()),instrumentationSHA256=digest(Path(__file__).read_bytes()),sourceGeometryChanges=0,tolerancesChanged=False,qualification='Exact rejected original-kernel input; logger records only and rethrows. No geometry repair, approval or publication.'))
  raise
original.lower_region=capture
original.main()
