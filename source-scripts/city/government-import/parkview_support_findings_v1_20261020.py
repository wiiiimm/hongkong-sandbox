"""Persist bounded source-context findings; no placement waiver or geometry edits."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-support-findings-v1-20261020';DOC=BASE/BATCH
names=['parkview-three-four-world-contacts-v2','parkview-three-support-views-v1','parkview-mixed-support-v1','parkview-nearest-source-faces-v1'];refs=[Path(__file__)];receipts=[]
assert not DOC.exists()
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for n in names:
  p=BASE/('government-xl-'+n+'-20261020')/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts.append(r);refs.append(p)
images=[]
for uid in ['256113','255917','255646']:
 p=BASE/'government-xl-parkview-three-support-views-v1-20261020'/(uid+':0-junctions.png');q=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()));assert q in receipts[1]['evidenceRefs'];images.append(q);refs.append(p)
nearpath=BASE/'government-xl-parkview-nearest-source-faces-v1-20261020/nearest.json.gz';assert dict(path=str(nearpath.relative_to(ROOT)),sha256=digest(nearpath.read_bytes()))in receipts[3]['evidenceRefs'];refs.append(nearpath)
rows=[{k:v for k,v in r.items()if k!='points'}for r in read(nearpath)['rows']]
review=dict(uids=['landsd/256113:0','landsd/255917:0','landsd/255646:0'],reviewer='Codex ROOT',imagesActuallyViewed=images,nearestFaceDiagnostics=rows,observations=['ROOT inspected all three opposite-view context exports. Unresolved points run along lower tower wall boundaries amid original layered podium faces. These translucent cropped views do not establish complete whole-source placement or rule out all visible gaps.', 'Complete original/literal/left-F32/balanced-F32 support accounts agree: Blocks5/3/7 retain58/69/46 unresolved samples after direct finite contacts. Adding archived drawn terrain does not resolve more.', 'Literal nearest finite podium distances: Block3 maximum0.048411679m; Block7 maximum0.040479933m; Block5 maximum5.262027678m. These distances explain distinct diagnostic scales but do not modify the1mm direct-face query tolerance or grant support approval.', 'Packed original root horizontal translations are multiples of0.0625m at roughly838km coordinates. This is only a provenance lead, not proof of a packing bug or a justification for moving/scaling geometry. Next compare untouched provider GLTF scene matrices with the packed scene and inspect acquisition code.', 'Block5 additionally retains its earlier complete-foundation buried face5177. No permanent rejection assigned; investigate the several-metre outliers separately.'],installationApproved=False,placementApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False)
save(DOC/'ROOT-FINDINGS.json',review)
module('parkview_findings_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-support-findings-no-approval',refs,review)
