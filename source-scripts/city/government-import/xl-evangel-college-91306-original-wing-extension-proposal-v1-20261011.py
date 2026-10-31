"""Freeze a complete named136 original wing-extension proposal, no approval."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from evangel_college_original_wing_extension_identity_20261011 import proposal,UID
BASE=ROOT/'docs/astra-city/government-import';RAW=BASE/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011';PRIMARY=BASE/'government-xl-evangel-college-91306-primary-relations-v1-20261011';CONTEXT=BASE/'government-xl-evangel-college-91306-western-original-patches-context-v1-20261011';OWNER=BASE/'government-xl-evangel-college-91306-observed-owner-packet-verification-v1-20261011'
BATCH='government-xl-evangel-college-91306-original-wing-extension-proposal-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [RAW,PRIMARY,OWNER]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for pin in r['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
   refs.extend(p for p in folder.rglob('*')if p.is_file())
 for pin in read(CONTEXT/'provenance.json')['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 refs.extend(p for p in CONTEXT.rglob('*')if p.is_file())
 row=read(RAW/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];world=decode_original_world_triangles(asset.read_bytes());out=proposal(read(RAW/'identity.json'),row,world,read(RAW/'complete-current-forms.json.gz')['rows'],read(PRIMARY/'exact-current-one-primary.json'),read(CONTEXT/'diagnostic.json.gz'))
 packet=BASE/'government-xl-evangel-college-91306-official-campus-packet-v1-20261011';out['architecturalInterpretationPrimaryRefs']=[ref(packet/p)for p in ['official-page-0.html','official-page-1.html','official-page-2.html','actual-owner-campus-image-3.png']]
 assert out['proposalSpatialGuardsSatisfied'];save(DOC/'diagnostic.json.gz',out)
 refs.extend([asset,HERE/'evangel_college_original_wing_extension_identity_20261011.py',HERE/'test_evangel_college_original_wing_extension_identity_20261011.py',HERE/'king_cheung_complete_ancillary_proposal_20261011.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
 s=importlib.util.spec_from_file_location('evangel_wing_extension_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'named136-original-school-wing-extension-source-only-proposal',refs,dict(uids=[UID],completeOriginalFaces=13960,namedOriginalExtensionFaces=136,ordinaryExtentFaces=13824,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps({k:out[k]for k in ['fullSourceSpatialChecks','ordinaryExtentFaceCount','proposalSpatialGuardsSatisfied']}),flush=True)
if __name__=='__main__':main()
