"""Use the existing strict nested validator for one hash-bound candidate only.

No CLI, approval, publisher guard bypass or publication call. Every other patch
uses the canonical validator. Canonical publication code is never edited.
"""
from pathlib import Path
from run import ROOT,HERE,read,digest
from primrose_compound_foundation_v2_20261015 import module
from nested_terrain_patch_validation_v1_20261027 import validate_patch as nested_validate
from original_coordinated_retained_contract_v1_20261027 import verify_terrain

def publisher(name,prior_path,candidate_path,owners,sources,patch):
 prior_path=Path(prior_path).resolve();candidate_path=Path(candidate_path).resolve()
 assert prior_path.is_relative_to(ROOT)and candidate_path.is_relative_to(ROOT)
 prior,candidate=read(prior_path),read(candidate_path)
 assert str(candidate_path.relative_to(ROOT))==patch['candidate']['path']
 retention=verify_terrain(prior,candidate,owners,sources,patch,digest(prior_path.read_bytes()),digest(candidate_path.read_bytes()))
 canonical=module(name,HERE.parent/'island-detail-integration/publish.py');original=canonical.validate_patch
 parent=ROOT/'3d-viewer/city/data/terrain.json';parent_sha=digest(parent.read_bytes());expected_parent=read(parent)
 def validate(node,grid):
  if node==candidate:
   assert digest(prior_path.read_bytes())==patch['replacedNativeTerrain'][0]['sha256']and digest(candidate_path.read_bytes())==patch['candidate']['sha256']
   assert digest(parent.read_bytes())==parent_sha and grid==expected_parent,'Exact current root terrain required'
   nested_validate(node,grid)
  else:original(node,grid)
 canonical.validate_patch=validate
 return canonical,retention
