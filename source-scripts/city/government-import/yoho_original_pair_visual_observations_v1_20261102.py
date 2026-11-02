"""Freeze ROOT's bounded observations of actual exported source/retained views.

This note records images actually inspected; it grants no physical, neighbour,
engineering, performance, per-facade or publication acceptance.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 base=ROOT/'docs/astra-city/government-import';prefix='government-xl-yoho-mall-ii273672-';batch=prefix+'bounded-visual-observations-v1-20261102';out=base/batch;assert not out.exists();refs=[Path(__file__)];panels=[];sheets=[]
 for name,count in [(prefix+'private-browser-inspection-sheets-v1-20261102',68),(prefix+'retained-supplement-inspection-sheets-v1-20261102',16)]:
  path=base/name/'panel-bindings.json';bindings=read(path);assert bindings['fullFramesPreserved']and not bindings['exportedSourceImagesModified'];refs.append(path);current=[]
  for sheet in bindings['rows']:
   p=ROOT/sheet['path'];assert digest(p.read_bytes())==sheet['sha256'];refs.append(p);sheets.append(dict(path=sheet['path'],sha256=sheet['sha256']))
   for panel in sheet['panels']:
    p=ROOT/panel['path'];assert digest(p.read_bytes())==panel['sha256'];refs.append(p);current.append(panel)
  assert len(current)==count;panels.extend(current)
 assert len(panels)==84 and len({p['path']for p in panels})==84 and len(sheets)==21
 actors={p['uid']for p in panels};assert len(actors)==17 and {'landsd/273672:0','landsd/3007:0'}<=actors
 for name in [prefix+'two-originals-private-preview-v1-20261102',prefix+'retained-camera-supplement-v1-20261102']:
  _,pins=authenticate(base/name);refs.append(base/name/'result.json')
  for width in ['1280','390']:
   path=base/name/width/'staged-browser.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];report=read(path);assert report['passed']and not report['errors'];refs.append(path)
 fixture,pins=authenticate(base/(prefix+'atomic-fixture-v1-20261102'));refs.append(base/(prefix+'atomic-fixture-v1-20261102')/'result.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
 result=dict(uids=fixture['uids'],sourceSHA256ByUid=fixture['sourceSHA256ByUid'],currentManifestSHA256=digest(manifest.read_bytes()),reviewer='ROOT',imagesActuallyViewed=panels,sheetsActuallyViewed=sheets,initialExportCount=68,supplementExportCount=16,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,observations=['Both unchanged originals render as a curved mall podium with authored roof/walkway details and a separate bridge-junction housing. All actual desktop/mobile day/night source panels were inspected.','All15 retained actors were inspected in actual current-scene exports. Initial300895mobile and300896views were obscured by nearby facades; the camera-only supplement now shows their roofs/plan context without source, terrain or visibility edits.','Night panels are dark on untextured originals. These observations do not certify every facade or repair/reaccept pre-existing installed-model support negatives.','All16 unresolved column groups were separately viewed in two directions: original wall sides extend through actual grade beneath existing authored decks. No caps or geometry were generated.','Three atomic UI exports were inspected as lifecycle context only; interface panels obscure some geometry, so they are not substitutes for the unobstructed source canvas captures.'],qualification=__doc__)
 save(out/'ROOT-VISUAL-OBSERVATIONS.json',result);module('yoho_bounded_visual_observation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-actual-original-and-retained-export-observations',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
