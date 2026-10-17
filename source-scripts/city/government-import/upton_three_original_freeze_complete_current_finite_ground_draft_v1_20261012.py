"""UNEXECUTED immutable diagnostic freezer, preserving all finite/body failures."""
import argparse,json
from pathlib import Path
from fractions import Fraction as F
from run import ROOT,HERE,read,save,connect,reservations
from upton_three_original_complete_current_finite_ground_draft_v1_20261012 import DOC,LOCAL,BATCH,CAP,RUNTIME,UIDS,MANIFEST_SHA,state,native,ref,module

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);a=p.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists()
 result=read(DOC/'diagnostic.json.gz');scope=read(CAP/'capture-scope.json');capture=read(CAP/'result.json');before=read(CAP/'protected-state-before.json');selections=read(CAP/'selection.json.gz')['rows'];native_before=read(CAP/'native-source-state-before.json')['rows']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(capture['jobId'],)).fetchone()==('complete',capture)
 assert result['uids']==UIDS and result['sourceOnly']and result['ordinaryThresholdM']=='-1/2'and result['completeFaces']==13704 and result['genuineBodyObligations']==749 and result['zeroFaceObligations']==17 and result['all23ProperSourceCrossingsRetained']
 for key in ['physicalAccepted','installationApproved','foreignHoldsDischarged','gradeRootProved','wholeEdgeCapPathsQualified']:assert result[key]is False
 assert result['sourceGeometryChanges']==result['terrainGeometryChanges']==0 and result['currentNativeCount']==6649 and result['currentManifest']==scope['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json') and result['currentManifest']['sha256']==MANIFEST_SHA
 counts=[11657,1655,392];bodies=[737,8,4];zeros=[16,1,0]
 for actor,count,body,zero in zip(result['actors'],counts,bodies,zeros):
  assert actor['uid']==UIDS[counts.index(count)];top=actor['originalBodyCensus'];assert len(top['completeOriginalFaceIds'])==count and len(top['sharedEdgeConnectedComponents'])==body and len(top['exactNonrenderingOriginalFaces'])==zero
  assert len(actor['completeOriginalPlaneAttribution'])==count and sum(r['exactPlaneClass']=='zero'for r in actor['completeOriginalPlaneAttribution'])==zero
  bindings=actor['allFourStreamBindings'];assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'}
  assert {x['wholeWorldSHA256']for x in bindings.values()}==set(actor['distinctCompleteFiniteProofs'])
  for x in bindings.values():assert x['completeFaces']==count and x['wholeGroundSHA256']==actor['completeGroundSHA256']and x['proofTupleSHA256']
  for h,proof in actor['distinctCompleteFiniteProofs'].items():
   rows=proof['allWholeFacetProofs'];assert proof['completeFaces']==len(rows)==count and [r['face']for r in rows]==list(range(count));assert proof['ordinaryFailingFaces']==[r['face']for r in rows if not r['ordinaryFiniteProved']]
   for row in rows:
    assert row['ordinaryFiniteProved']==bool(row['completeProjectionCovered']and F(row['exactLowerM'])>=-F(1,2));assert row['strictPositiveFiniteProved']==bool(row['completeProjectionCovered']and F(row['exactLowerM'])>0)
  assert not actor['sourceBodyRolesQualified']and not actor['gradeRootProved']and not actor['wholeEdgeCapPathsQualified']
 for e in capture['evidenceRefs']+result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 for path,h in scope['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==native_before
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','upton_finite_freezer_closure');paths=set();walker.local_imports(Path(__file__),paths)
 walker.declared_refs(result,paths);paths.add(DOC/'diagnostic.json.gz');paths.update(CAP/n for n in ['result.json','capture-scope.json','protected-state-before.json','native-source-state-before.json','selection.json.gz']);paths.add(RUNTIME)
 note='Complete unchanged13704 original faces/all4worlds/749 genuine body obligations/17 zero source facets against per-actor complete actual drawn ground. Fixed ordinary>=-.5m, exact finite column min/max refinement and strict clearance separate. Preserve all23 proper original crossings, every negative/raw plane/body result and all foreign/runtime/native/support holds. Contact at a point or within a wall is no exposed whole-edge/cap/grade/root proof; no foundation intent inferred. No source/pose/terrain changes, no native reapproval or installation.'
 (DOC/'REVIEW.md').write_text(note+'\n');paths.add(DOC/'REVIEW.md')
 frozen=walker.F.freeze(BATCH,'upton-three-original-complete-finite-current-ground-no-root-credit',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,currentNativeCount=6649,completeFaces=13704,genuineBodyObligations=749,zeroFaceObligations=17,all23ProperOriginalCrossingsPreserved=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(frozen['jobId'],)).fetchone()==('complete',frozen)
 for e in frozen['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selections),default=str))==native_before and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease)
 print(json.dumps(dict(jobId=frozen['jobId'],allRefs=len(frozen['evidenceRefs']),sourceOnly=True,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
