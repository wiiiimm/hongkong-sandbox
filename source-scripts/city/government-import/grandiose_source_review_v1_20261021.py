"""Bind the two unchanged Grandiose originals to exact completed acceptance evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-source-review-v1-20261021';DOC=BASE/BATCH
NAMES={k:'government-xl-grandiose-'+v+'-20261021'for k,v in dict(capture='assembly-capture-v1',mainIdentity='podium-identity-review-v1',roofIdentity='roof-identity-v1',physical='physical-review-v1',neighbours='neighbour-review-v2',browser='private-browser-v2',overview='private-browser-v3',contact='contact-review-v1').items()}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for k,n in NAMES.items():
   p=BASE/n/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p);pins[k]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def bind(k,p):
  key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key],key;refs.append(p);return dict(path=key,sha256=pins[k][key])
 def take(k,file):
  p=BASE/NAMES[k]/file;bind(k,p);return read(p)
 selection=take('capture','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert set(sources)=={'landsd/246824:0','landsd/81731:0'}
 physical=take('physical','ROOT-PHYSICAL-REVIEW.json');near=take('neighbours','ROOT-NEIGHBOUR-REVIEW.json');identity=take('mainIdentity','ROOT-IDENTITY-REVIEW.json');roof=take('roofIdentity','identity.json');context=take('roofIdentity','context.json');contact=take('contact','ROOT-CONTACT-REVIEW.json')
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['sourceSHA256ByUid']==sources
 assert near['sourceSpecificNeighbourInterpretationAccepted']and not near['remainingNeighbourFailures']
 assert identity['sourceIdentityAccepted']and identity['sourceSHA256']==sources['landsd/246824:0']
 assert roof['passed']and not roof['reasons']and roof['sourceSHA256']==sources['landsd/81731:0']
 assert context['identity']['sourceExcessCoveredByUnrelatedFormsM2']==0
 assert contact['geometryChanges']==0 and not contact['installationApproved']
 reports=[]
 for k in ['browser','overview']:
  for width in [1280,390]:
   report=take(k,f'{width}/staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==4
   for v in views:assert v['pick']==v['collision']==v['uid']and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and v['sourceSHA256']==sources[v['uid']]
   if width==390:
    failures=[v for v in report['views']if v.get('phase')=='failed-download'];assert {v['uid']for v in failures}==set(sources)and all(v['fallbackRetained']for v in failures)
   reports.append(bind(k,BASE/NAMES[k]/str(width)/'staged-browser.json'))
 images=[]
 for k,w,file in [('overview',1280,'staged-landsd-246824-0-1280-1500.png'),('overview',390,'staged-landsd-246824-0-390-2200.png'),('browser',1280,'staged-landsd-81731-0-1280-1500.png'),('browser',390,'staged-landsd-81731-0-390-2200.png'),('browser',1280,'staged-local-joint-roof-podium-original-corner-1280.png')]:images.append(bind(k,BASE/NAMES[k]/str(w)/file))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256'];refs.append(manifest)
 review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,foreignContactContextAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,rawStrictFailuresRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,foreignContactBasis='Previously reviewed authored contact with 27898 remains source context, not a nonintersection claim or independent rejection. Its old terrain failures are not reused as current acceptance: fresh complete four-mode foundations, actual terrain runtime and full current regional neighbour checks govern this proposal. Roof identity has no unrelated-footprint coverage. No original facets are clipped or shifted.',visualLimitations='The initial oblique podium view is largely obscured by towers and is not used as its shape evidence. The steeper overview shows the roof/podium footprint between the towers. The oblique roof view shows curved stepped roof details. The corner close-up shows source walls but does not independently establish precise corner clearance; exact whole-source numerical contacts provide that evidence. Night materials are dark without procedural windows; surrounding buildings and UI obscure portions. Mobile captures include failure-test banners; complete reports verify recovery. Screenshots do not prove unseen clearance.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 module('grandiose_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-final-review-bound-to-source-and-browser',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
