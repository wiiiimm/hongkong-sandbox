"""Acquisition-only pointers; actual parent/proposal/adjacent seams replayed."""
import math
from original_disjoint_routing_metadata_scope_20261010 import canonical,subtree
from original_unchanged_adjacent_terrain_boundary_20261010 import verify as verify_seam,sha
from native_patch_resolution import _faces,_patch_bounds

def boundaries(preflight,manifest,candidates,seams,*,candidate_ref,seam_ref,manifest_ref,actual_assets,proposal):
 assert preflight['currentManifest']==manifest_ref and manifest_ref['path']=='3d-viewer/city/data/manifest.json'
 assert len(candidates)==1 and candidates[0]==preflight['immutableTerrainProposal'];candidate=candidates[0];replacement=candidate['replaces'];assert not candidate.get('replacesMany') and replacement['retainedUids']
 assert candidate_ref['path'].endswith('/terrain-candidates.json') and seam_ref['path'].endswith('/exact-unchanged-adjacent-terrain-seams.json')
 assert _patch_bounds(proposal)==candidate['bounds'] and seams['terrainProposal']==dict(path=candidate['path'],sha256=candidate['sha256'])
 rows=preflight['completeCurrentTerrainRouting'];entries=manifest['terrainPatches'];assert len(rows)==len(entries) and len({e['url'] for e in entries})==len(entries)
 assert set(actual_assets)=={e['url'] for e in entries};parent=actual_assets[replacement['url']];assert parent['ref']['sha256']==replacement['sha256'];assert _patch_bounds(parent['data'])==candidate['bounds']
 b=candidate['bounds'];assert len(b)==4 and all(math.isfinite(x) for x in b) and b[0]<b[2] and b[1]<b[3]
 seam_by_url={r['adjacentURL']:r['proof'] for r in seams['rows']};assert len(seam_by_url)==len(seams['rows']);used=set();result=[];parent_count=0
 for i,(row,entry) in enumerate(zip(rows,entries)):
  assert row['entry']==entry and row['asset']==actual_assets[entry['url']]['ref'] and row['asset']['path']=='3d-viewer/'+entry['url'];assert entry['url'].startswith('city/data/') and '..' not in entry['url'].split('/')
  bounds=row['testedBounds'];assert bounds
  for other in bounds:assert len(other)==4 and all(math.isfinite(x) for x in other) and other[0]<=other[2] and other[1]<=other[3]
  if entry['url']==replacement['url']:
   assert row['exactDeclaredParentReplacement'] is True and entry['sha256']==replacement['sha256'];parent_count+=1
  else:
   assert row['exactDeclaredParentReplacement'] is False
   if any(not(o[2]<b[0] or o[0]>b[2] or o[3]<b[1] or o[1]>b[3]) for o in bounds):
    assert len(bounds)==1 and entry['url'] in seam_by_url
    actual=actual_assets[entry['url']];assert _patch_bounds(actual['data'])==bounds[0]
    binding=dict(completeOriginalParentTrianglesSHA256=sha(_faces(parent['data'])),completeProposalTrianglesSHA256=sha(_faces(proposal)),completeUnchangedAdjacentTrianglesSHA256=sha(_faces(actual['data'])),currentManifestSHA256=manifest_ref['sha256'],parentAsset=parent['ref'],proposalAsset=dict(path=candidate['path'],sha256=candidate['sha256']),unchangedAdjacentAsset=actual['ref'])
    proof=verify_seam(_faces(parent['data']),_faces(proposal),_faces(actual['data']),parent_bounds=b,proposal_bounds=b,adjacent_bounds=bounds[0],expected_binding=binding,current_binding=binding);assert proof==seam_by_url[entry['url']];used.add(entry['url'])
  if 'source' in entry:result.append(dict(pointer=f'/completeCurrentTerrainRouting/{i}/entry/source',canonicalSHA256=canonical(entry['source']),documentType='exact-parent-replacement-routing-acquisition-provenance-v1',boundCandidateRef=candidate_ref,boundSeamRef=seam_ref,boundManifestRef=manifest_ref,qualification='Only authoritative manifest acquisition provenance is nonrecursive. All routing asset bytes, exact parent replacement and complete unchanged adjacent affine seam remain replayed; own source/TIN/ground/core inputs never omitted.'))
 assert parent_count==1 and used==set(seam_by_url)
 return result

def verify_boundaries(preflight,manifest,candidates,seams,declared,**kwargs):
 expected=boundaries(preflight,manifest,candidates,seams,**kwargs);assert declared==expected
 for r in declared:assert canonical(subtree(preflight,r['pointer']))==r['canonicalSHA256']
 return {r['pointer'] for r in declared}
