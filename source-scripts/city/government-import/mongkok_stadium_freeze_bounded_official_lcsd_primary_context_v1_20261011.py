"""DRAFT freeze completed unchanged Stadium source attribution, not identity/physical approval."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-stadium-bounded-official-lcsd-primary-context-v1-20261011';DOC=B/BATCH;METHOD=B/'government-xl-mongkok-stadium-original-source-visual-primary-method-v2-20261011/METHOD.md';UID='landsd/240332:0';PROTECTED=[UID,'landsd/240527:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(PROTECTED,)).fetchall()
def main():
 before=state();assert not(DOC/'result.json').exists();d=read(DOC/'diagnostic.json');assert d['uid']==UID and d['sourceOnly']and d['siteContextOnly']and not d['sourceFeatureRegistrationPerformed']and not d['sourceComponentUIDOrElevationProven']and not d['currentAcceptance']and not d['installationApproved']and not d['identityAccepted']and not d['architectureRoleAccepted']and d['governmentGeometryChanges']==0 and d['terrainGeometryChanges']==0 and d['completeExactOfficialResourceCount']==4 and len(d['originalUnwarpedPlanPageExports'])==4
 for e in d['evidenceRefs']:assert ref(ROOT/e['path'])==e
 spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);paths={p for p in DOC.rglob('*')if p.is_file()};paths.add(METHOD);m.local_imports(HERE/'mongkok_stadium_bounded_official_lcsd_primary_context_v1_20261011.py',paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths)
 summary=dict(exactOfficialResources=d['completeExactOfficialResourceCount'],actualReadersPerResource=d['readerCountPerResource'],originalUnwarpedPageExports=len(d['originalUnwarpedPlanPageExports']),allOriginalResourceVersionsPreserved=True,featureRegistrationPerformed=False,sourceUIDOrHeightProven=False,allIdentityGuardObligationsUnresolved=True)
 note=d['qualification']+' '+json.dumps(summary)+' No source body function, low stair/forecourt role, ownership, support or extent waiver is inferred. Source metadata and historical source membership remain distinct from current acceptance; all model/terrain/review/pointer bytes are untouched.'
 (DOC/'REVIEW.md').write_text('# Mongkok Stadium bounded official primary context\n\n'+note+'\n');save(DOC/'review.json',dict(uid=UID,sourceOnly=True,currentAcceptance=False,installationApproved=False,summary=summary,finding=note,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([DOC/'REVIEW.md',DOC/'review.json']);m.F.freeze(BATCH,'mongkok-stadium-bounded-official-primary-context-no-acceptance',sorted(paths),dict(uids=[UID],sourceOnly=True,currentAcceptance=False,installationApproved=False,governmentGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0,pointerWrites=0,protectedDistinctInstalledSource='landsd/240527:0',qualification=note));assert state()==before;print(json.dumps(dict(jobId=read(DOC/'result.json')['jobId'],protectedReviewsUnchanged=True)),flush=True)
if __name__=='__main__':main()
