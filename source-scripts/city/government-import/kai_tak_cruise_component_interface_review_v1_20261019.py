"""Source-specific interpretation of unchanged rooftop interfaces; not publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-component-interface-review-v1-20261019';DOC=BASE/BATCH
NAMES=['component-views-v2','four-world-interfaces-v1','component-four-mode-foundations-v1','original-component-checks-v2'];SUFFIX='-20261019'
def folder(n):return BASE/('government-xl-kai-tak-cruise-'+n+SUFFIX)
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 foundations=read(folder('component-four-mode-foundations-v1')/'summary.json')['rows'];assert len(foundations)==52 and all(r['passed']and r['buried']==r['upwardBuried']==0 for r in foundations)
 interfaces=read(folder('four-world-interfaces-v1')/'interfaces.json.gz')['rows'];contacts=read(folder('four-world-interfaces-v1')/'contacts.json.gz')['rows'];bounds=read(folder('four-world-interfaces-v1')/'path-bounds.json.gz')['rows'];assert len(contacts)==3348 and all(r['contactPassed']for r in contacts);assert len(bounds)==28 and all(r['passed']and r['maximumBoundM']<=.001 for r in bounds)
 special='landsd/92919:0';rawspecial=[r for r in interfaces if r['uid']==special];assert len(rawspecial)==4
 for r in rawspecial:
  p=r['proof'];assert p['samples']==p['wallIntersections']==42 and p['strictContacts']==0 and not p['unresolved'] and not p['passed'];assert all(x['sourceWallFaces']and x['supportFaces']and -.5<=x['gap']<-.1 for x in p['resolved'])
 selection=read(folder('original-component-checks-v2')/'selection.json.gz')['rows'];assert len(selection)==13
 for r in selection:assert read(folder('original-component-checks-v2')/(r['uid'].split('/')[1]+'-identity.json'))['passed']
 rendered=read(folder('component-views-v2')/'render.json');assert len(rendered['views'])==8 and not rendered['errors'];images=[v['image']for v in rendered['views']]
 for img in images:assert digest((ROOT/img['path']).read_bytes())==img['sha256']
 review=dict(reviewer='Codex ROOT',uids=[r['uid']for r in selection],sourceSpecificInterfaceInterpretationAccepted=True,installationApproved=False,publicationApproved=False,rawStrictFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceBindings=[dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],modelId=r['modelId'],sourceForm=r['source'])for r in selection],imagesActuallyInspected=images,basis=[
 'ROOT inspected all eight corrected V2 plan/oblique exports: green original component, purple unchanged terminal. Six components show curved projecting roof sections above their enclosures;92856 is an enclosure beside the tower,92919 a small rooftop enclosure. This is visual context, not engineering certification.',
 'Five components pass strict interface checks. Seven other components retain all837 original failed rays, with exact original finite-face starting membership and continuous shared-edge lower-face paths to contact. All3348 endpoint checks pass the unchanged maximum-surface interval across four captured coordinate representations; all28 path groups remain within the existing0.001m membership tolerance. No geometry is created from these paths.',
 'For92919 all42 original low-rim samples lie on original vertical walls that also intersect the original terminal surface at the same XZ. This holds in all four captured modes, within the existing0.5m embedding cap. Its canonical passed flag remains false because it has no strict bottom-rim samples. The visible enclosure rises above the deck; complete50-face foundations in every mode contain no wholly buried faces. The source-specific interpretation accepts these actual wall/deck contacts, not a floating or wholly buried mesh.',
 'All13 exact source identities and all52 complete compound foundations pass. Preserve the entire original meshes, fixed1x scale and original placement. This interpretation is limited to these exact source revisions and this terminal source; no generic support threshold or other model approval changes.'],remaining=['Terminal original ground relationship qualification','Current complete14-source candidate loader, neighbour and runtime checks','Retained299814 native terrain replacement proof','Staged/live desktop and mobile visual, collision, picking and fallback checks','Guarded installation and Neon installed verification'])
 save(DOC/'ROOT-INTERFACE-REVIEW.json',review)
 module('kai_interface_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-exact-original-rooftop-interface-interpretation',list(dict.fromkeys(refs)),dict(uids=review['uids'],sourceSpecificInterfaceInterpretationAccepted=True,installationApproved=False))
if __name__=='__main__':main()
