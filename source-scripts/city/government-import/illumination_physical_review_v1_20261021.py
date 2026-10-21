"""Scope an original wall/ground interpretation without changing canonical tests."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-physical-review-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
def doc(n,f):return take(n,BASE/n/f)
rn='government-xl-illumination-inset-runtime-v2-20261021';selection=doc(rn,'selection.json.gz');metrics=doc(rn,'metrics.json');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==2
for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
policy=module('illumination_raw_policy',HERE/'acceptance-policy.py');raw=[]
for row in selection['rows']:
 uid=row['uid'];identitybatch='government-xl-remaining-forty-original-identity-v2-20261021' if uid=='landsd/255531:0'else 'government-xl-remaining-forty-podium-identity-v1-20261021'
 identity=doc(identitybatch,uid.split('/')[1]+'/identity.json');assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256']==sources[uid]
 assert identity['exactRouteManifestSHA256']==selection['manifestSHA256']
 for p,h in identity['exactRouteTileHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 metric=next(m for m in metrics['rows']if m['uid']==uid)
 reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=identity['proof']),metric,metrics['profiles']['mobile'])
 expected=['ground-contact-unresolved']if uid=='landsd/255531:0'else ['terrain-intersects-source-over-0.5m']
 assert reasons==expected,(uid,reasons);raw.append(dict(uid=uid,reasons=reasons))
contacts=doc('government-xl-illumination-four-world-contacts-v1-20261021','contacts.json.gz')['rows'];assert len(contacts)==4 and all(r['samples']==r['canonicalContacts']==10 and r['rawInterface']['passed']for r in contacts)
foundation=doc('government-xl-illumination-four-world-foundations-v1-20261021','summary.json')['rows'];assert len(foundation)==8
for r in foundation:assert r['completeTerrainTriangles']==r['triangles'] and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['minimumGapM']>=-.5
samples=doc('government-xl-illumination-actual-samples-v2-20261021','samples.json');old=doc('government-xl-illumination-actual-samples-v1-20261021','samples.json');assert samples['rows']==old['rows'] and len(samples['rows'])==13 and samples['missing']==0
context=doc('government-xl-illumination-low-edge-context-v1-20261021','context.json');assert context['sourceSHA256']==sources['landsd/258737:0'] and context['faceIndex']==1044 and context['normalisedVertical']==0
assert all(r['faceIndex']==1044 and abs(r['renderedMinusOriginalGroundM'])<1e-12 for r in context['samples'])
assert context['vertices'][0][1]==context['vertices'][1][1] or abs(context['vertices'][0][1]-context['vertices'][1][1])<1e-12
assert context['vertices'][2][1]-context['vertices'][1][1]>32
assert {r['faceIndex']for r in context['edgeNeighbours']}=={1045,1522}
profile=doc('government-xl-illumination-wall-profile-v1-20261021','profile.json')['summary'];assert profile['sourceSHA256']==context['sourceSHA256']
images=[];n='government-xl-illumination-wall-context-view-v1-20261021';_,ip=authenticate(BASE/n)
for name in ['source-context.png','wall-profile.png']:
 p=BASE/n/name;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ip[k];refs.append(p);images.append(dict(path=k,sha256=ip[k]))
terrain=doc('government-xl-illumination-local-inset-v2-20261021','terrain-candidates.json');summary=doc('government-xl-illumination-local-inset-v2-20261021','summary.json');assert summary['terrainValidationPassed'] and summary['sourceGeometryChanges']==0
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
review=dict(uids=sorted(sources),reviewer='Codex ROOT',sourceSHA256ByUid=sources,terrainCandidates=terrain,sourceSpecificPhysicalInterpretationAccepted=True,rawPolicyReasons=raw,rawCanonicalFailuresPreserved=True,imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publicationApproved=False,basis='The tower uses its unchanged original podium: all ten strict contacts pass in every captured coordinate representation. The podium has thirteen raw clearance failures on the bottom edge of one continuous vertical original facade (face1044), with exact shared-edge adjoining original faces1045/1522. Original government ground reproduces every failed height, and the corrected inset retains those same records. Source-context and wall-profile exports were inspected: this is shallow embedment at the bottom of the original facade, extending over32m above its bottom, not an upward floor or a whole buried original. Complete foundations in all four coordinate representations retain zero fully buried faces. Accept this exact original wall-ground relationship as source-authored embedment for viewer placement; this is not an engineering foundation certification. The0.5m canonical threshold and13 raw failures are unchanged. No generic wall exception, new support root, model edits or translation are introduced.',scope='Exact two original hashes and corrected V2terrain only. Full neighbour, loader, staged/live browser, collision/picking/recovery and guarded publication remain separate requirements.')
save(DOC/'ROOT-PHYSICAL-REVIEW.json',review);refs.append(HERE/'acceptance-policy.py');module('illumination_physical_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-original-wall-ground-interpretation',refs,review)
