"""DRAFT source-only immutable topology/registration diagnostic freezer; no reviews or pointers."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';DOC=B/BATCH;C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';A=B/'government-xl-science-museum-open-sided-original-gltf-members-acquisition-v1-20261011';UIDS=['landsd/80343:0','landsd/83471:0'];METHOD=B/'government-xl-science-museum-original-open-sided-contact-topology-method-v1-20261011/method.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def main():
 before=state();assert not(DOC/'result.json').exists();d=read(DOC/'diagnostic.json.gz');assert d['sourceOnly']and not d['currentAcceptance']and not d['installationApproved']and not d['identityAccepted']and not d['roleApproval']and d['geometryChanges']==0
 for folder in [C,A]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 for e in d['evidenceRefs']:assert ref(ROOT/e['path'])==e
 spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);paths={p for p in DOC.rglob('*')if p.is_file()};paths.update([METHOD,HERE/'test_science_museum_contact_relative_interior_v1_20261011.py']);m.local_imports(HERE/'science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py',paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths);m.declared_refs(read(METHOD),paths)
 summary=dict(originalOpenBodies=len(d['originalOpenBodyDetails']),nonCoplanarPositivePairs=d['nonCoplanarPositiveDimensionalPairs'],coplanarPositivePairs=d['coplanarPositiveDimensionalPairs'],properRelativeInteriorSurfaceCrossingPairs=d['properNoncoplanarRelativeInteriorCrossingPairs'],pointOnlyPairs=d['pointOnlyPairs'],originalOfficialFootprintCoverageRemainsRaw9075Percent=True,primaryFeatureRegistrationUnresolved=True)
 note=d['qualification']+' '+json.dumps(summary)+' Historical BASIC height remains estimated/null recorded, exact source height remains untouched. Source footprint registration describes original/historical context only; no runtime/ownership/attachment exemption or current acceptance.'
 (DOC/'REVIEW.md').write_text('# Science Museum original contact topology\n\n'+note+'\n');save(DOC/'review.json',dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,summary=summary,finding=note,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([DOC/'REVIEW.md',DOC/'review.json']);m.F.freeze(BATCH,'science-museum-original-contact-topology-registration-no-acceptance',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,governmentGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0,pointerWrites=0,qualification=note));assert state()==before;print(json.dumps(dict(jobId=read(DOC/'result.json')['jobId'],protectedReviewsUnchanged=True)))
if __name__=='__main__':main()
