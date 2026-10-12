"""DRAFT: read-only saved-proof partition, no numerical or acceptance execution."""
import json,hashlib,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
BATCHES={
 'finite':'government-xl-west-wing26195-complete-current-finite-ground-v3-20261012',
 'grade':'government-xl-west-wing26195-bounded-current-grade-cap-routes-v2-20261012',
 'corridor':'government-xl-west-wing26195-exposed-edge-connected-facet-corridors-v1-20261012',
 'seed153':'government-xl-west-wing26195-seed153-two-edge-corridor-expansion-v1-20261012',
 'visual':'government-xl-west-wing26195-current-typed-original-visual-surface-roles-v1-20261012'}

def load(name):
 p=BASE/BATCHES[name]/'diagnostic.json.gz';raw=p.read_bytes()
 return json.loads(gzip.decompress(raw)),dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest())

def partition(finite,grade,corridor,seed153,visual):
 bindings=finite['allFourStreamBindings'];assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'}
 for d in [grade,corridor,seed153,visual]:
  assert d['allFourStreamBindings']==bindings and d['currentManifest']==finite['currentManifest'] and d['sourceOnly'] and not d['physicalAccepted']
 bodies=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];assert len(bodies)==118
 flat=[i for body in bodies for i in body];assert len(flat)==46918 and sorted(flat)==list(range(46918))
 ids=bodies[0];assert len(ids)==5062 and len(set(ids))==5062
 result={}
 for key,proof in finite['distinctCompleteFiniteProofs'].items():
  records=proof['allWholeFacetProofs'];assert len(records)==46918 and [r['face']for r in records]==list(range(46918))
  g=grade['distinctBoundedRouteDiagnostics'][key];c=corridor['distinctBoundedCorridorDiagnostics'][key];s=seed153['distinctBoundedDiagnostics'][key]
  gs={r['seedFace']:r for r in g['routes']};assert len(gs)==42 and all(r['genuineExposedGradeDiagnostic']for r in gs.values())
  early={i for i,r in gs.items()if r['boundedOriginalPath']};later={r['seedFace']for r in c['boundedConnectedRoutes']if r['diagnosticRouteFound']}
  assert len(early)==17 and len(later)==24 and early.isdisjoint(later) and s['diagnosticRouteFound'] and not s['wholeFacet154StrictPositiveClaim'] and not s['newGradeRootClaim']
  assert set(gs)==early|later|{153} and all(i in ids for i in gs)
  failed={i for i in ids if not records[i]['ordinaryFiniteProved']};assert failed==set(gs)
  strict={i for i in ids if not records[i]['strictPositiveFiniteProved']};assert len(strict)==418 and failed<=strict
  rows=[]
  for i in ids:
   r=records[i];role='strict-clearance-only'if r['strictPositiveFiniteProved']else'ordinary-clear-with-retained-strict-warning'
   if i in failed:role='saved-emerging-grade-wall-and-corridor-context-only'
   route=('whole-exposed-edge'if i in early else'exposed-subinterval-and-within-facet'if i in later else'segment-only-wall154-to-cap44545'if i==153 else None)
   rows.append(dict(sourceFace=i,originalBody=0,ordinaryFiniteProved=r['ordinaryFiniteProved'],strictPositiveFiniteProved=r['strictPositiveFiniteProved'],completeProjectionCovered=r['completeProjectionCovered'],savedProofRole=role,savedRouteKind=route,wholeFacetRoleAccepted=False,bodyRootAccepted=False))
  assert not records[154]['strictPositiveFiniteProved'] and records[154]['ordinaryFiniteProved']
  result[key]=dict(completeBody0Faces=5062,ordinaryFailureFaces=sorted(failed),strictUncertifiedFaces=sorted(strict),remainingOrdinaryPassStrictUncertifiedFaces=sorted(strict-failed),allFacetEvidence=rows,sourceFacet154SegmentOnly=True,body0Qualified=False)
 roles=visual['typedSourceVisualRoleContext'];assert roles['sourceVisualOnlyBodies']==[108,113] and not roles['fullRoleReconciliationAccepted']
 return dict(sourceOnly=True,noNumericRecomputation=True,completeOriginalBodies=118,body0WholeRoleQualified=False,groundRootAccepted=False,physicalAccepted=False,installationApproved=False,legacyAcceptanceBackfillAllowed=False,allFourStreamBindings=bindings,distinctSavedPartitions=result,remainingInputs=['The 376 ordinary-clear facets retain strict warnings but require no new strict-clearance rule; identify only source-specific role obligations actually required by the unchanged carrier contract.', 'Independent complete connected body0 root/role qualification binding the 42 genuine failures, positive-dimensional grade and certified exposed-edge/eligible-cap routes, plus exact source interpretation.', 'Body2 has 25 retained strict warnings but ordinary clearance passes; its independent role/support obligation must follow the existing contract rather than a new strict-facet requirement.', 'Remaining 116 body roles and all proper interior crossing relationships require exact typed reconciliation.', 'Complete current identity, foreign/native, water/foundation/runtime/browser checks remain independent.'])

if __name__=='__main__':
 # DRAFT ONLY: no save, DB, lease, worker or current acceptance; ROOT review first.
 raise SystemExit('Draft only; numerical execution is not authorised.')
