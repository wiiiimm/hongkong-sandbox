"""One unchanged original Block17 opening association, not physical contact/root."""
from pathlib import Path
import json,numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_original_lower_opening_mounts_v3_20261011 import binding,verify
B=ROOT/'docs/astra-city/government-import';GRAPH=B/'government-xl-parkview-block17-complete-original-support-graph-v1-20261011';ROUTE=B/'government-xl-parkview-block17-bounded-eligible-native-route-v1-20261011';BATCH='government-xl-parkview-block17-original-lower-opening-association-v3-20261011';DOC=B/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');assert g['unreachedBodies']==[62];p=ROOT/g['source']['path'];assert ref(p)==g['source'];t=decode_original_world_triangles(p.read_bytes());assert digest(t.tobytes())==g['completeOriginalWorldSHA256'];cs=g['completeSourceEdgeBodyFaces'];host=sorted(f for b in map(int,g['completeConditionalParents'])for f in cs[b]);body=cs[62];expected=binding(t,body,host);proof=None;failure=None
 try:proof=verify(t,body,host,expected_binding=expected)
 except AssertionError as error:failure=str(error)
 refs=[ref(x)for x in [Path(__file__),p,GRAPH/'diagnostic.json.gz',ROUTE/'diagnostic.json.gz',HERE/'complete_original_lower_opening_mounts_v3_20261011.py',HERE/'complete_original_lower_opening_mounts_v2_20261011.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'test_complete_original_lower_opening_mounts_v3_20261011.py']]
 result=dict(uids=g['uids'],completeOriginalFaces=len(t),completeOriginalWorldSHA256=digest(t.tobytes()),originalBody=62,originalBodyFaces=body,completeReachableOriginalHostFaces=host,exactSourceBodyHostBinding=expected,completeOriginalLowerOpeningV3Proof=proof,guardFailure=failure,associationProved=proof is not None,exactOriginalContactStillAbsent=True,structuralRootCredit=False,structuralBridgeCredit=False,closedSolidCertified=False,architecturalFunctionUnresolved=True,originalDegenerateFacetsPreserved=g['completeOriginalDegenerateFaces'],originalDegenerateCoordinates=t[g['completeOriginalDegenerateFaces']].tolist(),degenerateFacesProvideNoSupportOrBandCredit=True,sourceOnly=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(associationProved=result['associationProved'],guardFailure=failure,proofKeys=list(proof)if proof else[])),flush=True)
if __name__=='__main__':main()
