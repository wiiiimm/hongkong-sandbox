"""Existing source-only freezer, exact inputs and unchanged review-state fence."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import'
CASES=[('government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011','beverly_hill_k_original_carrier_bounded_grade_route_diagnostic_v1_20261011.py'),('government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011','elm_tree_b_original_podium_complete_finite_contact_inventory_v1_20261011.py')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s)",(['landsd/255543:0','landsd/255939:0','landsd/253874:0','landsd/258892:0'],)).fetchall()
def main():
 before=state();s=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 for batch,producer in CASES:
  doc=B/batch;d=read(doc/'diagnostic.json.gz');assert not(doc/'result.json').exists();paths=set([doc/'diagnostic.json.gz']);m.local_imports(HERE/producer,paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths)
  if 'beverly'in batch:
   note='Complete12640-face original carrier255939 has273 genuine shared-edge bodies. Cap2122 body has674 facets. Against exact historical owned255543 proposed350-facet drawn-ground cache, cap coverage is false with two positive uncovered pieces despite positive lower7661945/65536m. BFS stops atcap:1node,0edges,no route. Missing complete carrier/current actualground prevents this frozen context from qualifying cap or grade route. This does not prove current cap fails, no route exists or global recovery impossible. Existing16 BlockK detail obligations/historical native unsupported-lowrim remain unchanged.'
  else:
   note=d['qualification']+' Direct original contacts are finite geometry only; no ground/root or native reapproval.'
  (doc/'REVIEW.md').write_text('# Original support diagnostic\n\n'+note+'\n\nNo geometry, publication, mutable capture or model review-state changes.\n');save(doc/'review.json',dict(uids=d['uids'],finding=note,sourceOnly=True,currentAcceptance=False,installationApproved=False,globalRecoveryImpossible=False,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([doc/'REVIEW.md',doc/'review.json']);m.F.freeze(batch,'complete-original-source-support-diagnostic-no-current-root-credit',sorted(paths),dict(uids=d['uids'],sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,globalRecoveryImpossible=False,noMutableCapture=True,qualification=note))
 assert state()==before;print(json.dumps(dict(jobs=[read(B/n/'result.json')['jobId']for n,_ in CASES],reviewStateUnchanged=True)))
if __name__=='__main__':main()
