"""DRAFT immutable source-only finite far-body contacts; preserve exact held review state."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-youth-square173512-far-body-full-source-finite-contacts-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PROTECTED=['landsd/173512:0','landsd/139415:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(PROTECTED,)).fetchall()
def main():
 before=state();assert not(DOC/'result.json').exists();d=read(DOC/'diagnostic.json.gz')
 assert d['uid']==PROTECTED[0]and d['fullOriginalFaces']==13100 and d['completeGenuineBodies']==372 and d['selectedFarBodies']==[6,152,153]and len(d['completeSelectedFaces'])==524
 assert d['sourceOnly']and d['allOther372BodyObligationsRetained']and d['prior286FarAndForeignAndSampledBurialFailuresRetained']
 assert not any(d[k]for k in ['currentAcceptance','identityAccepted','mountSupportRootCredit','installationApproved','sourceGeometryChanges','terrainGeometryChanges'])
 for e in d['evidenceRefs']:assert ref(ROOT/e['path'])==e
 spec=importlib.util.spec_from_file_location('reviewed_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 paths={p for p in DOC.rglob('*')if p.is_file()};m.local_imports(HERE/'youth_square173512_far_body_full_source_finite_contacts_v1_20261011.py',paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths)
 summary=dict(fullOriginalFaces=13100,completeGenuineBodies=372,selectedFarBodies=d['selectedFarBodies'],completeSelectedFaces=524,completePairDomain=d['completeOtherBodyFacetPairDomain'],exactPairs=d['completeInclusive3DAABBPairsTested'],completeFiniteContacts=len(d['allExactContacts']),selectedBodySummaries=d['completeSelectedBodySummaries'])
 note=d['qualification'];(DOC/'REVIEW.md').write_text('# Youth Square original far-body finite contacts\n\n'+note+'\n\n'+json.dumps(summary)+'\n')
 save(DOC/'review.json',dict(uids=PROTECTED,sourceOnly=True,summary=summary,finding=note,currentAcceptance=False,installationApproved=False,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([DOC/'REVIEW.md',DOC/'review.json'])
 m.F.freeze(BATCH,'youth-square-original-far-body-finite-contacts-no-acceptance',sorted(paths),dict(uids=PROTECTED,sourceOnly=True,currentAcceptance=False,installationApproved=False,governmentGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0,pointerWrites=0,qualification=note))
 assert state()==before;r=read(DOC/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 print(json.dumps(dict(jobId=r['jobId'],protectedReviewsUnchanged=True,allEvidenceRefsVerified=len(r['evidenceRefs']))),flush=True)
if __name__=='__main__':main()
