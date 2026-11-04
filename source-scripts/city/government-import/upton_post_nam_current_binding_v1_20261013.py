"""Named post-Nam current binding; no numeric/source/current acceptance transfer."""
from pathlib import Path
import hashlib
from actual_native_bounds_baseline_rebind_20261011 import validate_unchanged_actor
OLD='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
DELTA='landsd/79099:0'
def manifest_delta(old,current,new_url):
 assert old['officialModelCatalogues']+[new_url]==current['officialModelCatalogues']
 assert {k:v for k,v in old.items()if k!='officialModelCatalogues'}=={k:v for k,v in current.items()if k!='officialModelCatalogues'},'Only named catalogue append is permitted'
 return True
def census(old,current):
 assert len(old)==len(set(old))==6649 and len(current)==len(set(current))==6650
 assert set(current)-set(old)=={DELTA} and set(old)<=set(current)
 return True
def historical_ref(q,root,old_manifest):
 original=Path(root)/q['path'];actual=original
 if q['path']=='3d-viewer/city/data/manifest.json' and q['sha256']==OLD:actual=Path(old_manifest)
 assert hashlib.sha256(actual.read_bytes()).hexdigest()==q['sha256'],q
 return actual

def actor_binding(prior,actual,entry,form,source_ref,source_sha):
 return validate_unchanged_actor(prior,actual,entry,form,source_ref,source_sha)
