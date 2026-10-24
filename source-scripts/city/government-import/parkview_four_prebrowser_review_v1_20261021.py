"""Reconcile exact four-source checks, leaving browser/publication outstanding."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-prebrowser-review-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,f):
 folder=BASE/('government-xl-'+n+'-20261021');_,ps=authenticate(folder);p=folder/f;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
s=take('parkview-four-raw-identity-v1','selection.json.gz');uids={r['uid']for r in s['rows']};assert len(uids)==4
physical=take('parkview-four-physical-review-v1','ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted'] and set(physical['uids'])==uids
bindings=take('parkview-four-current-bindings-v2','bindings.json.gz');bound={r['uid']:r for r in bindings['rows']}
loader=take('parkview-four-loader-v1','validation.json');assert loader['models']==loader['loaderAccepted']==loader['checksPassed']==4 and loader['exceptions']==0
raw=take('parkview-four-loader-v1','summary.json');assert {r['uid']:r['reasons']for r in raw['rawPolicyReasons']}=={u:['ground-contact-unresolved']for u in uids}
metrics=take('parkview-12-15-shared-runtime-v2','metrics.json');rows=[]
for row in s['rows']:
 uid=row['uid'];sha=row['sourceSHA256'];assert physical['sourceSHA256ByUid'][uid]==sha==bound[uid]['sourceSHA256'];assert bound[uid]['allFourCompleteWorldsIdentical'] and bound[uid]['exactCurrentContactWitnessListsMatch']
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset)
 m=next(x for x in metrics['rows']if x['uid']==uid);assert m['sourceSHA256']==sha and m['sourcePreserved'] and m['missingTerrain']==m['missingDrawnTerrain']==0 and m['maxSamplerDelta']<=.002
 foundation=take('parkview-12-15-shared-runtime-v2',uid.split('/')[1]+'-foundation.json');assert foundation['completeTerrainTriangles']==foundation['triangles']==row['triangles'] and foundation['fullyBuriedTriangles']==foundation['fullyBuriedUpwardTriangles']==0 and foundation['minimumGapM']>=-.5
 if uid in {'landsd/253980:0','landsd/255260:0'}:
  identity=take('parkview-shared-podium-pair-identity-v1','identity.json');assert identity['identityAccepted'] and identity['passed'];assert next(x for x in identity['rows']if x['uid']==uid)['sourceSHA256']==sha
 else:
  identity=take('parkview-four-raw-identity-v1',uid.split('/')[1]+'-identity.json');assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256']==sha
 rows.append(dict(uid=uid,sourceSHA256=sha,identityAccepted=True,wholeTerrainFoundationPassed=True,sourceSpecificPodiumPhysicalReviewAccepted=True,rawPolicyReasons=['ground-contact-unresolved']))
forms=take('parkview-12-15-form-regression-v2','summary.json');assert forms['forms']==26 and forms['ordinaryFlagged']==0 and all(x['existingNative'] and x['reasons']==['existing-native-neighbour-requires-full-mesh-check']for x in forms['flagged'])
native=take('parkview-12-15-native-regression-v2','summary.json');assert native['allRetainedPassed'] and native['nominated']==native['checked']==native['passed']==11
lineage=take('parkview-12-15-terrain-lineage-v2','verification.json');assert lineage['allParentFacesAccounted'] and lineage['maximumParentPlaneResidualM']<=1e-6 and lineage['maximumSourcePlaneResidualM']<=1e-6 and lineage['maximumUpperSurfaceShortfallM']<=1e-6
terrain=take('parkview-12-15-private-terrain-v2','terrain-candidates.json');assert len(terrain)==1;t=terrain[0];assert len(set(t['replaces']['retainedUids']))==11
for p,h in [(ROOT/t['path'],t['sha256']),(ROOT/'3d-viewer'/t['replaces']['url'],t['replaces']['sha256'])]:assert digest(p.read_bytes())==h;refs.append(p)
for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==s['manifestSHA256'];refs.append(manifest)
result=dict(uids=sorted(uids),rows=rows,rawPolicy=raw['rawPolicyReasons'],physicalInterpretation=physical['basis'],ordinaryForms=26,retainedNativeModels=11,terrainCandidates=terrain,currentManifestSHA256=s['manifestSHA256'],prebrowserChecksPassed=True,visualAcceptance=False,installationApproved=False,publicationApproved=False,sourceGeometryChanges=0,remaining=['desktop/mobile staged and live source/retained views','root image inspection','guarded publication and installed receipt'],qualification='Raw canonical podium-contact negatives retained and resolved only by the exact source-specific physical interpretation. Whole actual terrain foundation checks independently pass. No general flag or numerical-threshold bypass.')
save(DOC/'review.json',result);module('parkview_prebrowser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-prebrowser-evidence-review',list(dict.fromkeys(refs)),dict(uids=sorted(uids),prebrowserChecksPassed=True,installationApproved=False));print('Four-source prebrowser checks complete',flush=True)
