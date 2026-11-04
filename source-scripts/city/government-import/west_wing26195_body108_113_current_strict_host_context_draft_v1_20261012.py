"""DRAFT JSON-only strict host context. No opening/body/support/identity acceptance."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_complete_current_body_contact_graph_draft_v1_20261012 as D
import west_wing26195_body108_113_strict_host_association_draft_v1_20261012 as H
BATCH='government-xl-west-wing26195-body108-113-current-strict-host-context-v1-20261012';DOC=D.S.G.P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=D.S.G.P.BASE/'government-xl-west-wing26195-body108-113-strict-host-association-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_body108_113_current_strict_host_context_draft_v1_20261012.py';HELPER=Path(H.__file__);TEST=HERE/'test_west_wing26195_body108_113_strict_host_association_draft_v1_20261012.py';ref=D.ref

def validation():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==14 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noActualSourceAssociationExecution'];assert v['codeRefs']==[ref(p)for p in [HELPER,TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];s=(ROOT/v['testLog']['path']).read_text();assert 'Ran 14 tests'in s and s.rstrip().endswith('OK');return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog'],ref(PROPOSAL/'METHOD.md')]
def inputs():
 _,scope,worlds,finite,old,corridor,sd=D.inputs();r=read(D.DOC/'result.json');assert r['jobId']=='9f0be819837f76962af45f7ea1035e45c0d6418191840b48f3536909c80c2568'and ref(D.DOC/'result.json')['sha256']=='587848c729c180031c4f64de2b2ce02c04835ecf3a0f094ac3f25c03037121fe'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 graph=read(D.DOC/'diagnostic.json.gz');assert graph['allFourStreamBindings']==finite['allFourStreamBindings'];assert set(finite['allFourStreamBindings'])=={'original','literal','explicitLeftF32','explicitBalancedF32'}and all(x['completeFaces']==46918 and x['wholeGroundSHA256']==D.S.G.P.F.GROUND_SHA for x in finite['allFourStreamBindings'].values());cs=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];assert len(cs)==118 and len(cs[108])==8 and len(cs[113])==2 and cs[108]==list(range(45369,45377))and cs[113]==[46081,46082];return r,scope,worlds,finite,graph

def calculate(world,key,finite,graph):
 cs=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];out={}
 for b,kind in [(108,'body108-minimum-edge-context'),(113,'body113-whole-two-face-surface-context')]:
  hosts=H.strict_hosts(world,cs[0],cs[b],records);hs=hosts['selectedWholeFiniteHostIDs'];assert len(hs)<=512,'Bounded host workload exceeded; preserve failure';association=H.associate(world,cs[b],hs,kind,expected_binding=H.binding(world,cs[b],hs));contacts=[x for x in graph['distinctCompleteBodyDiagnostics'][key]['allExactCrossBodyContacts']if b in x['originalBodyLabels']];out[str(b)]=dict(originalBodyLabel=b,currentArithmeticOriginalBodyLabelsAreProvenanceOnly=True,completeStrictHostSelection=hosts,associationContext=association,completeSavedActualCrossBodyContacts=contacts,allRawPointAndCrossingNegativesPreserved=True,typedAcceptanceRouteEstablished=False)
 return dict(wholeWorldSHA256=digest(world.tobytes()),bodies=out,all118BodyObligationsRemainUnqualified=True,body0GroundRoleRemainsConditional=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');args=p.parse_args();valid=validation();receipt,scope,worlds,finite,graph=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not args.owned:
  c=reservations.claim('westwing-two-body-host-context-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);walker=D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingtwohostclosure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)]+valid
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
  for e in codes:assert ref(ROOT/e['path'])==e
  before=read(D.S.G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(D.S.G.P.F.state(before['uids']),default=str))==before['rows']
 fence();results={}
 for mode,world in worlds.items():
  b=finite['allFourStreamBindings'][mode];assert digest(world.tobytes())==b['wholeWorldSHA256'];key=b['proofTupleSHA256']
  if key in results:continue
  fence();results[key]=calculate(world,key,finite,graph);save(LOCAL/('completed-'+mode+'.json.gz'),results[key]);fence();assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(world=mode,selectedHosts={b:len(r['completeStrictHostSelection']['selectedWholeFiniteHostIDs'])for b,r in results[key]['bodies'].items()},typedAcceptanceRouteEstablished=False)),flush=True)
 fence();save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,completeFaces=46918,completeOriginalBodies=118,completeGroundFaces=3240,all42OrdinaryFailuresAnd443StrictUncertifiedRetained=True,legacyDeliveryAnd15ReviewsUnchanged=True,allFourStreamBindings=finite['allFourStreamBindings'],currentManifest=scope['currentManifest'],distinctBodyAssociationContexts=results,unchangedOpeningV3TwoCycleRejectionPreserved=True,literalBody113PointOnlyNegativePreserved=True,allPrior17Plus24PlusSeed153PathsPreserved=True,noFiniteGradeCorridorOrContactCensusRerun=True,evidenceRefs=codes+[ref(D.DOC/'result.json'),ref(D.DOC/'diagnostic.json.gz'),ref(D.PROPOSAL/'next-unresolved-body-context.json.gz')]));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
