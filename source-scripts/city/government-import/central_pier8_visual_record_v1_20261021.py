"""Record ROOT inspection of exact staged Pier8 day/night desktop/mobile exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-pier8-visual-record-v1-20261021';DOC=BASE/BATCH;source=BASE/'government-xl-central-pier8-staged-browser-v1-20261021'
assert not DOC.exists();_,pins=authenticate(source);refs=[Path(__file__),source/'result.json'];images=[]
for width in [1280,390]:
 report=source/str(width)/'staged-browser.json';assert digest(report.read_bytes())==pins[str(report.relative_to(ROOT))];r=read(report);assert r['passed']and not r['errors'];refs.append(report)
 for time in ['1500','2200']:
  p=source/str(width)/f'staged-landsd-213352-0-{width}-{time}-canvas.png';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
review=dict(uids=['landsd/213352:0'],images=images,reviewer='ROOT',observations=['Complete original roof, colonnade, quay railing and landward stairs visible in exported day views at both widths.','No procedural window overlay on the original source.','No visibly buried upper building geometry in these views.','Night views retain the same silhouette; full native neighbour regression remains pending.'],installationApproved=False,sourceGeometryChanges=0,qualification='Visual observations bound to these exact four exported images; does not grant neighbour, support, whole-source identity or publication acceptance.')
save(DOC/'review.json',review);r=module('pier8_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-bound-staged-visual-observations',refs,review);print(r['jobId'],flush=True)
