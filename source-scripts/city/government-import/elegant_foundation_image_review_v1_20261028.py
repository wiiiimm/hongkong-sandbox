"""Freeze actual ROOT inspection of twelve private BASIC foundation exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
SOURCE='government-xl-elegant-garden-foundation-closeups-v1-20261028'
BATCH='government-xl-elegant-garden-foundation-image-review-v1-20261028'

def main():
 receipt,pins=authenticate(BASE/SOURCE)
 refs=[Path(__file__),BASE/SOURCE/'result.json'];rows=[]
 for width in [1280,390]:
  path=BASE/SOURCE/str(width)/'staged-browser.json'
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
  report=read(path);assert report['passed']and report['diagnosticOnly']and not report['errors']
  assert {r['uid']for r in report['foundationDiagnostics']}=={'landsd/213586:0','landsd/99061:0','landsd/336456:0'}
  refs.append(path)
  for row in report['foundationDiagnostics']:
   assert len(row['candidates'])==48 and len(row['exports'])==2
   for image in row['exports']:
    p=path.parent/image['file'];assert image['selectionClosed']
    assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
   rows.append(dict(uid=row['uid'],width=width,lowerTriangles=row['lowerTriangles'],visibleLowerSamples=row['best']['visibleLowerSamples'],totalLowerSamples=row['best']['totalLowerSamples'],cameraCollision=row['best']['cameraCollision'],exports=[e['file']for e in row['exports']]))
 notes=dict(uids=sorted({r['uid']for r in rows}),actualExportsInspected=12,rows=rows,browserJob=receipt['jobId'],visualReviewApproved=False,physicalAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,
  findings=[
   '213586: clean day/night exports show the narrow ground-level seam in desktop and mobile. Much of the footing is naturally obscured by adjacent BASIC walls. Lower-band samples are 1/13 desktop and 3/13 mobile; no whole-interface clearance is inferred.',
   '99061: desktop close-up shows posts against the source podium and terrain; mobile is dominated by the source podium, which blocks all12lower-band rays. This remains an explicitly unresolved mobile foundation observation, not a failed or corrupt source model.',
   '336456: desktop and mobile show a canopy with posts against the irregular terrain. Other BASIC walls hide parts of the footprint; 2/8lower-band samples are visible in each viewport. These views do not prove absence of all native intersections.',
   'Selection highlights are removed in every export. The exact active original context is recorded per image, but the full16joint scene is not required or proven by this separate targeted diagnostic. Night BASIC window patterns remain bright while original surfaces are dark; no materials were changed.'],
  next='Complete canopy post collision/contact evidence and obtain a useful mobile view of the main canopy lower posts without hiding neighbours or changing geometry/budgets. Keep independent original-source identity, boundary, support and publication work pending.')
 save(BASE/BATCH/'root-observations.json',notes)
 module('foundation_image_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-unselected-desktop-mobile-basic-foundation-export-inspection',refs,notes)

if __name__=='__main__':main()
