"""Freeze completed source views and ROOT descriptive interpretation only."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,save,connect
import citywalk134332_saved_failure_source_orientation_context_draft_v2_20261013 as C
import citywalk134332_current_ground_only_supervised_draft_v1_20261013 as G
import parkview_block17_freeze_current_source_evidence_20261011 as F
BATCH='government-xl-citywalk134332-saved-failure-source-orientation-context-v2-20261013'
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();c,d,components,labels,worlds,ground,g=C.inputs();before=G.inputs(a)
 x=read(C.OUT/'source-context.json');audit=read(C.P/'independent-source-profile-export-readback-v2.json');review=read(C.OUT/'ROOT-message-bounded-visual-interpretation-source-context-v1.json')
 assert x['sourceOnly']and not x['currentAcceptance']and not x['physicalAccepted']and not x['installationApproved'];assert x['completeSourceFaces']==41277 and x['completeOriginalBodies']==193 and len(x['allSourceGroundBindings'])==12 and len(x['orientationProfiles'])==3
 assert audit['allInputRefsVerified']==33 and audit['context']==C.ref(C.OUT/'source-context.json')and audit['all193ObligationsRetained'];assert review['reviewer']=='ROOT'and review['actualViewsInspectedByROOT']and not review['blanketBuriedExemption']and not review['gradeRootAccepted']and not review['physicalAccepted']and not review['installationApproved']
 from PIL import Image
 for v in x['outputs']:
  assert C.ref(ROOT/v['path'])=={'path':v['path'],'sha256':v['sha256']}
  with Image.open(ROOT/v['path'])as im:assert im.size==(1800,1500)
 for z in x['orientationProfiles'].values():assert len(z['belowMinusHalfFaceRecords'])==683 and len(z['coverageOnlyFaceIDs'])==1322
 receipt=read(ROOT/c['finiteResult']['path'])
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert C.ref(ROOT/e['path'])==e
 assert G.inputs(a)==before
 if a.preflight_only:print(json.dumps(dict(preflightPassed=True,noWorker=True,sourceOnly=True,views=3,inputRefs=33,currentUIDs=len(before['currentState']['uids']),protectedRows=before['currentState']['observedProtectedReviewRecords'])));return
 assert not(C.OUT/'result.json').exists();save(C.OUT/'protected-current-state-for-source-context-freeze.json',before)
 paths=set();F.local_imports(Path(__file__),paths)
 for folder in [C.OUT,C.P]:paths.update(t for t in folder.rglob('*')if t.is_file())
 for obj in [x,audit,review,c,before]:F.declared_refs(obj,paths)
 paths.add(ROOT/c['finiteResult']['path']);paths.add(ROOT/c['finiteDiagnostic']['path']);assert G.inputs(a)==before
 result=F.F.freeze(BATCH,'saved-original-source-orientation-ROOT-descriptive-context-no-acceptance',sorted(paths),dict(uids=['landsd/134332:0'],sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,completeSourceFaces=41277,originalBodies=193,belowBoundFacetsPerTuple=683,coverageOnlyPerTuple=1322,currentNativeCount=6650,currentManifest=before['currentState']['currentManifest'],sourceContext=C.ref(C.OUT/'source-context.json'),boundedROOTVisualInterpretation=C.ref(C.OUT/'ROOT-message-bounded-visual-interpretation-source-context-v1.json'),noFiniteContactSourceOrTerrainReplay=True,all193ObligationsRetained=True,blanketBuriedExemption=False))
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert C.ref(ROOT/e['path'])==e
 assert G.inputs(a)==before
 print(json.dumps(dict(jobId=result['jobId'],resultSHA256=C.ref(C.OUT/'result.json')['sha256'],allLiteralRefs=len(result['evidenceRefs']),exactNeonVerified=True,sourceOnly=True,currentAcceptance=False,sourceContextLeaseReleasedByExistingHelper=True)),flush=True)
if __name__=='__main__':main()
