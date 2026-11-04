"""Four exact original standing skins, current ground proposal only.
Complete source paths and ordinary rim failures are preserved, no root transfer.
"""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_original_wing_extension_identity_20261011 import UID,SOURCE_SHA
from evangel_college_named_standing_grade_skin_20261011 import verify,sha,IDS
B=ROOT/'docs/astra-city/government-import';Q=B/'government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011';PHYSICAL=B/'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
BATCH='government-xl-evangel-college-91306-four-standing-current-grade-skin-proposal-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [Q,PHYSICAL]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 q=read(Q/'diagnostic.json.gz');runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path);refs.append(runtime_path);assert len(runtime['rows'])==1 and runtime['rows'][0]['uid']==UID
 ground=np.asarray(runtime['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert sha(ground)==q['completeActualGroundSHA256']and q['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==q['currentManifestSHA256']==runtime['inputHashes']['3d-viewer/city/data/manifest.json']
 for path,h in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 rows=[];cache={}
 for row in q['rows']:
  output=[]
  for component in sorted(IDS):
   x=next(x for x in row['completeFiveStandingDispositions']if x['originalComponent']==component);assert x['completeOriginalFaces']==IDS[component]and x['allOriginalFacetsOrdinaryClear']and x['completeOrdinaryFootingVerbatim']['passed']is False
   part=np.asarray(x['completeOriginalGeometry'],dtype='<f8');binding=dict(completePartSHA256=sha(part),completeGroundSHA256=sha(ground));key=(component,sha(part))
   if key not in cache:cache[key]=verify(part,ground,component=component,source_face_ids=IDS[component],expected_binding=binding,current_binding=binding)
   output.append(dict(originalComponent=component,completeNamedStandingSkinProof=cache[key],rawOrdinaryWholeFootingVerbatim=x['completeOrdinaryFootingVerbatim'],sourceRoleInterpretationProposed=True,independentSourceStandingSkinRootAccepted=False))
  rows.append(dict(arithmetic=row['arithmetic'],completeWorldSHA256=row['completeWorldSHA256'],completeFourStandingSkinProofs=output));print(json.dumps(dict(arithmetic=row['arithmetic'],completeStandingSkins=4)),flush=True)
 save(DOC/'proposal.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeActualGroundSHA256=sha(ground),currentManifestSHA256=digest(before),allPrior226DispositionsAndRawFootingFailuresRetained=True,newSourceGeometry=False,newTerrainGeometry=False,loadBearingClaim=False,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for path,h in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 refs.extend(HERE/n for n in ['evangel_college_named_standing_grade_skin_20261011.py','test_evangel_college_named_standing_grade_skin_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py']);refs.append(DOC/'proposal.json.gz')
 spec=importlib.util.spec_from_file_location('evangel_standing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.freeze(BATCH,'four-named-original-standing-source-skin-genuine-current-grade-and-clear-upper-perimeters-proposal',refs,dict(uids=[UID],currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-standing-skins-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
