"""Durable bounded disposition for fourteen complete unchanged Langham details.

No source corruption, permanent rejection, threshold waiver or missing-face
inference. Source-only historical geometric evidence; current acceptance still
requires fresh current guards. A new method or authoritative provider context
must prove the specific original visual association, rather than rerun failures.
"""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-fourteen-unchanged-method-disposition-v1';DOC=BASE/BATCH
UID='landsd/79318:0';NATIVE='landsd/224399:0'
BODIES=(91,213,214,355,476,477,550,618,630,683,711,761,830,902)
SLICES=('xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1','xl-terrain-recovery-20261011-langham-disconnected-finite-host-diagnostic-v1','xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1','xl-terrain-recovery-20261011-langham-unresolved-original-detail-context-v2','xl-terrain-recovery-20261011-langham-remaining-14-full-host-point-context-v2','xl-terrain-recovery-20261011-langham-remaining14-new-visual-hosts-four-stream-diagnostic-v1','xl-terrain-recovery-20261011-langham-owned-current-four-stream-finite-v1')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];diags={}
 for name in SLICES:
  folder=BASE/name;receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  p=folder/'diagnostic.json.gz';assert next(r for r in receipt['evidenceRefs']if r['path']==str(p.relative_to(ROOT)))==ref(p);diags[name]=read(p);refs.extend((ref(p),ref(folder/'result.json')))
 graph=diags[SLICES[0]];newhosts=diags[SLICES[5]];finite=diags[SLICES[6]]
 assert len(finite['rows'])==4 and all(not r['unprovedFaces']for r in finite['rows'])
 faces=sorted(i for b in BODIES for i in graph['components'][b]['globalOriginalFaces']);assert len(faces)==54 and len(set(faces))==54 and all(graph['components'][b]['actorUID']==UID for b in BODIES)
 newrows=newhosts['rows'];assert len(newrows)==4 and all(len(r['completeFourteenSourceDetails'])==14 for r in newrows)
 for row in newrows:
  assert {r['originalBody']for r in row['completeFourteenSourceDetails']}==set(BODIES)
  assert all(r['allFiveCompleteHostsOutsideExistingBand']is True and len(r['allFiveCompleteConditionalVisualHostBounds'])==5 for r in row['completeFourteenSourceDetails'])
 points=diags[SLICES[4]]['rows'];assert len(points)==4
 for mode in points:
  assert {r['originalBody']for r in mode['perCompleteOriginalBody']}==set(BODIES)
  for part in mode['perCompleteOriginalBody']:
   assert not part['allPositiveDimensionalInterfaces']
   assert part['completeOriginalSourceFaces']==graph['components'][part['originalBody']]['globalOriginalFaces']
   exactpoints={tuple(q)for c in part['allExactPointInterfaces']for q in c['exactContact']['exactPoints']}
   assert len(exactpoints)==(1 if part['originalBody']==683 else 0)
 assert finite['sourceSHA256']=='1be9a6399ce7e447ae734182f278bef08e7bbb58aa97cb8a468b133d175c00e4'
 context=BASE/SLICES[3]/'original-unresolved-details-1800x1600.png';refs.append(ref(context))
 records=[]
 for b in BODIES:
  part=graph['components'][b]
  records.append(dict(originalBody=b,completeOriginalSourceFaces=part['globalOriginalFaces'],completeOriginalBounds=part['bounds'],sourceRoleUnknown=True,
   disposition='not-qualified-under-completed-unchanged-source-mounting-methods',
   exactOriginalPositiveStructuralAttachmentNotProved=True,
   previousComplete865ConditionalHostScope=ref(BASE/SLICES[4]/'diagnostic.json.gz'),
   newCompleteFiveConditionalVisualHostScope=ref(BASE/SLICES[5]/'diagnostic.json.gz'),
   completeCurrentFrozenFourRepresentationClearance=ref(BASE/SLICES[6]/'diagnostic.json.gz'),
   pointOnlyContactCannotBridgeOrSupplyTwoDistinctAnchors=(b==683),
   reason='One distinct original/current point only; no positive-dimensional interface or second distinct mount anchor.'if b==683 else'No original/literal/two explicit Float32 contacts with the complete conditional865-host scope; full mounting/loop methods do not qualify the complete part.',
   allFiveNewVisualHostsStrictlyOutsideExistingPointOneMetreBand=True,
   concreteRevisitCondition='A separately justified exact full-original component role with authoritative provider/site mounting context, or a new complete finite attachment/association certificate under unchanged limits; alternatively an authenticated provider source revision. Preserve all original faces, raw failures, root/foreign/current guards. No point glue, invented mounting function, source pose shift or tolerance widening.',
   structuralRootOrBridgeCredit=False,publicationApproved=False,permanentRejection=False,corruptionInferred=False))
 assert all(ref(ROOT/r['path'])==r for r in refs)
 out=dict(uids=[UID],sourceSHA256='1be9a6399ce7e447ae734182f278bef08e7bbb58aa97cb8a468b133d175c00e4',completeUnqualifiedSourceBodies=list(BODIES),completeUnqualifiedSourceFaces=faces,dispositions=records,
  disposition='held-source-mounting-evidence',humanStatus='held-source-evidence',
  nextStep='Advance independent recoverable sources. Revisit these14 only with the specific new evidence/method in each disposition; unchanged method reruns cannot install them.',
  frozenCurrentBaselineOnly=True,noFreshCurrentReacceptance=True,
  wholeSourceNotCertifiedByThisDisposition=True,allOtherPositiveProofsPreserved=True,
  noInstallationWithCompletedMethods=True,permanentRejection=False,corruptionInferred=False,requiresAI=False,requiresHumanDecision=False,
  sourceOnly=True,currentAcceptance=False,structuralRootCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'fourteen-complete-original-langham-source-mounting-unchanged-method-held-disposition-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeUnqualifiedBodies=14,completeUnqualifiedFaces=54,disposition=out['disposition'],humanStatus=out['humanStatus'],nextStep=out['nextStep'],permanentRejection=False,corruptionInferred=False,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
