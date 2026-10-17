"""Source/current role proposal only; no full model acceptance or publication."""
import importlib.util,json,subprocess,sys,uuid
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import source_proposal_pin_path
from evangel_college_named_lower_source_skin_v3_20261011 import verify as lower,sha,GROUND_SHA
from evangel_college_named_two_upper_strips_v2_20261011 import verify as strips
B=ROOT/'docs/astra-city/government-import'
NAMES={'source':'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011','finite':'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011','grade':'government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011','graph':'government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011','q':'government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011','physical':'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'}
BATCH='government-xl-evangel-college-91306-remaining-original-lower-skin-and-two-strip-proposal-v3-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
TEST_EVIDENCE=B/'government-xl-evangel-college-91306-remaining-role-code-validation-v3-20261011'
def row(d,mode):
 r=[r for r in d['rows']if r['arithmetic']==mode];assert len(r)==1;return r[0]
def owned():
 assert reservations.owns(read(LEASE))and not DOC.exists();refs=[Path(__file__)];folders={k:B/n for k,n in NAMES.items()}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for k,p in folders.items():
   receipt=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(p/'result.json')
   for pin in receipt['evidenceRefs']:
    f=source_proposal_pin_path(pin)if k in {'source','graph'}else ROOT/pin['path'];assert digest(f.read_bytes())==pin['sha256'];refs.append(f)
 source=read(folders['source']/'complete-four-stream-ground-inputs.json.gz');finite=read(folders['finite']/'diagnostic.json.gz');grade=read(folders['grade']/'diagnostic.json.gz');graph=read(folders['graph']/'diagnostic.json.gz');q=read(folders['q']/'diagnostic.json.gz');physical=read(folders['physical']/'diagnostic.json.gz')
 runtime_path=HERE/'local'/folders['physical'].name/'runtime-geometry.json.gz';runtime=read(runtime_path);refs.append(runtime_path);assert len(runtime['rows'])==1 and runtime['rows'][0]['uid']==UID;ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert sha(ground)==GROUND_SHA==q['completeActualGroundSHA256']and source['uid']==UID and source['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==q['currentManifestSHA256']==grade['completeCurrentManifestSHA256']==physical['currentManifest']['sha256']
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 rows=[]
 for mode,stream in source['completeWorldStreams'].items():
  w=np.asarray(stream['completeWorldTriangles'],dtype='<f8');gr=row(graph,mode);qr=row(q,mode);parts=gr['completeOriginalTopology']['sharedEdgeConnectedComponents'];assert sha(w)==gr['completeWorldSHA256']==qr['completeWorldSHA256']
  rows.append(dict(arithmetic=mode,completeWorldSHA256=sha(w),namedLowerSourceSkinProposal=lower(world=w,ground=ground,finite_row=row(finite,mode),grade_row=row(grade,mode),parts=parts),namedTwoUpperStripProposal=strips(world=w,qualification_row=qr,parts=parts,qualified_host_face_ids=qr['completeConditionalHostFaceIds']),qualifiedHostsStillRequireWholeComposer=True));print(json.dumps(dict(arithmetic=mode)),flush=True)
 save(DOC/'proposal.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeActualGroundSHA256=GROUND_SHA,currentManifestSHA256=digest(before),raw132FiniteFailuresAndAll226DispositionsRetained=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 test=read(TEST_EVIDENCE/'validation.json');assert test['passed']is True and test['tests']==27 and test['productionReplayPerformedByTests']is False
 assert digest((TEST_EVIDENCE/'actual-adverse-tests.log').read_bytes())==test['testLogSHA256']
 for p,h in test['codeHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs.extend([TEST_EVIDENCE/'validation.json',TEST_EVIDENCE/'actual-adverse-tests.log'])
 refs.append(DOC/'proposal.json.gz');refs.extend(HERE/n for n in ['evangel_college_named_lower_source_skin_v3_20261011.py','evangel_college_named_two_upper_strips_v2_20261011.py','test_evangel_college_named_remaining_source_roles_v3_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py'])
 for n in ['government-xl-evangel-remaining-role-v2-tapered-wall-classification-failure-archive-20261011','government-xl-evangel-remaining-role-v1-schema-failure-archive-20261011','government-xl-evangel-college-91306-two-sloping-undersides-context-v1-20261011','government-xl-evangel-college-91306-two-upper-strip-context-v1-20261011','government-xl-evangel-college-91306-current-grade-v4-failure-archive-20261011']:refs.extend(p for p in (B/n).rglob('*')if p.is_file())
 assert reservations.owns(read(LEASE))and manifest.read_bytes()==before
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 s=importlib.util.spec_from_file_location('evangel_remaining_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'named-original-lower-skin-base-closure-and-two-three-backed-free-upper-strips-proposal',refs,dict(uids=[UID],currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-remaining-roles-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
