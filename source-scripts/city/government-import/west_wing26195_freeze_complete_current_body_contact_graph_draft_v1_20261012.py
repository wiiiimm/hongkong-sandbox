"""DRAFT full-body contact evidence freezer; never acceptance/backfill."""
import argparse,json,itertools
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations,digest
import west_wing26195_complete_current_body_contact_graph_draft_v1_20261012 as D

def canon(v):return json.loads(json.dumps(v))
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);args=p.parse_args();valid=D.validation();lease=read(Path(args.lease_file));assert reservations.owns(lease);receipt,scope,worlds,finite,old,corridor,seed=D.inputs();d=read(D.DOC/'diagnostic.json.gz');cs=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];assert d['completeFaces']==46918 and d['completeOriginalBodies']==118 and d['completeGroundFaces']==3240 and d['sourceOnly']and d['all42OrdinaryFailuresAnd443StrictUncertifiedRetained']and d['noFiniteOrGradeOrCorridorArithmeticRerun']and d['legacyDeliveryAnd15ReviewsUnchanged']
 assert not any(d[k]for k in ['physicalAccepted','bodySupportAccepted','gradeRootAccepted','installationApproved','sourceGeometryChanges','terrainGeometryChanges']);assert d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==finite['allFourStreamBindings']and set(d['distinctCompleteBodyDiagnostics'])=={v['proofTupleSHA256']for v in d['allFourStreamBindings'].values()}
 assert d['prior17Plus24PlusSeed153DiagnosticsPreserved']==[D.ref(D.S.G.P.DOC/'diagnostic.json.gz'),D.ref(D.S.G.DOC/'diagnostic.json.gz'),D.ref(D.S.DOC/'diagnostic.json.gz')]
 allchunks=set()
 for name,world in worlds.items():
  binding=d['allFourStreamBindings'][name];assert digest(world.tobytes())==binding['wholeWorldSHA256'];key=binding['proofTupleSHA256'];r=d['distinctCompleteBodyDiagnostics'][key];pairlist,labels=D.candidates(world,cs);assert r['wholeWorldSHA256']==binding['wholeWorldSHA256']and r['completeOriginalBodyFaces']==cs and r['completeClosed3DAABBCandidatePairs']==len(pairlist)<=D.MAX_PAIRS and r['completeCandidatePairListSHA256']==digest(json.dumps(pairlist,separators=(',',':')).encode());assert r['all118BodySupportRolesRemainUnqualified']and r['mainBody0GroundRoleRemainsConditional']and r['currentArithmeticOriginalBodyLabelsAreProvenanceOnly']
  chunkrows=[];seenpairs=[];codecontract=None
  for start in range(0,len(pairlist),D.CHUNK):
   end=min(start+D.CHUNK,len(pairlist));path=D.LOCAL/'chunks'/key/f'{start:06d}-{end:06d}.json.gz';chunk=read(path);c=chunk['contract'];assert c['proofTupleSHA256']==key and c['wholeWorldSHA256']==binding['wholeWorldSHA256']and c['completeFaces']==46918 and c['completeOriginalBodies']==118 and c['completeCandidatePairs']==len(pairlist)and c['candidatePairListSHA256']==r['completeCandidatePairListSHA256']and c['firstPair']==start and c['exclusiveLastPair']==end
   for e in c['codeRefs']:assert D.ref(ROOT/e['path'])==e
   if codecontract is None:codecontract=c['codeRefs']
   assert c['codeRefs']==codecontract and D.ref(Path(D.__file__))in codecontract and D.ref(Path(__file__))in codecontract
   assert chunk['exactCandidatePairIDs']==[list(x)for x in pairlist[start:end]];seenpairs+=chunk['exactCandidatePairIDs'];chunkrows+=chunk['allFiniteContacts'];allchunks.add(path)
  assert seenpairs==[list(x)for x in pairlist]and chunkrows==r['allExactCrossBodyContacts']and len({tuple(x['sourceFaces'])for x in chunkrows})==len(chunkrows);pairset=set(pairlist);cache={}
  # Replay every claimed actual contact, including zero/point/crossing classification.
  # Omitted contact decisions remain producer evidence over the complete pair list.
  for x in chunkrows:
   i,j=x['sourceFaces'];assert (i,j)in pairset and int(labels[i])!=int(labels[j]);assert x==D.record(world,i,j,labels,cache)
  assert r['allPositiveSurfaceContextGraph']==canon(D.graph(118,chunkrows))and r['nonInteriorCrossingSurfaceContextGraph']==canon(D.graph(118,chunkrows,exclude_interior=True));assert len(r['all6903BodyPairSummaries'])==6903
  for summary,(a,b)in zip(r['all6903BodyPairSummaries'],itertools.combinations(range(118),2)):
   rows=[x for x in chunkrows if set(x['originalBodyLabels'])=={a,b}];assert summary==dict(originalBodies=[a,b],pointOnly=sum(x['dimension']==0 for x in rows),positiveDimensional=sum(x['dimension']>0 for x in rows),bothInteriorCrossings=sum(x['bothRelativeInteriorSurfaceCrossing']for x in rows),contactFaces=[x['sourceFaces']for x in rows])
 walker=D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbodyfreeze');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(D.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']+valid:assert D.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.update(allchunks);paths.add(D.DOC/'diagnostic.json.gz');paths.add(Path(args.lease_file));paths.update(p for p in D.LOCAL.rglob('*')if p.is_file());paths.update(p for p in D.PROPOSAL.iterdir()if p.is_file());D.inputs();assert reservations.owns(lease)
 result=walker.F.freeze(D.BATCH,'complete118-original-body-current-finite-contact-context-no-support-credit',sorted(paths),dict(uids=[D.S.G.P.F.UID],sourceOnly=True,physicalAccepted=False,bodySupportAccepted=False,gradeRootAccepted=False,installationApproved=False,modelReviewWrites=0,completeFaces=46918,completeBodies=118,completeGroundFaces=3240,allRawNegativesRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert D.ref(ROOT/e['path'])==e
 D.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
