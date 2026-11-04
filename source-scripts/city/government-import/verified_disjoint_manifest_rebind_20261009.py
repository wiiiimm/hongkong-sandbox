"""Reject reuse after any regional change; never changes numeric acceptance."""
import math

def box(value):
 assert len(value)==4 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in value),'Malformed finite region'
 assert value[0]<=value[2] and value[1]<=value[3],'Reversed region'
 return value

def disjoint(a,b):
 a,b=box(a),box(b)
 return a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1]

def verify(old_manifest,new_manifest,old_inventory,new_inventory,region,*,expected_old_hashes,current_old_input_hashes,manifest_path,old_manifest_sha,new_manifest_sha):
 box(region);assert old_manifest_sha!=new_manifest_sha,'Rebind must identify a changed global manifest'
 assert expected_old_hashes.get(manifest_path)==old_manifest_sha
 assert set(current_old_input_hashes)==set(expected_old_hashes),'Omitted frozen numeric input'
 assert current_old_input_hashes[manifest_path]==new_manifest_sha
 assert all(current_old_input_hashes[p]==h for p,h in expected_old_hashes.items() if p!=manifest_path),'Regional numeric/source input changed'
 allowed={'officialModelCatalogues','terrainPatches'}
 assert {k:v for k,v in old_manifest.items() if k not in allowed}=={k:v for k,v in new_manifest.items() if k not in allowed},'Unclassified manifest rendering change'
 changes=[]
 for kind in ['terrain','native']:
  old,new=old_inventory[kind],new_inventory[kind]
  assert len(old)==len({r['id'] for r in old}) and len(new)==len({r['id'] for r in new}),'Duplicate inventory actor'
  before,after={r['id']:r for r in old},{r['id']:r for r in new}
  for key in sorted(set(before)|set(after)):
   a,b=before.get(key),after.get(key)
   if a==b:continue
   for row in [a,b]:
    if row is not None:assert disjoint(row['completeWorldXZBounds'],region),'Changed actor/terrain touches frozen current region'
   changes.append(dict(kind=kind,id=key,before=a,after=b))
 assert changes,'Manifest additions/removals lack complete inventory evidence'
 return dict(verifiedDisjointGlobalManifestRebind=True,oldManifestSHA256=old_manifest_sha,currentManifestSHA256=new_manifest_sha,completeFrozenRegionWorldXZBounds=region,changedCompleteInventory=changes,allFrozenNumericAndSourceInputHashesUnchanged=True,numericAcceptanceRecomputed=False,installationApproved=False)
