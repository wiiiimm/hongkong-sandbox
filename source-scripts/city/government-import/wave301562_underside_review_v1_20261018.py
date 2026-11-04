"""Bounded original service-block underside interpretation; not full installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave301562-same-face-contact-v2-20261018';BATCH='government-xl-wave301562-reviewed-underside-v1-20261018';DOC=BASE/BATCH
UID='landsd/301562:0';SHA='8326b663b61047b8728c2fa49550b0ab26b48868a05b8b2588db33004acf1959'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 finite=read(PRIOR/'finite-face-connections.json');assert len(finite['rows'])==4
 for row in finite['rows']:
  assert row['uid']==UID and row['sourceFaces']==144 and row['samples']==90 and row['strictContacts']==73 and row['rawUnresolved']==17 and row['verifiedSameFiniteFaceConnections']==17
  assert row['wholeFoundationBuried']==row['wallIntersections']==0 and all(x['entireSegmentOnSameFiniteFace']for x in row['checks'])
 identity=read(BASE/'government-xl-wave-verdant-remaining-reviewed-identities-v1-20261018/landsd-301562-0-review.json');assert identity['identityOnlyApproved'] and identity['sourceSHA256']==SHA and identity['sourceFaces']==144
 browser=read(BASE/'government-xl-wave301562-focused-context-v3-20261018/staged-browser.json');view=next(x for x in browser['baseContextViews']if 'ramp-low' in x['file']);assert browser['passed'] and not browser['errors'];assert view['viewRay']['firstBuilding']['uid']==UID and view['viewRay']['firstBuilding']['faceIndex']==138 and view['viewRay']['firstTerrain']is None
 assert view['cameraCollisionUid']=='landsd/301560:0' and all(not x['hit']for x in view['collisionVolumes']if x['kind']=='model-surface')
 plan=BASE/'government-xl-wave301562-primary-plan-context-v1-20261018';provenance=read(plan/'provenance.json');assert digest((plan/'the-wave-sales-brochure.pdf').read_bytes())==provenance['sha256']
 decision=dict(uid=UID,sourceSHA256=SHA,sourceFormSHA256=identity['sourceFormSHA256'],worldTrianglesSHA256=identity['worldTrianglesSHA256'],sourceSpecificInterfaceInterpretationAccepted=True,rawStrictWarningsPreserved=True,rawStrictContacts=73,rawSamples=90,rawUnresolved=17,rawUnresolvedFaceIds=[80,87,88,138,142],finiteFaceEvidence=finite,identityReview=identity,primaryDocument=provenance,reviewedPdfPages=[20,47,48],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,fullAcceptance=False,currentMapAcceptance=False,installationApproved=False,reviewBasis=[
 'This decision concerns only the exact144-face original service source and its recorded17rim-above-support points. It does not convert those points into strict contacts or expand the existing1m vertical or0.5m interface allowances.',
 'All17 points are on the bottom or adjoining side faces of the broad service-block end. Each point and an existing strict-contact point lie on the same finite original triangle in all4coordinate modes, verified from complete source arrays. The convex triangle contains the entire joining segment. Maximum along-face span6.769742m is reported as source geometry, not a new admissible gap distance or an engineering load-bearing certificate.',
 'The unchanged source has73existing strict contacts, no missing support samples, no wall-intersection resolutions, and complete144-face compound foundations with zero buried faces in all4modes. The17positions also failed against the original sourceTIN, so they were not introduced by the private transition terrain.',
 'The inspected developer layout and GF/B1plans show a ground-floor service strip beside descending carpark access at the end of Tower2. Exact source identity and the complete assembly plan establish the corresponding service-source context; brochure rotation remains qualitative, not surveyed registration.',
 'The actual renderer view ray reaches original underside face138 directly with no terrain occluder before it. The low camera hits the existing podium interior-volume policy but no actual model surface. This confirms the exposed underside interpretation; it is not a claim that normal walking enters the podium interior.',
 'Taken together, the source-connected slab/wall spans and ground-floor/basement context justify retaining this authored elevated underside rather than filling the gap, moving the model, or deleting faces to force all low-rim rays to touch ground. This is the bounded architectural interpretation of these exact original faces; generic automatic support tests and raw failures remain unchanged.',
 'All whole-assembly identity, retained-neighbour, current terrain/sampler, collision, runtime, failed-download, live publication and installed-ledger obligations remain separate. Changed source bytes, current source form, world geometry or affected terrain requires fresh qualification.'])
 save(DOC/'ROOT-UNDERSIDE-REVIEW.json',decision);(DOC/'ROOT-REVIEW.md').write_text('\n\n'.join(decision['reviewBasis'])+'\n');refs.extend(ROOT/p for p in pins)
 out=module('wave_underside_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-service-source-authored-underside-review-v1',list(set(refs)),dict(uids=[UID],sourceSHA256=SHA,sourceSpecificInterfaceInterpretationAccepted=True,rawUnresolvedPreserved=17,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
