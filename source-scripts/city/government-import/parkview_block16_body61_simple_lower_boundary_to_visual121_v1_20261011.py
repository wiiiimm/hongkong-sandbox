"""DRAFT: body61 whole six-edge opening against original visual121 only.
Preserves four-edgev3 failure; no generic visual/structural hierarchy approval.
"""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_original_simple_lower_opening_mounts_v1_20261011 import binding,verify
B=ROOT/'docs/astra-city/government-import';GRAPH=B/'government-xl-parkview-block16-complete-original-support-graph-v1-20261011';OLD=B/'government-xl-parkview-block16-original-lower-opening-association-v3-20261011';DOC=B/'government-xl-parkview-block16-body61-simple-lower-boundary-to-visual121-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');old=read(OLD/'diagnostic.json.gz');assert g['existingCapStrictClear']is False and g['unreachedBodies']==[57,58,59,60,61,62,121]and old['conditionalSourceHostsRemainUngrounded']is True
 for d in [GRAPH,OLD]:
  receipt=read(d/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 failure=next(r for r in old['rows']if r['originalBody']==61);hostmount=next(r for r in old['rows']if r['originalBody']==121);assert failure['associationProved']is False and failure['guardFailure']and hostmount['associationProved']is True and hostmount['completeOriginalLowerOpeningV3Proof']['completeLowerOpeningAssociated']is True
 source=ROOT/g['source']['path'];assert ref(source)==g['source'];t=decode_original_world_triangles(source.read_bytes());assert digest(t.tobytes())==g['completeOriginalWorldSHA256']==old['completeOriginalWorldSHA256'];cs=g['completeSourceEdgeBodyFaces'];body=cs[61];host=cs[121];expected=binding(t,body,host);proof=None;guardfailure=None
 try:proof=verify(t,body,host,expected_binding=expected)
 except AssertionError as error:guardfailure=str(error)
 if proof is not None:assert len(proof['completeDirectedLowerOpening'])==6
 refs=[ref(p)for p in [Path(__file__),source,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',OLD/'diagnostic.json.gz',OLD/'result.json',HERE/'complete_original_simple_lower_opening_mounts_v1_20261011.py',HERE/'test_complete_original_simple_lower_opening_mounts_v1_20261011.py',HERE/'complete_original_lower_opening_mounts_v2_20261011.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 for r in refs:assert ref(ROOT/r['path'])==r
 out=dict(uids=['landsd/256319:0'],source=g['source'],completeOriginalWorldSHA256=g['completeOriginalWorldSHA256'],originalBody=61,originalHostBody=121,completeOriginalBodyFaces=body,completeOriginalHostFaces=host,exactSourceBodyHostBinding=expected,wholeSimpleMinimumBoundaryProof=proof,guardFailure=guardfailure,wholeBoundaryAssociated=bool(proof and proof['completeLowerOpeningAssociated']),originalV3FourEdgeFailureVerbatim=failure,host121OriginalV3MountVerbatim=hostmount,visualOnVisualSourceContextOnly=True,hostAnd117ConditionalHostsRemainUngrounded=True,sourceGroundRouteStillBlocked=True,existingCapStrictClear=False,allSevenVisualRolesRemainUnapproved=True,structuralRootCredit=False,structuralBridgeCredit=False,genericStructuralHierarchyCredit=False,closedSolidCertified=False,architecturalFunctionInferred=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',out);print(json.dumps(dict(wholeBoundaryAssociated=out['wholeBoundaryAssociated'],guardFailure=guardfailure,originalV3FailurePreserved=True,sourceOnly=True)),flush=True)
if __name__=='__main__':main()
