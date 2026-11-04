"""Record a rejected exact-clip operand; original algorithm and guards unchanged."""
import sys,inspect
from pathlib import Path
import shapely
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_affine_halfplane_clip_v2_20261030 import lower_region
batch=sys.argv[sys.argv.index('--batch')+1]
assert batch.startswith('government-xl-')and'/'not in batch
out=HERE/'local'/batch
original=module('diagnostic_original_inset',HERE/'selected_original_local_inset_v18_20261101.py')
def capture(region,difference):
 try:return lower_region(region,difference)
 except AssertionError:
  assert out.exists()
  (out/'capture-wrapper.py').write_bytes(Path(__file__).read_bytes())
  frame=inspect.currentframe().f_back.f_locals
  if all(k in frame for k in ['i','j','source','planes','source_refs']):
   ids=[int(frame['i']),int(frame['j'])]
   save(out/'rejected-source-plane-pair.json',dict(indices=ids,sourceFaces=[frame['source'][i].tolist() for i in ids],fittedPlanes=[list(map(float,frame['planes'][i])) for i in ids],sourceRefs=frame['source_refs'],sourceGeometryChanges=0,qualification='Read-only original caller operands; source facets/planes and algorithm unchanged.'))
  path=out/'rejected-clip-input.json';assert not path.exists()
  save(path,dict(regionWKB=region.wkb_hex,difference=list(map(float,difference)),regionArea=float(region.area),regionValid=bool(region.is_valid),regionType=region.geom_type,canonicalKernelSHA256=digest((HERE/'exact_affine_halfplane_clip_v2_20261030.py').read_bytes()),instrumentationSHA256=digest(Path(__file__).read_bytes()),sourceGeometryChanges=0,tolerancesChanged=False,qualification='Exact rejected original-kernel input; logger records only and rethrows. No geometry repair, approval or publication.'))
  raise
original.lower_region=capture
original.main()
