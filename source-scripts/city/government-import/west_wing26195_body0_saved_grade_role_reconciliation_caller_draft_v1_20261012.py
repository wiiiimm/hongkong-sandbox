"""DRAFT exact saved-proof caller. ROOT review required before any invocation."""
import argparse,json
from pathlib import Path
from run import ROOT,read,save,digest,connect
import west_wing26195_body0_saved_facet_role_partition_draft_v1_20261012 as P
import west_wing26195_body0_source_bound_grade_role_draft_v1_20261012 as H
BASE=P.BASE;PROPOSAL=BASE/'government-xl-west-wing26195-body0-source-bound-grade-role-proposal-v1-20261012'
RECEIPTS={
 'finite':('a0f08846d525ebbcde49b6b62151d031fd73a41f4633c5455fcaeac4d06ffcac','0a4485ffe26c1242a91fb5e2040f7a886db775e459790f7e5f0baa8328e67449'),
 'grade':('74b5215e3f2271cdc04a5fc213835c930e22f32393fedea9a5b45407947e92e6','1ac8072a8f44e9124089ee6dfd2e1ef9c4b77cf906cf3b2d2e9f3494bc02ca0a'),
 'corridor':('67805072f17832400bfe15830c39a5413d7850b03f8e797de4b93b0afae7099b','d761a5e5336cb58a9535c7e1e0a4a58021d6f3588eeefa42e2d7f9ba86623209'),
 'seed153':('c074d4029e2a72d26e45c187c524c18f20135c8e038afac5de992848293d164b','e75adce0044c077f63fde26447fd6fbc820551c9a038541276eb6c5db6acc077'),
 'visual':('38eaf53948efac4fa3ee79a598376907e3226e60b45c57a5e1180da31903d42c','9dc688df668407492c2d2417db3f34e556bda10a26e3ad6185e946c4b7645d3b')}
def main():
 a=argparse.ArgumentParser();a.add_argument('--interpretation');a=a.parse_args();data=[];refs=[]
 # No new grade/contact/terrain arithmetic. Exact Neon queries remain read-only.
 for name,(job,sha)in RECEIPTS.items():
  path=BASE/P.BATCHES[name]/'result.json';assert digest(path.read_bytes())==sha;r=read(path);assert r['jobId']==job and r['sourceOnly']and not r['physicalAccepted']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
  d,ref=P.load(name);data.append(d);refs.append(ref)
 import west_wing26195_current_typed_visual_surface_roles_draft_v1_20261012 as T
 _,scope,*_=T.inputs();assert T.ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
 for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 before=read(T.M.D.S.G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(T.M.D.S.G.P.F.state(before['uids']),default=str))==before['rows']
 fixture=read(T.M.VISUAL/'context.json');source=fixture['source'];assert digest((ROOT/source['path']).read_bytes())==H.SOURCE
 captured=read(T.M.D.S.G.P.F.CAP/'actual-render-geometry.json.gz');actual=next(x for x in captured['rows']if x['uid']==H.UID);assert actual['sourceSHA256']==H.SOURCE and actual['loadedGroupScale']==[1,1,1] and actual['sourceGeometryChanges']==0 and captured['startEndAllInputsVerified']
 original=read(T.M.D.S.G.P.F.CAP/'original-full-source-root-context.json.gz');assert original['uid']==H.UID and original['sourceGeometryChanges']==0 and original['completeOriginalWorldSHA256']==data[0]['allFourStreamBindings']['original']['wholeWorldSHA256']
 identity=dict(uid=H.UID,sourceSHA256=H.SOURCE,sourcePreserved=True,unitScale=actual['loadedGroupScale'][0],poseChanges=0,actualGroupMatrixWorldSHA256=H.sha(actual['loadedGroupMatrixWorldFloat64']),actualRootTranslation=actual['cataloguePreparedRootTranslation'],rawInstalledEntrySHA256=H.sha(actual['rawInstalledEntry']),completeOriginalWorldSHA256=original['completeOriginalWorldSHA256'],completeCapturedGroundSHA256=scope['completeActualGroundSHA256'])
 contracts=read(BASE/'government-xl-west-wing26195-body0-saved-facet-role-reconciliation-proposal-v1-20261012/existing-carrier-contract-refs.json')
 for e in contracts['codeRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 interpretation=read(Path(a.interpretation))if a.interpretation else None
 if interpretation:
  for e in interpretation['sourceViewRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 result=H.verify(*data,identity,contracts,expected_binding=H.binding(*data,identity,contracts),interpretation=interpretation)
 # Canonical supervisor/validation/freezer to be added after ROOT source review.
 print(json.dumps(dict(sourceOnly=True,body0RoleRootCandidateReady=result['body0RoleRootCandidateReady'],all42GradeRoutesComplete=result['all42GradeRoutesComplete'],wholeSourcePhysicalAccepted=False,remainingSourceInterpretation=result['remainingSourceInterpretation'])))
if __name__=='__main__':main()
