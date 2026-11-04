"""Actual complete assets/frozen four-stream proofs for the unexecuted138 policy."""
from run import ROOT,HERE,read,digest
import twin155_complete_boundary_actual_fixture_v1_20261011 as prior
import twin138_named_original_source_placement_proposal_v1_20261011 as k
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def actual_fixture():
 docs,old,refs,receipts=prior.actual_fixture();worlds=next(iter(old.values()))['worlds']
 path=ROOT/'docs/astra-city/government-import'/k.CONTEXT_BATCH/'diagnostic.json.gz'
 p=k.pins();assert digest(path.read_bytes())==p['contextDiagnosticSHA256'];context=read(path);refs.append(ref(path))
 assert context['completeFourWorldSHA256']==p['completeFourWorldSHA256']
 common=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in docs['paths']['rows']]);assert len(common)==827
 expected=set(a['originalBody']for a in docs['bands']['rows'][0]['all293OriginalBodyAssociations'])-set(prior.k.NAMED_SOURCE_PART_FACES)
 assert len(expected)==138 and set(map(int,p['parts']))==expected
 result={}
 for c in context['complete138OriginalImageContexts']:
  part=c['originalBody'];uid=c['actorUID'];assert c['completeOriginalFaces']==docs['graph']['bodies'][part]['globalOriginalFaces']
  hosts={}
  for mode in k.MODES:
   row=next(r for r in docs['paths']['rows']if r['mode']==mode)
   hosts[mode]=sorted(f for b in common if docs['graph']['bodies'][b]['actorUID']==uid for g in row['completeActualCensusForEveryOriginalBody'][b]['completeActualEdgeCensus']['sharedEdgeConnectedComponents']for f in g)
   assert hosts[mode]==c['completeQualifiedNonvisualFacesByMode'][mode]
   band=next(r for r in docs['bands']['rows']if r['mode']==mode);a=next(a for a in band['all293OriginalBodyAssociations']if a['originalBody']==part)
   assert next(r for r in c['allPriorMountingAndFreeEdgeNegativesVerbatim']if r['mode']==mode)['allAssociationAndMountingFindingsVerbatim']==a
   finite=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);offset=0 if uid=='landsd/222465:0'else 13063
   record=next(r for r in c['allFourStreamCompleteFiniteFindings']if r['mode']==mode)
   assert record['completeActualDrawnGroundSHA256']==finite['completeActualDrawnGroundSHA256']
   for f in record['completePartFiniteFindings']:
    i=f['globalOriginalFace']-offset;assert f['completeFiniteProofVerbatim']==finite['allFaces'][i]and f['completeFacetContextVerbatim']==finite['completeAllOriginalFacetContexts'][i]
  for image in c['contextImages']:assert ref(ROOT/image['path'])==image;refs.append(image)
  result[part]=dict(part=part,uid=uid,source_sha=k.SOURCE_SHA[uid],worlds=worlds,context=c,qualified_nonvisual_faces=hosts)
 assert set(result)==expected and sum(len(v['context']['completeOriginalFaces'])for v in result.values())==1521
 for q in context['evidenceRefs']:assert ref(ROOT/q['path'])==q;refs.append(q)
 assert all(ref(ROOT/r['path'])==r for r in refs)
 return docs,result,list({(r['path'],r['sha256']):r for r in refs}.values()),receipts
