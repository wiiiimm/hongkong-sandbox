"""Freeze closed, nonaccepting current source captures and exact role evidence."""
import ast,importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import'
S=importlib.util.spec_from_file_location('block17_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');F=importlib.util.module_from_spec(S);S.loader.exec_module(F)
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
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid='landsd/256116:0'").fetchall()
def main():
 before=review_state();names=[('fresh-current-physical-capture-v1','parkview_block17_fresh_current_physical_capture_20261011.py'),('fresh-current-carrier-capture-v1','parkview_block17_fresh_current_carrier_capture_20261011.py'),('current-four-stream-source-proofs-v1','parkview_block17_current_four_stream_source_proofs_20261011.py'),('fresh-current-bounded-route-binding-v1','parkview_block17_fresh_current_bounded_route_binding_20261011.py')]
 for short,producer in names:
  batch='government-xl-parkview-block17-'+short+'-20261011';doc=B/batch;assert doc.exists();paths=set();local_imports(HERE/producer,paths);local_imports(Path(__file__),paths)
  paths.update(p for p in (HERE/'local'/batch).rglob('*')if p.is_file())
  for p in list(doc.rglob('*')):
   if p.is_file():
    paths.add(p)
    if p.name.endswith('.json')or p.name.endswith('.json.gz'):declared_refs(read(p),paths)
  if short=='fresh-current-physical-capture-v1':
   for n in ['parkview_block17_actual_render_attributes_20261011.mjs','parkview_block17_check_all_current_native_20261011.mjs','parkview_block17_capture_module_closures_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs','xl-final-script-pass.py','acceptance-policy.py']:
    local_imports(HERE/n,paths)
  if short=='fresh-current-carrier-capture-v1':paths.add(HERE/'parkview_block17_current_carrier_actual_render_attributes_20261011.mjs')
  if short=='current-four-stream-source-proofs-v1':
   for n in ['test_complete_original_lower_opening_mounts_v2_20261011.py','test_exact_original_segment_surface_contact_band_20261009.py']:local_imports(HERE/n,paths)
  if short=='current-four-opening-guards-v3':
   for n in ['test_complete_original_lower_opening_mounts_v3_20261011.py','test_complete_original_lower_opening_mounts_v2_20261011.py','test_exact_original_segment_surface_contact_band_20261009.py']:local_imports(HERE/n,paths)
  notes='Source-only unchanged provider geometry and stable manifest ba6399c629e6c8876125a339cc80e0a03974080449cf156438c9fe6c346901f3 after root Block6 installation. No live acceptance, installation, source/terrain edits or whole-native reapproval. Explicit F32 arithmetic is not a universal GPU/camera guarantee. Historical terrain-regresses-neighbour:landsd/256120:0 remains in original held evidence; current no-terrain-change foreign check is a distinct new scope, not a waiver.'
  if short=='fresh-current-physical-capture-v1':notes+=' Exact current identity passes, 23 foreign forms flagged zero, all six current retained native forms pass unchanged-terrain regression guards with no newly buried faces. All 15,614 actual indexed source facets pass full foundation check, no buried faces, minimum finite drawn gap 2.075176084839m. Numeric guard samples every position vertex and triangle centroid plus low-rim edge interiors at <=1m XZ spacing against actual makeTerrain facets, separately compares makeTerrainSampler:49,847 checks/344 low-rim, maxSamplerDelta0, missingTerrain0. Two raw warnings stay ground-contact-unresolved and sampled-ground-gap-below-model-bottom. Literal loader models/loaderAccepted/checksPassed integer1, exceptions0. Acceptance/native/neighbour module closures plus the validator single explicit literal dynamic call are bound at start/end. No new terrain proposals.'
  elif short=='fresh-current-carrier-capture-v1':notes+=' Complete fresh native carrier ground has25,167 unchanged facets; original/native literal/left/balanced F32 source meshes/matrices/attributes are recorded. This capture supplies no whole-native source or ground reapproval.'
  elif short=='current-four-stream-source-proofs-v1':notes+=' All four complete owned worlds are byte-identical SHA64c8caaf2abc65c8cc12acbf1ae9e7a7c3d7dfd9f6ee8e74b9eeb9b5f5161dca. Every15,614 facet satisfies existing ordinary finite clearance predicate>=−.5m. Minimum conservative bound−1099/4096m is not a strict-positive proof or penetration witness. Full actual ground195 facets SHA69a6a6a30b480a07542fa4e30b39c990079ac8d205a29d17177eca82d9b3b007.93 genuine body censuses/91 positive interfaces retain92 conditional structural bodies (15,602 nonzero facets); ten-face body62 passes exact body/host-bound v3 full lower-opening association without exact contact/function/solid/root/bridge credit. Original zero-area faces24/25 remain unchanged, included in all-facet terrain proof but excluded from support and host band credit.'
  else:notes+=' Complete owned/native four-stream worlds and entire fresh carrier drawn ground equal exact old cap/contact/grade-route proof inputs, enabling proof reuse only on full tuple equality. Qualified original path51646→49682→54417→54418, three whole exposed shared edges, only qualified grade-wall/intermediate finite facets/strict cap credited. Actual lower wall vertex penetration−57736278035/18488549376m and prior facet54320 coverage gap/partly buried52248–52249 negatives remain preserved; no whole wall/native-body clearance. Cap54418 strict whole finite lower113831/32768m remains separate from ordinary whole-owned source predicate.'
  (doc/'REVIEW.md').write_text('# Parkview Block17: '+short+'\n\n'+notes+'\n\nRemaining promotion requirements: independent root review of numerical role logic, fully bound current runtime/browser and publisher guards, and guarded installation with unchanged originals. Primary owner/contractor imagery supplies estate context only; exact fixture identity/function remains unknown.\n')
  save(doc/'review.json',dict(uids=['landsd/256116:0','landsd/254491:0'],finding=notes,scriptFullAcceptancePassed=False,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,remaining=['independent-role-review','current-runtime-browser-and-publisher-gates','guarded-installation'],bodyRoleLimits=['body62-opening-association-only-no-function-solid-root-or-bridge','original-zero-area24/25-retained-no-support-band-credit'],closedEvidenceRefs=[ref(p)for p in sorted(paths)]))
  paths.add(doc/'REVIEW.md');paths.add(doc/'review.json');save(doc/'evidence-scope.json',dict(closedEvidenceRefs=[ref(p)for p in sorted(paths)],sourceOnly=True,noLiveWrites=True))
  F.freeze(batch,short,sorted(paths),dict(uids=['landsd/256116:0','landsd/254491:0'],outcome=short+'-source-only-complete',scriptFullAcceptancePassed=False,currentAcceptance=False,sourceOnly=True,currentHeldReasonsPreserved=True))
 assert review_state()==before,'Held Block17 review state changed during source-only freeze'
 print('All four current source-only jobs verified; Block17 held review state unchanged.')
if __name__=='__main__':main()
