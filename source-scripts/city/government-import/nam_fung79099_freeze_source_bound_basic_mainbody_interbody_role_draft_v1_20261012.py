"""DRAFT saved-mainbody and complete interbody contact context; no root approval."""
import argparse,json,itertools
from pathlib import Path
from collections import Counter
from nam_fung79099_source_bound_basic_mainbody_interbody_role_draft_v1_20261012 import ROOT,HERE,read,ref,module,connect,reservations,inputs,mainbody_saved_facts,typed_graph,DOC,LOCAL,BATCH,CAP,JOIN,FINITE,UIDS,PROTECTED,MANIFEST_SHA

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);a=p.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists()
 bound,capture,join,receipt,scope,before,selections,prior,finite=inputs();d=read(DOC/'diagnostic.json.gz');bodies=prior['originalCensus']['sharedEdgeConnectedComponents'];zero=prior['originalCensus']['exactNonrenderingOriginalFaces'];labels={i:b for b,ids in enumerate(bodies)for i in ids}
 assert d['uid']==UIDS[0]and d['sourceSHA256']==prior['sourceSHA256']and d['carrierUID']==PROTECTED and d['completeFaces']==13061 and d['completeOriginalBodies']==569 and d['originalZeroFaces']==75
 assert d['currentManifest']==scope['currentManifest']and d['currentNativeCount']==6649 and d['allFourStreamBindings']==finite['allFourStreamBindings']
 assert d['mainbodySavedCarrierFacts']==mainbody_saved_facts(prior,finite)
 for k in ['rootAccepted','bodySupportAccepted','physicalAccepted','installationApproved','wholeBASICReaccepted','originalGovernmentPodiumUsed','finiteContactPrismGradeArithmeticReplayed']:assert d[k]is False
 assert d['sourceOnly']and d['fullIdentityForeignNativeFoundationRuntimeGatesStillIndependent']and d['sourceGeometryChanges']==d['terrainGeometryChanges']==0
 assert {b['wholeWorldSHA256']for b in d['allFourStreamBindings'].values()}==set(d['distinctInterbodyRoleContexts'])
 for sh,g in d['distinctInterbodyRoleContexts'].items():
  assert g['worldSHA256']==sh and g['allOriginalBodyPairCount']==161596 and g['all75AuthoredZeroFacesNoRootOrBridge']==zero
  assert g['actualWorldZeroFaceIds']==sorted(prior['distinctSourcePrismContactProofs'][sh]['actualBodyCensus']['exactNonrenderingOriginalFaces'])
  records=g['allExactCrossBodyContacts'];assert len({tuple(r['sourceFaces'])for r in records})==len(records)
  for r in records:
   i,j=r['sourceFaces'];assert 0<=i<j<13061 and r['originalBodyLabels']==[labels.get(i),labels.get(j)]and r['originalNonrenderingSourceFlags']==[i in zero,j in zero]
   assert r['actualNonrenderingSourceFlags']==[i in g['actualWorldZeroFaceIds'],j in g['actualWorldZeroFaceIds']]and r['dimension']in [0,1,2]
  assert g['typedGraph']==typed_graph(records)
  counts=Counter(tuple(sorted(r['originalBodyLabels']))for r in records if None not in r['originalBodyLabels'])
  assert g['bodyPairContactCounts']==[dict(originalBodies=[i,j],contactCount=counts.get((i,j),0))for i,j in itertools.combinations(range(569),2)]
  roles=g['all569BodyRoleCandidates'];assert len(roles)==569
  for i,r in enumerate(roles):
   assert r['originalBody']==i and r['completeOriginalFaceIds']==bodies[i]and not r['terminalRoleAccepted']and not r['structuralSupportAccepted']and not r['independentGroundRootRequiredForEveryDetail']
   assert r['conditionalSourcePath']==g['typedGraph']['conditionalGraph']['conditionalPositiveDimensionalContactPaths'].get(str(i))
  chunks=[];contacts=[];last=0
  for path in sorted((LOCAL/'chunks'/sh).glob('*.json.gz')):
   chunk=read(path);c=chunk['contract'];assert c['worldSHA256']==sh and c['firstPair']==last and c['exclusiveLastPair']>last and c['candidatePairs']==g['completeClosed3DAABBCandidatePairs']and c['candidatePairListSHA256']==g['candidatePairListSHA256']
   assert len(chunk['pairs'])==c['exclusiveLastPair']-last;last=c['exclusiveLastPair'];chunks+=chunk['pairs'];contacts+=chunk['contacts']
  assert last==g['completeClosed3DAABBCandidatePairs']and contacts==records and len({tuple(p)for p in chunks})==len(chunks)
  import hashlib
  assert hashlib.sha256(json.dumps([tuple(p)for p in chunks],separators=(',',':')).encode()).hexdigest()==g['candidatePairListSHA256']
 for e in d['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_role_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.declared_refs(d,paths)
 paths.update(ROOT/e['path']for r in [capture,join,receipt]for e in r['evidenceRefs']);paths.update(q for folder in [DOC,LOCAL]for q in folder.rglob('*')if q.is_file())
 (DOC/'REVIEW.md').write_text('Nam-specific geometric BASIC carrier candidate: reuse41 mainbody positive interfaces onto exactly62 previously grade-qualified caps and complete1601-face actual connected mainbody; no BASIC/contact/prism/grade/finite rerun. New spatial-indexed complete interbody context retains all569 bodies/75 authored zero faces and every crossing flag. Body0 is an unaccepted root candidate; source paths are conditional. Disconnected authored terminal details need exact visual/mount evidence, never independent ground roots by default or structural bridges. Complete current identity/foreign/native/foundation/water/runtime/browser gates remain independent. No source, pose, scale, terrain, review, physical or installation changes.\n');paths.add(DOC/'REVIEW.md');inputs();assert reservations.owns(lease)
 result=walker.F.freeze(BATCH,'nam-source-bound-mainbody-and-conditional-assembly-context',sorted(paths),dict(uids=UIDS+[PROTECTED],sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,currentNativeCount=6649,completeFaces=13061,completeOriginalBodies=569,originalZeroFaces=75,physicalAccepted=False,rootAccepted=False,installationApproved=False,wholeBASICReaccepted=False,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),rootAccepted=False)))
if __name__=='__main__':main()
