"""Fence complete current progress and exact remaining source-detail reasons."""
import importlib.util
from fractions import Fraction as F
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-ying-hoi-current-causal-dispositions-v1';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();names=['government-xl-terrain-recovery-ying-hoi-existing-terrain-current-v1-20261010','xl-terrain-recovery-20261010-ying-hoi-fresh-original-support-replay-v1','xl-terrain-recovery-20261010-ying-hoi-complete-finite-clearance-v1','xl-terrain-recovery-20261010-ying-hoi-complete-original-local-host-planes-v1','xl-terrain-recovery-20261010-ying-hoi-complete-original-local-host-planes-v2','xl-terrain-recovery-20261010-ying-hoi-complete-original-perpendicular-host-boundaries-v1','xl-terrain-recovery-20261010-ying-hoi-remaining-54-original-mounts-v1','xl-terrain-recovery-20261010-ying-hoi-original-mounted-details-visual-v1'];refs=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name;r=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.extend([ref(q) for q in p.rglob('*') if q.is_file()]);refs.extend(r['evidenceRefs'])
 graph=read(BASE/names[1]/'diagnostic.json.gz');perpendicular=read(BASE/names[5]/'diagnostic.json.gz');mounts=read(BASE/names[6]/'diagnostic.json.gz');nearest={r['component']:r for r in mounts['results']};held=[]
 for r in perpendicular['results']:
  if r['sourceOnlyBoundaryBandPassed']:continue
  k=r['component'];c=graph['components'][k];row=dict(component=k,actorUID=c['actorUID'],everyOriginalFace=c['globalOriginalFaces'],wholeOriginalBounds=c['bounds'],rawBoundaryReasons=r['reasons'],completePerimeterCertificate=False,structuralRootCredit=False,visualRoleAccepted=False)
  if k in nearest:
   distances=[F(f['nearestCompleteOriginalRootedSurface']['exactSquaredDistanceM2']) for f in nearest[k]['everyOriginalFaceNearestWitness'] if f['nearestCompleteOriginalRootedSurface']];row.update(allOriginalFacetNearestWitnesses=nearest[k]['everyOriginalFaceNearestWitness'],exactMinimumSquaredSourceDistanceM2=str(min(distances)),everyNearestWitnessBeyondPointOneM=all(x>F(.1)**2 for x in distances),exactOriginalVertexAnchors=nearest[k]['exactOriginalAuthoredVertexContacts'])
  row['currentHeldReason']='whole-original-detail-separated-over-existing-point-one-band' if row.get('everyNearestWitnessBeyondPointOneM') else 'complete-original-detail-finite-mount-role-not-yet-proved';held.append(row)
 assert [r['component'] for r in held if r.get('everyNearestWitnessBeyondPointOneM')]==[276,277]
 contexts=[]
 for uid in ['205663','207957']:
  p=BASE/f'xl-terrain-recovery-20261010-ying-hoi-{uid}-complete-current-context-v1';d=read(p/'diagnostic.json.gz');assert not d['continuousAffectedFaces'] and not d['wholeSourceUncoveredFaces'];contexts.append(dict(uid=d['uid'],wholeSourceFaces=d['wholeSourceFaces'],completeCurrentContext=ref(p/'diagnostic.json.gz')));refs.extend(d['evidenceRefs']+[ref(p/'diagnostic.json.gz')])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert graph['currentManifestSHA256']==digest(manifest.read_bytes());refs.extend([ref(manifest),ref(Path(__file__))]);refs=sorted({(r['path'],r['sha256']):r for r in refs}.values(),key=lambda r:(r['path'],r['sha256']))
 result=dict(uids=['landsd/207957:0','landsd/205663:0'],candidateUID='landsd/207957:0',retainedAlreadyInstalledUID='landsd/205663:0',currentManifestSHA256=digest(manifest.read_bytes()),completeOriginalFaces=11590,completeOriginalComponents=655,independentlyRootedStructuralComponents=len(graph['resolvedOriginalComponents']),unrootedOriginalVisualCandidates=200,sourceOnlyPerpendicularBoundaryPasses=len(perpendicular['sourceOnlyPassedComponents']),remainingUnprovedOriginalDetailComponents=held,completeOriginalAndRenderedFiniteClearancePassed=True,completeCurrentContexts=contexts,wholeSourceCurrentFoundationIdentityNeighbourRuntimePassed=True,rawTowerGroundOnlyWarningsRemainPreserved=True,currentHeldReason='complete-original-visual-detail-role-coverage-incomplete',qualification='The 165 perpendicular boundary passes are geometry diagnostics, not mounted-role acceptance. Both details276/277 exceed the unchanged0.1m band even at their nearest rooted facets; no threshold waiver. All35 residual parts, actual attributes, faces, distances and original boundary failures remain. Source geometry/root/terrain unchanged; no permanent impossibility claim or installation credit.',installationApproved=False,publication=False,structuralCreditFromVisualParts=False,evidenceRefs=refs)
 save(DOC/'dispositions.json.gz',result)
 spec=importlib.util.spec_from_file_location('ying_hold_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-current-original-detail-causal-held-dispositions-v1',[ROOT/r['path'] for r in refs],{k:v for k,v in result.items() if k!='evidenceRefs'})
if __name__=='__main__':main()
