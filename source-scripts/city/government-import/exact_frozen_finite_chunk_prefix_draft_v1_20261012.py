"""Check complete immutable historical row dictionaries against final proof prefixes."""
import hashlib
from exact_frozen_finite_chunk_hydration_draft_v1_20261012 import hydrate

def verify_prefixes(historical, final_proofs):
 for (world_sha,ground_sha),rows in historical.items():
  key=hashlib.sha256((world_sha+ground_sha).encode()).hexdigest();assert key in final_proofs
  actual=final_proofs[key]['allWholeFacetProofs'];assert actual[:len(rows)]==rows,'Historical proof payload changed in final output'
 return {world:len(rows)for(world,ground),rows in historical.items()}
