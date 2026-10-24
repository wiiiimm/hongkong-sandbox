"""Exact-source lower-interface interpretation; not publication or a global waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-grade-review-v1-20261018';DOC=BASE/BATCH
NAMES=['three-podium-terrain-v2','thirteen-foundations-v2','podium-clearance-locations-v2','original-grade-faces-v1','full-grade-context-v1','grade-views-v1','hoi-yu-prior-review-v2']
def folder(n):return BASE/('government-xl-olympian-two-'+n+'-20261018')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   d=folder(n);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 f=read(folder('thirteen-foundations-v2')/'summary.json');assert f['allModesPassed']and len(f['rows'])==52
 full=read(folder('full-grade-context-v1')/'summary.json')['rows'];assert len(full)==4 and {r['mode']for r in full}=={'original','literal','left','balanced'}
 expected=read(folder('original-grade-faces-v1')/'summary.json')['rows'][1]['flaggedFaces']
 for r in full:assert r['wholeSourceFaces']==22075 and r['continuousNegativeFaceIds']==expected and not r['negativeUpwardFaceIds']and not r['uncoveredFaces']and r['negativeWithoutExposedWitness']==[9705,9706,9707,9708]
 contexts=read(folder('original-grade-faces-v1')/'239351:0-faces.json.gz')['rows'];assert len(contexts)==102 and all(abs(r['normalYRatio']or 0)<.001 for r in contexts)
 locations=read(folder('podium-clearance-locations-v2')/'summary.json')['rows'];assert all(r['maxCandidateOriginalDifference']<.00003 for r in locations)
 metrics=read(folder('three-podium-terrain-v2')/'metrics.json')['rows'];assert all(r['sourcePreserved']and r['maxSamplerDelta']==0 for r in metrics)
 images=sorted(folder('grade-views-v1').glob('*.png'));assert len(images)==3
 decision=dict(uids=[r['uid']for r in locations],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in locations},reviewer='Codex ROOT',originalGradeInterpretationAccepted=True,sourceSpecific=True,rawTerrainMetrics=metrics,completePodiumGroundContexts=full,inspectedImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],observations=[
 'The source-local terrain mask previously discarded zero-area projected vertical walls. Including their finite projected edges removed the introduced 7.4m terrain discrepancy without moving or editing a government building. Existing preservation margins were unchanged.',
 'All surviving flagged points reproduce government source TIN to within 0.03mm. The full 22075-face podium check in four coordinate modes isolates 51 near-vertical lower perimeter-wall faces; no upward surface is affected and every face has terrain coverage. Four short lower-wall faces9705-9708 have no exposed point. These are retained source-authored buried wall portions, not claimed visible or repaired. The diagnostic interface images show these wall regions within the lower perimeter assembly.',
 'The three originals retain their source-authored low-rim gaps: main podium -0.032 to1.130m; second podium0.795 to1.062m; Park Avenue podium0.474 to0.855m. These are accepted as limitations of these exact original exports and source terrain, with source pose unchanged. This is not a claim of zero physical gap, structural certification, or a new global contact tolerance. All52 existing complete foundation checks pass.',
 'The corrected candidate introduces no new wholly buried geometry in25 current native neighbours; Hoi Yu retains its independently verified prior exact-source support interpretation. Ten BASIC neighbour flags identify the ten intended above-podium originals and require the complete13-model installation together.'
 ],modelGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,publication=False,fullAcceptance=False,remaining=['complete desktop/mobile browser acceptance','combined source acceptance and guarded installation'])
 save(DOC/'ROOT-GRADE-REVIEW.json',decision);refs.extend(ROOT/p for p in pins)
 module('grade_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-exact-original-grade-interpretation-v1',refs,dict(uids=decision['uids'],originalGradeInterpretationAccepted=True,fullAcceptance=False))
if __name__=='__main__':main()
