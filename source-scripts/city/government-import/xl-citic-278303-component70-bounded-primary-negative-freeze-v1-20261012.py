"""UNEXECUTED historical-source/primary-search negative freezer only.
No new download, source computation, distance rerun, live fence/approval or review
mutation. The prior seven interpretations and unidentified70 remain unchanged.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-citic-independent-branding-review-checkpoint-v1-20261011/result.json'
PRIOR_SHA='3033c4f26ed7bd5387e30e4e222e94ca477052c4afe6ce9dd58fbfeb0ed7b346';PRIOR_JOB='fa3347605ba645a6802ac345b6a914e9d8e4d5ead661338c14415070d30201cf'
PACKET=BASE/'government-xl-citic-component70-bounded-primary-search-v1-20261011'
UID='landsd/278303:0';SOURCE='284eaf0cf2337754e101689410df4336801dc20c96a4cedb4f745d8c6fb8eb3f'
EXPECTED=[('https://www.hfc.org.hk/filemanager/files/TFHK_20110525_ppt_item4.pdf','hfc-2011-signage-proposal.pdf',200,'5aaa8fc599a0798a14cebd4cbcd6de3cacf4e2d911c680842e71b86ff9c5af09'),('https://www.hfc.org.hk/filemanager/files/paper_no_hc_12_2011.pdf','hfc-2011-meeting-report.pdf',200,'885dfeb02bc52c072089622c97f1ec8f201c51092ec40fec0dd87a8f47a88379'),('https://www.citictower.com.hk/','owner-home.html',403,'832962035a86aed4af15b98270dd29dbb073481b504d73e864beb9d9290eb21e')]
BATCH='government-xl-citic-278303-component70-bounded-primary-negative-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def preflight():
 assert not DOC.exists();assert digest(PRIOR.read_bytes())==PRIOR_SHA;prior=read(PRIOR);assert prior['jobId']==PRIOR_JOB and prior['uids']==['landsd/232579:0',UID]and prior['proposedSignageComponents']==[34,29,39,36,35,33,40]and prior['unresolvedComponents']==[70]
 source_pins=[p for p in prior['evidenceRefs']if p['sha256']==SOURCE];assert len(source_pins)==1;source=ROOT/source_pins[0]['path'];assert digest(source.read_bytes())==SOURCE
 retrieval=read(PACKET/'retrieval.json');exports=read(PACKET/'actual-page-exports.json');assert retrieval['sourceOnly']and retrieval['currentAcceptance']is False and retrieval['installationApproved']is False and len(retrieval['rows'])==3
 for row,(url,name,status,sha)in zip(retrieval['rows'],EXPECTED):
  p=PACKET/name;assert row['url']==row['finalUrl']==url and row['status']==status and row['sha256']==sha and row['path']==str(p.relative_to(ROOT))and row['bytes']==len(p.read_bytes())and digest(p.read_bytes())==sha
 assert exports['rawPdfSHA256']==EXPECTED[0][3]and exports['sourceOnly']and exports['noPreciseRegistration']and [r['page']for r in exports['rows']]==list(range(1,12))
 for row in exports['rows']:
  p=ROOT/row['path'];assert p.parent==PACKET and row['width']==2400 and row['height']==1800 and digest(p.read_bytes())==row['sha256']
 refs=[Path(__file__),PRIOR,source]+[p for p in PACKET.iterdir()if p.is_file()]+[HERE/n for n in ['run.py','xl-popcorn-source-investigations-checkpoints-20261009.py','popcorn_original_ancillary_identity_20261009.py']]+[HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']]
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};return prior,retrieval,exports,refs,pins

def main():
 state=preflight()
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();claim=reservations.claim('citic-bounded-primary-negative-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 prior,retrieval,exports,refs,pins=state;lease=read(LEASE);assert lease['resources']==['building:'+UID]and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PRIOR_JOB,)).fetchone()==('complete',prior)
 save(DOC/'diagnostic.json',dict(uids=[UID],sourceSHA256=SOURCE,priorCompletedJob=PRIOR_JOB,priorResultFileSHA256=PRIOR_SHA,priorActorUIDsVerbatim=prior['uids'],priorSevenComponentsVerbatim=prior['proposedSignageComponents'],priorSevenInterpretationQualificationVerbatim=prior['qualification'],priorSevenVisualRoleAcceptedVerbatim=prior['visualRoleAccepted'],unresolvedOriginalComponent=70,completeOriginalComponentFaceIDs=list(range(14024,14036)),previousSourceBoundsVerbatim=[[745.9326171875,84.3281478881836,752.8671875],[747.4189453125,85.61315536499023,755.9501953125]],sourceBoundsNotRecomputed=True,rawRetrievalVerbatim=retrieval,actualExportProvenanceVerbatim=exports,inspectedPrimaryPages=[9,11],boundedSearchDisposition='Official2011 rooftop-sign proposal and meeting report do not uniquely identify original lower box70; owner403 preserved. No precise registration/as-built correspondence/function/mount/root claim.',newComponent70RoleEvidenceSupported=False,additionalEvidenceThatCouldChangeDisposition='A uniquely corresponding owner/architect/contractor side elevation, equipment detail or original photo at this exact unchanged source context.',historicalImmutableSourceAndPrimaryPacketOnly=True,previousRuntimeOrCurrentProofNotTransferred=True,unchangedHostDistanceTestsNotRerun=True,sourceEvidenceInterpretationUsedAI=True,physicalAccepted=False,currentAcceptance=False,modelReviewWrites=0,sourceGeometryChanges=0,terrainGeometryChanges=0,newlyInstalled=0))
 assert reservations.owns(lease)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(DOC/'diagnostic.json');s=importlib.util.spec_from_file_location('citic_primary_negative_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=m.freeze(BATCH,'bounded-primary-source-component70-still-unidentified-no-current-role-credit',refs,dict(uids=[UID],sourceSHA256=SOURCE,priorCompletedJob=PRIOR_JOB,sevenPriorComponentsPreserved=[34,29,39,36,35,33,40],unidentifiedComponents=[70],historicalSourceAndPrimaryPacketOnly=True,newComponent70RoleEvidenceSupported=False,currentAcceptance=False,physicalAccepted=False,modelReviewWrites=0,sourceEvidenceInterpretationUsedAI=True,newlyInstalled=0));print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
