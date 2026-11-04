"""DRAFT immutable source-only diagnostic freezer, no geometry/review/pointer changes."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded
NAME='government-xl-mongkok-stadium240332-adjacent15c-historical-original-tin-acquisition-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/NAME;PRODUCER=HERE/'mongkok_stadium240332_adjacent15c_historical_original_tin_acquisition_v1_20261011.py'
UIDS=['landsd/240332:0','landsd/240527:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def main():
 d=decoded(read(DOC/'diagnostic.json.gz'));before=state();assert not(DOC/'result.json').exists()and d['sourceOnly']and not d['currentAcceptance']and not d['terrainCandidateCreated'];assert d['uids']==UIDS;assert d['originalTerrainMemberRequests']==len(d['completeOriginalMembers'])==3 and d['historicalOfficialIndexOnly']and not d['poseDecodePerformed']and not d['adjacentFiniteCoverageOrSeamsProved'];summary=dict(originalTerrainMembers=3,sourceSheet=d['sourceSheet'],sourceRevision=d['sourceRevision'],freshIndexSucceeded=False,finiteCoverageProved=False)
 spec=importlib.util.spec_from_file_location('reviewed_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);paths={p for p in DOC.rglob('*')if p.is_file()and not p.name.endswith('.tmp')};m.local_imports(PRODUCER,paths);m.local_imports(Path(__file__),paths);m.declared_refs(d,paths);assert all(ref(ROOT/e['path'])==e for e in d['evidenceRefs']);note=d['qualification']+' Summary: '+json.dumps(summary)
 (DOC/'REVIEW.md').write_text('# Source-only diagnostic\n\n'+note+'\n');save(DOC/'review.json',dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,summary=summary,finding=note,evidenceRefs=[ref(p)for p in sorted(paths)]));paths.update([DOC/'REVIEW.md',DOC/'review.json']);m.F.freeze(NAME,'bounded-original-terrain-source-diagnostic-no-acceptance',sorted(paths),dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,installationApproved=False,terrainCandidateCreated=False,originalSourceGeometryChanges=0,liveTerrainChanges=0,qualification=note));assert state()==before;print(json.dumps(dict(jobId=read(DOC/'result.json')['jobId'],protectedReviewStateUnchanged=True,summary=summary)))
if __name__=='__main__':main()
