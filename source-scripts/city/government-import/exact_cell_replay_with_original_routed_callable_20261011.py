"""Exact cell replay using the captured original routed callable, never proxy.

The existing exact-cell numerical function is reused unchanged. This only makes
its original routed dependency explicit when a named pipeline proxy is active.
"""
from pathlib import Path
from run import ROOT,HERE,digest
from routed_original_cell_identity import verify_files as ORIGINAL_ROUTED_VERIFY
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import numpy as np
ORIGINAL_ROUTED_PATH=HERE/'routed_original_cell_identity.py'
ORIGINAL_ROUTED_SHA=digest(ORIGINAL_ROUTED_PATH.read_bytes())
def require_original_callable(callback):
 assert callback is ORIGINAL_ROUTED_VERIFY,'Only the captured original routed verifier is permitted; proxy/self recursion is rejected'
 assert Path(callback.__code__.co_filename).resolve()==ORIGINAL_ROUTED_PATH.resolve()
 assert digest(ORIGINAL_ROUTED_PATH.read_bytes())==ORIGINAL_ROUTED_SHA
 return True
def verify_files(row,context,local,*,routed_verifier=ORIGINAL_ROUTED_VERIFY):
 require_original_callable(routed_verifier)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
 current=routed_verifier(row,context,local)
 tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']==row['native']['model']['triangles']
 binding={'uid':row['uid'],'sourceSHA256':digest(raw),'decodedWorldTrianglesSHA256':digest(tri.astype('<f8').tobytes())}
 result=apply_exact_cell(current,tri,expected_binding=binding,current_binding=binding)
 require_original_callable(routed_verifier);assert (ROOT/row['candidate']['path']).read_bytes()==raw
 return result
