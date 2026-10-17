"""Freeze closed, nonaccepting current source captures and exact role evidence."""
import ast,importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import'
S=importlib.util.spec_from_file_location('block6_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');F=importlib.util.module_from_spec(S);S.loader.exec_module(F)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def local_imports(p,seen):
 if p in seen or not p.exists():return
 seen.add(p)
 if p.suffix!='.py':return
 for node in ast.walk(ast.parse(p.read_text())):
  if isinstance(node,ast.ImportFrom)and node.module:local_imports(HERE/(node.module.split('.')[0]+'.py'),seen)
  if isinstance(node,ast.Import):
   for n in node.names:local_imports(HERE/(n.name.split('.')[0]+'.py'),seen)
def declared_refs(x,paths):
 if isinstance(x,dict):
  if 'path'in x and 'sha256'in x and isinstance(x['path'],str):
   p=ROOT/x['path'];assert p.is_file(),str(p);assert digest(p.read_bytes())==x['sha256'],str(p);paths.add(p)
  if 'inputHashes'in x:
   for s,h in x['inputHashes'].items():
    p=ROOT/s;assert p.is_file()and digest(p.read_bytes())==h,str(p);paths.add(p)
  for v in x.values():declared_refs(v,paths)
 elif isinstance(x,list):
  for v in x:declared_refs(v,paths)
def review_state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid='landsd/255438:0'").fetchall()
def main():
 before=review_state();names=[('fresh-current-physical-capture-v1','parkview_block6_fresh_current_physical_capture_20261011.py'),('fresh-current-carrier-capture-v1','parkview_block6_fresh_current_carrier_capture_20261011.py'),('current-four-stream-source-proofs-v1','parkview_block6_current_four_stream_source_proofs_20261011.py'),('current-four-opening-guards-v3','parkview_block6_current_four_opening_guards_v3_20261011.py'),('fresh-current-bounded-route-binding-v1','parkview_block6_fresh_current_bounded_route_binding_20261011.py')]
 for short,producer in names:
  batch='government-xl-parkview-block6-'+short+'-20261011';doc=B/batch;assert doc.exists();paths=set();local_imports(HERE/producer,paths);local_imports(Path(__file__),paths)
  paths.update(p for p in (HERE/'local'/batch).rglob('*')if p.is_file())
  for p in list(doc.rglob('*')):
   if p.is_file():
    paths.add(p)
    if p.name.endswith('.json')or p.name.endswith('.json.gz'):declared_refs(read(p),paths)
  if short=='fresh-current-physical-capture-v1':
   for n in ['parkview_block6_actual_render_attributes_20261011.mjs','parkview_block6_check_all_current_native_20261011.mjs','xl-final-script-pass.py','acceptance-policy.py']:
    local_imports(HERE/n,paths)
  if short=='fresh-current-carrier-capture-v1':paths.add(HERE/'parkview_block6_current_carrier_actual_render_attributes_20261011.mjs')
  if short=='current-four-stream-source-proofs-v1':
   for n in ['test_complete_original_lower_opening_mounts_v2_20261011.py','test_exact_original_segment_surface_contact_band_20261009.py']:local_imports(HERE/n,paths)
  if short=='current-four-opening-guards-v3':
   for n in ['test_complete_original_lower_opening_mounts_v3_20261011.py','test_complete_original_lower_opening_mounts_v2_20261011.py','test_exact_original_segment_surface_contact_band_20261009.py']:local_imports(HERE/n,paths)
  notes='Source-only evidence, unchanged provider geometry and current terrain. No live acceptance or installation. Current own body/host hashes and complete literal/explicit F32 attributes are bound. Explicit F32 arithmetic is not a universal GPU/camera guarantee.'
  if short=='fresh-current-physical-capture-v1':notes+=' Exact current identity passes; strict whole-source foundation passes, 23 foreign forms checked and no neighbour flags. All five relevant retained native forms resolve their existing guards. The two raw warnings remain: ground-contact-unresolved and sampled-ground-gap-below-model-bottom. The numeric ground guard samples model low vertices against runtime captured rendered terrain; the whole-facet finite proof is separate.'
  if short=='fresh-current-carrier-capture-v1':notes+=' Complete fresh native carrier ground has 25,167 facets; capture is not whole native reacceptance.'
  if short=='current-four-stream-source-proofs-v1':notes+=' All 11,041 original facets pass complete-current-ground finite bounds; 85 nonzero shared-edge bodies remain, 80 positive contacts reach 81 structural-role bodies. Four lower openings associate over their full edges within the unchanged fixed band; no solid/function/root/bridge credit.'
  if short=='current-four-opening-guards-v3':notes+=' Standalone v3 requires one genuine nonzero shared-edge body and only nonzero original host facets. Eleven adversarial tests pass, retaining nine v2 cases and adding closed disconnected tetrahedron and degenerate host rejection. All four actual bodies pass in all four bound streams; normalized complete v2 mounting proofs are verbatim unchanged.'
  if short=='fresh-current-bounded-route-binding-v1':notes+=' Complete tuple equality proves bounded route/cap reuse in all four streams. Qualified path60333→38937→38936→54398→54397→54396→54656→54655→58400, all eight whole edges exposed, only qualified wall/finite facets credited. Facet54320 uncovered area and partly buried52248–52249 remain excluded. No whole carrier body credit.'
  (doc/'REVIEW.md').write_text('# Parkview Block6: '+short+'\n\n'+notes+'\n\nRemaining promotion requirements: independent root review of numerical role logic, fully bound current runtime/browser and publisher guards, and guarded installation with unchanged originals. Primary owner/contractor imagery supplies estate context only; exact fixture identity/function remains unknown.\n')
  save(doc/'review.json',dict(uids=['landsd/255438:0','landsd/254491:0'],finding=notes,scriptFullAcceptancePassed=False,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,remaining=['independent-role-review','current-runtime-browser-and-publisher-gates','guarded-installation'],bodyRoleLimits=['four-opening-associated-visual-bodies-no-function-solid-root-or-bridge'],closedEvidenceRefs=[ref(p)for p in sorted(paths)]))
  paths.add(doc/'REVIEW.md');paths.add(doc/'review.json');save(doc/'evidence-scope.json',dict(closedEvidenceRefs=[ref(p)for p in sorted(paths)],sourceOnly=True,noLiveWrites=True))
  F.freeze(batch,short,sorted(paths),dict(uids=['landsd/255438:0','landsd/254491:0'],outcome=short+'-source-only-complete',scriptFullAcceptancePassed=False,currentAcceptance=False,sourceOnly=True,currentHeldReasonsPreserved=True))
 assert review_state()==before,'Held Block6 review state changed during source-only freeze'
 print('All five source-only jobs verified; Block6 held review state unchanged.')
if __name__=='__main__':main()
