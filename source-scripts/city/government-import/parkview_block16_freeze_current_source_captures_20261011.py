"""Freeze authorized complete current captures only; preserves all negatives."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
s=importlib.util.spec_from_file_location('reviewed_capture_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
B=ROOT/'docs/astra-city/government-import';PIN='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute("SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid='landsd/256319:0'").fetchall()
def main():
 before=state();assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==PIN
 for short,producer in [('fresh-current-physical-capture-v1','parkview_block16_fresh_current_physical_capture_20261011.py'),('fresh-current-carrier-capture-v1','parkview_block16_fresh_current_carrier_capture_20261011.py')]:
  batch='government-xl-parkview-block16-'+short+'-20261011';doc=B/batch;paths=set();f.local_imports(HERE/producer,paths);f.local_imports(Path(__file__),paths);f.local_imports(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py',paths)
  paths.update(p for p in (HERE/'local'/batch).rglob('*')if p.is_file())
  for p in list(doc.rglob('*')):
   if p.is_file():
    paths.add(p)
    if p.name.endswith('.json')or p.name.endswith('.json.gz'):f.declared_refs(read(p),paths)
  if short=='fresh-current-physical-capture-v1':
   for n in ['parkview_block16_actual_render_attributes_20261011.mjs','parkview_block16_check_all_current_native_20261011.mjs','parkview_block16_capture_module_closures_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs','actual_float32_model_matrix_bounds_20261011.mjs','xl-final-script-pass.py','acceptance-policy.py']:f.local_imports(HERE/n,paths)
   raw=read(doc/'current-raw-outcome.json');assert raw['currentManifest']['sha256']==PIN
   outcome={'rawOutcome':raw,'foundation':read(doc/'foundation.json'),'metrics':read(doc/'metrics.json'),'diagnosticResolutions':read(doc/'diagnostic-resolutions.json')}
   notes='Exact current identity passes;23 foreign forms are unflagged; all7 retained native forms pass unchanged-terrain regression with no newly buried faces. Literal loader models/loaderAccepted/checksPassed=1 and exceptions=0. All11351 indexed source facets enter the foundation diagnostic:4 fully buried facets,4.902382225623552 square metres, minimum gap -3.6449611480865656m; strict foundation fails. Numeric guard checks36179 position/centroid/low-rim samples (180 low-rim) against197 actual drawn facets; missingTerrain0 and maxSamplerDelta0. All five raw reasons remain: ground-contact-unresolved, sampled-ground-gap-below-model-bottom, sampled-terrain-above-model-bottom, terrain-intersects-source-over-0.5m, whole-source-foundation. No warning is reconciled. Full original, literal and actual F32 attributes are captured, without whole-surface proof from sparse samples. Historical256116/256120 proposed-terrain regressions remain separate immutable evidence.'
  else:
   paths.add(HERE/'parkview_block16_current_carrier_actual_render_attributes_20261011.mjs');scope=read(doc/'capture-scope.json');assert scope['currentManifest']['sha256']==PIN;outcome={'captureScope':scope};notes='Complete unchanged installed native254491 source63133 facets and actual renderer ground/attributes are captured. This establishes current input identity, not whole-native reapproval or positive cap45867 ground clearance.'
  notes+=' Stable post17 manifest '+PIN+'. Source-only current diagnostic; no source/terrain edits, acceptance, installation, function/structural/root/bridge credit or retention-removal approval. Existing cap burial and seven unapproved visual roles remain blocking.'
  (doc/'REVIEW.md').write_text('# Block16 current source-only capture\n\n'+notes+'\n')
  save(doc/'review.json',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,installationApproved=False,nativeReacceptance=False,retentionRemovalApproved=False,finding=notes,outcome=outcome,closedEvidenceRefs=[f.ref(p)for p in sorted(paths)]))
  paths.update([doc/'REVIEW.md',doc/'review.json']);save(doc/'evidence-scope.json',dict(closedEvidenceRefs=[f.ref(p)for p in sorted(paths)],sourceOnly=True,noLiveWrites=True))
  f.F.freeze(batch,short,sorted(paths),dict(uids=['landsd/256319:0','landsd/254491:0'],sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,currentHeldReasonsPreserved=True,scriptFullAcceptancePassed=False,outcome=outcome))
 assert state()==before;assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==PIN
 print('Both current source-only captures frozen/readback verified; Block16 held state and current manifest unchanged.',flush=True)
if __name__=='__main__':main()
