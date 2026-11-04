"""Existing source-only freezer, exact inputs and unchanged review-state fence."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import'
CASES=[('government-xl-beverly-hill-k-current-carrier-four-stream-bounded-grade-route-diagnostic-v3-20261011','beverly_hill_k_current_carrier_four_stream_bounded_grade_route_diagnostic_v3_20261011.py'),('government-xl-elm-tree-original-podium-complete-current-finite-ground-diagnostic-v1-20261011','elm_tree_original_podium_complete_current_finite_ground_diagnostic_v1_20261011.py'),('government-xl-beverly-hill-k-complete-current-carrier-strict-clearance-grade-exclusion-v1-20261011','beverly_hill_k_complete_current_carrier_strict_clearance_grade_exclusion_v1_20261011.py')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s)",(['landsd/255543:0','landsd/255939:0','landsd/253874:0','landsd/258892:0'],)).fetchall()
def main():
 before=state();s=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 for batch,producer in CASES:
  doc=B/batch;d=read(doc/'diagnostic.json.gz');assert not(doc/'result.json').exists();paths=set([doc/'diagnostic.json.gz']);m.local_imports(HERE/producer,paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths)
  if 'four-stream-bounded'in batch:
   note='Allfour complete12640 source world tuples are byte-identical; strictcap2122 fullycovered/positive against completeactualcurrent4facetground. Existing128face/127edge BFS budget reached, no grade path nominated; not global failure or entirecarrier grade exclusion. Original350facet historical proposedcoveragegap and16BlockKdetails remain unresolved.'
  elif 'elm-tree'in batch:
   x=next(iter(d['allDistinctWholeSourceFiniteProofs'].values()));note='Allfour complete764face podium world tuples byte-identical. Current8facet actualground covers everywhole source projection; '+str(len(x['ordinaryFailingSourceFaces']))+' sourcefacets fail unchanged ordinary−.5 finite predicate; minimumexact '+x['minimumCertifiedOrRefinedLowerM']+'m. Original99 linecontacts to1112facet towerbody269 remain sourcecontext only; all305 other bodies/podiumgrade and rawhistoricalBASIC233656/253871 regressions unresolved. This currentfailure is distinct from proposed/authenticTIN.'
  else:
   x=next(iter(d['allDistinctWholeSourceFiniteAndWallProofs'].values()));note='Every12640 unchanged carrierfacet and allfour byteidentical worlds against all4actualcurrentdrawngroundfacets: allStrict='+str(x['allStrictFiniteClearanceProved'])+', exactminimum='+x['minimumCertifiedOrRefinedLowerM']+'m, '+str(len(x['allExactVerticalNonzeroWallFacets']))+' complete verticalwalls, '+str(len(x['allExactPositiveUpperGroundWallInterfaces']))+' positive exactupper-envelopegradeinterfaces. This scoped exactsource/current result supplies no whole-native reapproval/root/foreign/currentacceptance. Seek actual independently evidenced original lower support/component/sourcegrade; no globalhistoricalimpossibility or invented geometry.'
  (doc/'REVIEW.md').write_text('# Original support diagnostic\n\n'+note+'\n\nNo geometry, publication, mutable capture or model review-state changes.\n');save(doc/'review.json',dict(uids=d['uids'],finding=note,sourceOnly=True,currentAcceptance=False,installationApproved=False,globalRecoveryImpossible=False,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([doc/'REVIEW.md',doc/'review.json']);m.F.freeze(batch,'complete-current-source-support-diagnostics-no-root-credit',sorted(paths),dict(uids=d['uids'],sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,globalRecoveryImpossible=False,noMutableCapture=True,qualification=note))
 assert state()==before;print(json.dumps(dict(jobs=[read(B/n/'result.json')['jobId']for n,_ in CASES],reviewStateUnchanged=True)))
if __name__=='__main__':main()
