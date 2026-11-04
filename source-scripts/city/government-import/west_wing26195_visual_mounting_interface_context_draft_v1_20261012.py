"""DRAFT JSON-only strict host context. No opening/body/support/identity acceptance."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_complete_current_body_contact_graph_draft_v1_20261012 as D
import west_wing26195_visual_mounting_interface_draft_v1_20261012 as H
import west_wing26195_body108_113_current_strict_host_context_draft_v1_20261012 as OLD
BATCH='government-xl-west-wing26195-body108-113-visual-mounting-interface-context-v1-20261012';DOC=D.S.G.P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=D.S.G.P.BASE/'government-xl-west-wing26195-body108-113-visual-mounting-interface-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_visual_mounting_interface_context_draft_v1_20261012.py';HELPER=Path(H.__file__);TEST=HERE/'test_west_wing26195_visual_mounting_interface_draft_v1_20261012.py';ref=D.ref;VISUAL=D.S.G.P.BASE/'government-xl-west-wing26195-body108-113-original-host-visual-context-v1-20261012'

def validation():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==12 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noActualSourceAssociationExecution'];assert v['codeRefs']==[ref(p)for p in [HELPER,TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];s=(ROOT/v['testLog']['path']).read_text();assert 'Ran 12 tests'in s and s.rstrip().endswith('OK');return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog'],ref(PROPOSAL/'METHOD.md')]
def inputs():
 r,scope,worlds,finite,graph=OLD.inputs();receipt=read(OLD.DOC/'result.json');assert receipt['jobId']=='91a894f8cd279721fa13fa5dfceb667a9a2c87aed789ff66bb126257ac1f0863'and ref(OLD.DOC/'result.json')['sha256']=='50a57d7e5512c92ef45c024401fab010bb09554f79788a4313372a3a53cc3682'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 previous=read(OLD.DOC/'diagnostic.json.gz');assert previous['allFourStreamBindings']==finite['allFourStreamBindings'];visual=read(VISUAL/'context.json');assert visual['sourceOnly']and visual['completeOriginalFaces']==46918 and visual['completeOriginalBodies']==118 and len(visual['outputs'])==7 and not visual['architectureRoleAccepted'];observed=read(VISUAL/'actual-export-readback-and-observations.json');assert observed['allSevenActuallyViewed']and observed['actualDimensionAndSHAReadback']
 for e in visual['evidenceRefs']+visual['outputs']:
  assert ref(ROOT/e['path'])=={k:e[k]for k in ['path','sha256']}
 return receipt,scope,worlds,finite,previous

def calculate(world,key,finite,previous):
 cs=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];old=previous['distinctBodyAssociationContexts'][key]['bodies'];assert cs[108]==list(range(45369,45377))and cs[113]==[46081,46082];out={}
 for body in [108,113]:out[str(body)]=H.diagnose(world,cs[body],cs[0],records,old[str(body)]['associationContext'],expected_binding=H.binding(world,cs[body],cs[0]))
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
  fence();results[key]=calculate(world,key,finite,graph);save(LOCAL/('completed-'+mode+'.json.gz'),results[key]);fence();assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(world=mode,body113WholeBandBoundaryEdges=results[key]['bodies']['113']['wholeBandAssociatedBoundaryEdgeIndices'],typedAcceptanceRouteEstablished=False)),flush=True)
 fence();save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,completeFaces=46918,completeOriginalBodies=118,completeGroundFaces=3240,all42OrdinaryFailuresAnd443StrictUncertifiedRetained=True,legacyDeliveryAnd15ReviewsUnchanged=True,allFourStreamBindings=finite['allFourStreamBindings'],currentManifest=scope['currentManifest'],distinctBodyAssociationContexts=results,unchangedOpeningV3TwoCycleRejectionPreserved=True,literalBody113PointOnlyNegativePreserved=True,allPrior17Plus24PlusSeed153PathsPreserved=True,noFiniteGradeCorridorOrContactCensusRerun=True,evidenceRefs=codes+[ref(D.DOC/'result.json'),ref(D.DOC/'diagnostic.json.gz'),ref(D.PROPOSAL/'next-unresolved-body-context.json.gz'),ref(OLD.DOC/'result.json'),ref(OLD.DOC/'diagnostic.json.gz'),ref(VISUAL/'context.json'),ref(VISUAL/'actual-export-readback-and-observations.json')]+[{k:e[k]for k in ['path','sha256']}for e in read(VISUAL/'context.json')['outputs']]));subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
