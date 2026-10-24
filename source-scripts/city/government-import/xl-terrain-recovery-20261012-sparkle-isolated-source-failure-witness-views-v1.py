"""DRAFT: additive isolated source views; no clearance/contact/role recheck."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict, Counter
import json, importlib.util, subprocess, sys, time, uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT, HERE, read, save, digest, reservations, connect

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261012-sparkle-isolated-source-failure-witness-views-v1'
DOC = BASE/BATCH
LOCAL = HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CONTEXT = BASE/'xl-terrain-recovery-20261012-sparkle-complete-original-current-ground-failure-context-v1'
FINITE = BASE/'xl-terrain-recovery-20261012-sparkle-complete-current-drawn-ground-finite-v1'
INTEGRATION = BASE/'government-xl-updated-code-integration-20261012/integration.json'
HISTORY = BASE/'government-xl-heya-before-installation-current-history-v1-20261011/root-actual-historical-input-contract.json'
METHOD = BASE/'government-xl-sparkle-isolated-source-witness-method-draft-20261012/METHOD.md'
CURRENT = '2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS = ['landsd/242198:0', 'landsd/228000:0', 'landsd/113733:0', 'landsd/138091:0']
MODES = ['originalSource', 'actualLiteral', 'explicitLeftAssociatedFloat32', 'explicitBalancedFloat32']
LOW = [2603,2604,2605,2608,2609,2613,2614,2615,2616,2617,2618]
BODY_IDS = [19,20,22,23,24]
PINS = {
 'diagnostic.json.gz': '189dc5756c33bdfe69a1ca6acef8a98c1aac1dd63832eaf002e21491890fd5b0',
 'source-gltf-documents-and-provider-poses.json.gz': 'ba9953fba43e30a8a7b98b566f100d2ffe2ebe83d948b0e2a7ad11d981d7d035',
 'complete-ground-facet-provenance.json.gz': 'fdda86480679de31d2a3b2adc62bf226d96d0f5b50f24fc276bd819daf3eaf4f',
}
FREEZER = HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
LOCAL_IMPORTS = [HERE/'run.py', HERE/'popcorn_original_ancillary_identity_20261009.py',
 HERE.parent/'shared-modelling/db.py', HERE.parent/'shared-modelling/jobs.py',
 HERE.parent/'shared-modelling/reservations.py', HERE.parent/'shared-modelling/reservation_runner.py']
PREFLIGHT = METHOD.parent/'offline-schema-pin-preflight.json'

def ref(p):
 return dict(path=str(p.resolve().relative_to(ROOT)), sha256=digest(p.read_bytes()))

def exact(pin):
 p = ROOT/pin['path']
 assert p.is_file() and ref(p) == pin, pin
 return p

def owned():
 lease = read(LEASE)
 assert reservations.owns(lease) and not DOC.exists()
 refs = [ref(Path(__file__)), ref(FREEZER), ref(INTEGRATION), ref(HISTORY), ref(METHOD), ref(PREFLIGHT),
         *[ref(p) for p in LOCAL_IMPORTS]]
 preflight = read(PREFLIGHT)
 assert preflight['passed'] is True and preflight['caller'] == ref(Path(__file__))
 assert preflight['currentLocalStaticImportClosure'] == sorted([ref(Path(__file__)),ref(FREEZER),*[ref(p) for p in LOCAL_IMPORTS]],key=lambda p:p['path'])
 assert preflight['savedContextPins'] == {name:ref(CONTEXT/name) for name in PINS}
 last = time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last >= 20:
   assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
   last = time.monotonic()
 for name,sha in [('developer-the-sparkle-floor-plan.pdf','5889ea450e5f7e204d9612576885a66557e19f8ee0b5a7135f3f7ae40ec211a0'),
                  ('developer-ground-floor-page3.png','501056a928c37a9a13b459808eb3adb14a4e151aa863d34a035329253cbcc30b')]:
  pin=ref(METHOD.parent/'primary'/name);assert pin['sha256']==sha;refs.append(pin)
 refs.extend(ref(METHOD.parent/'primary'/name) for name in ['developer-the-sparkle-floor-plan.request.json','developer-floor-plan-text.txt'])
 manifest = ROOT/'3d-viewer/city/data/manifest.json'
 start = ref(manifest)
 assert start['sha256'] == CURRENT
 refs.append(start)
 integration = read(INTEGRATION)
 historical = read(HISTORY)
 # This explicit archive map supplies old bytes only. It is never a current
 # loader equivalence, an arbitrary digest search or a receipt rewrite.
 archives = {}
 for r in integration['actualHistoricalVersions']:
  assert r['originalPath'] == r['actualBefore']['path']
  assert r['archive']['sha256'] == r['actualBefore']['sha256']
  exact(r['archive'])
  archives[r['originalPath'],r['actualBefore']['sha256']] = r['archive']
 # The genuine pre-Heya archive has its own exact root contract, whose
 # concrete schema is checked here rather than inferred from filenames.
 assert ref(HISTORY)['sha256'] == '27e12065a1de099b3d9d6530dc05d5e73462655d16622a309bb050292dae2589'
 historical_pins = {
  '3d-viewer/city/data/manifest.json':'947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6',
  'docs/astra-city/model-integration-20260909/current-source-review.json':'16bac8df5edc4bf370340bc9444c09c730445e86022a53b2b340751ba8faef57',
  '3d-viewer/city/data/building-progress.json':'ce6631c4035120fc2ae83fd3aba79ffaa3e103c11440aa2946151dda0a7838bd',
 }
 assert historical['historicalOnly'] is True and historical['hashAliasesOrSignatureOverrides'] is False
 actual_history = {r['actualPreInstallationInput']['path']:r for r in historical['actualHistoricalBytes']}
 assert set(actual_history) == set(historical_pins)
 for path,sha in historical_pins.items():
  row = actual_history[path]
  assert row['actualPreInstallationInput'] == dict(path=path,sha256=sha)
  pin = row['unmodifiedHistoricalBytes']
  assert pin['path'] == str((HISTORY.parent/'actual-bytes'/path).relative_to(ROOT)) and pin['sha256'] == sha
  exact(pin);archives[path,sha] = pin
 resolutions = []
 def historical_ref(pin):
  p = ROOT/pin['path']
  if p.is_file() and ref(p) == pin:
   refs.append(pin)
   pulse()
   return p
  archive = archives.get((pin['path'],pin['sha256']))
  assert archive is not None, ('unresolved exact historical input',pin)
  p = exact(archive)
  refs.append(archive)
  pulse()
  resolutions.append(dict(originalHistoricalPin=pin,actualArchive=archive,historicalEvidenceOnly=True))
  return p
 for folder,job in [(CONTEXT,'ea33291b60391b28e587650b6d60abc1817a9897650ee59737cea1285d15188f'),
                    (FINITE,'8ea68d031e3c9ff45936804eb6440db7c2fcb4dd6630cf8876578f8522a57dc3')]:
  result = read(folder/'result.json')
  assert result['jobId'] == job and result['newlyInstalled'] == 0
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone() == ('complete',result)
  refs.append(ref(folder/'result.json'))
  for pin in result['evidenceRefs']: historical_ref(pin)
 for name,sha in PINS.items():
  pin = ref(CONTEXT/name)
  assert pin['sha256'] == sha
  refs.append(pin)
 d = read(CONTEXT/'diagnostic.json.gz')
 source = read(CONTEXT/'source-gltf-documents-and-provider-poses.json.gz')
 ground = read(CONTEXT/'complete-ground-facet-provenance.json.gz')
 finite = read(FINITE/'diagnostic.json.gz')
 assert d['uids'] == UIDS and len(source['rows']) == 4
 assert len(d['failureRows']) == 920 and len(d['bodyWorldRows']) == 100
 assert d['completeOriginalBodies'] == 25 and len(d['completeOriginalZeroGlobalFacesRetainedUncredited']) == 150
 assert len(ground['completeActualGroundFaces']) == 3865
 pair = np.asarray(d['completePairOriginalWorld'],float)
 assert pair.shape == (19681,3,3)
 for mode in MODES:
  rows = [r for r in d['failureRows'] if r['mode'] == mode]
  assert len(rows) == 230 and Counter(r['originalBody'] for r in rows) == {19:130,20:16,22:54,23:28,24:2}
  assert Counter(r['fullFiniteProofVerbatim']['orientation'] for r in rows) == {'upward':201,'vertical':24,'downward':5}
  saved = next(r for r in finite['rows'] if r['uid'] == UIDS[1] and r['mode'] == mode)
  assert [r['actorLocalOriginalFace'] for r in rows] == saved['ordinaryUnprovedFaces']
  for r in rows: assert r['fullFiniteProofVerbatim'] == saved['allFaces'][r['actorLocalOriginalFace']]
  assert len([r for r in d['bodyWorldRows'] if r['mode'] == mode]) == 25
 original_rows = [r for r in d['failureRows'] if r['mode'] == 'originalSource']
 assert set(LOW) <= {r['actorLocalOriginalFace'] for r in original_rows if r['originalBody'] == 22}
 # Exact original edge lookup supplies incident face display membership only;
 # it supplies no new contact, connected-body, structural or role certificate.
 edges = defaultdict(set)
 for fi,tri in enumerate(pair[12875:]):
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   edges[tuple(sorted((tuple(a),tuple(b))))].add(fi)
 witnesses = []
 for row in d['failureRows']:
  proof = row['fullFiniteProofVerbatim'].get('rawPairedProofVerbatim',{}).get('sameConstraintOptimizedOrdinaryPrismProof',{})
  for piece in proof.get('allExactFiniteSourceGroundPieces',[]):
   gid = piece['originalGroundFace']
   for point in piece.get('allExactSourcePrismIntersectionVertices',[]):
    witnesses.append(dict(mode=row['mode'],body=row['originalBody'],actorLocalOriginalFace=row['actorLocalOriginalFace'],
      originalGroundFace=gid,savedFiniteVertexVerbatim=point,
      savedGroundProvenanceVerbatim=ground['completeGroundFacetProvenance'][str(gid)],
      witnessIsNotNewClearanceOrRoleProof=True))
 # Snapshot present module versions as a separate before/end byte inventory.
 # None are imported or used to generate/qualify the historical world arrays.
 current_modules = []
 for r in integration['actualHistoricalVersions']:
  if r['originalPath'].endswith('.js'):
   pin = ref(ROOT/r['originalPath']); refs.append(pin); current_modules.append(pin)
 refs = list({(r['path'],r['sha256']):r for r in refs}.values())
 for pin in refs: exact(pin)
 DOC.mkdir(parents=True)
 image_rows = []; sheets = []
 for bid in BODY_IDS:
  pulse(True)
  body = next(r for r in d['bodyWorldRows'] if r['mode'] == 'originalSource' and r['originalBody'] == bid)
  ids = body['completeActorLocalFaces']
  failed = [r['actorLocalOriginalFace'] for r in original_rows if r['originalBody'] == bid]
  incident = set(failed)
  for fi in failed:
   for a,b in zip(pair[12875+fi],np.roll(pair[12875+fi],-1,axis=0)):
    incident.update(edges[tuple(sorted((tuple(a),tuple(b))))])
  assert set(incident) <= set(ids)
  allbody = pair[[12875+i for i in ids]]
  centre = (allbody.min((0,1))+allbody.max((0,1)))/2
  lo = allbody.min((0,1)); hi = allbody.max((0,1)); pad = np.maximum((hi-lo)*.05,[.25,.25,.25])
  bounds = [lo-pad,hi+pad]
  fig = plt.figure(figsize=(26,18),dpi=100)
  view_specs = [('complete-source-body-context',24,-55,True),('isolated-failures-plan',90,-90,False),
                ('isolated-failures-X-Y',0,-90,False),('isolated-failures-Z-Y',0,0,False)]
  for n,(label,elev,azim,full) in enumerate(view_specs,1):
   ax = fig.add_subplot(2,2,n,projection='3d')
   def draw(faceids,color,alpha,lw):
    if faceids: ax.add_collection3d(Poly3DCollection((pair[[12875+i for i in faceids]]-centre)[:,:,[0,2,1]],
       facecolors=color,edgecolors=color,alpha=alpha,linewidths=lw))
   draw(ids if full else sorted(set(incident)-set(failed)),'#6584ad',.12,.22)
   draw([i for i in failed if i not in LOW],'#c72534',.48,.5)
   draw([i for i in failed if i in LOW],'#db9300',.65,.8)
   for mode,color in zip(MODES,['#000000','#8a2be2','#007f66','#de5900']):
    pts = [w['savedFiniteVertexVerbatim']['exactOriginalSourcePoint'] for w in witnesses if w['body']==bid and w['mode']==mode]
    if pts:
     xyz = np.asarray([[float(F(v)) for v in q] for q in pts])-centre
     ax.scatter(xyz[:,0],xyz[:,2],xyz[:,1],s=5,c=color,alpha=.6,label=mode+' saved vertices')
   display = (np.asarray(bounds)-centre)[:,[0,2,1]]
   ax.set_xlim(display[:,0]);ax.set_ylim(display[:,1]);ax.set_zlim(display[:,2]);ax.set_box_aspect(display[1]-display[0]);ax.view_init(elev,azim)
   ax.set_xlabel('X relative to recorded centre X (m)');ax.set_ylabel('Z relative to recorded centre Z (m)');ax.set_zlabel('Y relative to recorded centre Y (m)')
   ax.set_title(label+'; source body '+str(bid)+'; absolute HKPD Y = plotted Y + '+repr(float(centre[1]))+' m')
  fig.suptitle('Unchanged original Sparkle podium body '+str(bid)+' / '+str(len(ids))+' full facets / '+str(len(failed))+' failing facets\n'
   'Red: failed steep candidates; ochre: named 11 low patches; colours are annotations only, no role/function/root claim\n'
   'Complete actor context retained separately; no remote geometry or opaque ground surfaces drawn over these isolated views')
  path = DOC/('podium-body-'+str(bid)+'-isolated-source-witness-sheet-2600x1800.png')
  fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(path);plt.close(fig)
  with Image.open(path) as exported:
   assert exported.size == (2600,1800);exported.verify()
  refs.append(ref(path))
  record = dict(image=ref(path),width=2600,height=1800,originalBody=bid,uid=UIDS[1],
   completeActorLocalFaces=ids,allFailingActorLocalFaces=failed,completeIncidentOriginalFaceIDs=sorted(incident),
   diagnosticCentreOriginalXYZ=centre.tolist(),absoluteCropBounds=[b.tolist() for b in bounds],
   absoluteHKPDYFromPlottedVertical='plotted Y + diagnosticCentreOriginalXYZ[1]',
   views=[v[0] for v in view_specs],noGeometryEdited=True,noRoleRootOrCurrentRuntimeCredit=True)
  image_rows.append(record)
  sheets.append(dict(originalBody=bid,completeSourceBodyVerbatim=body,
   allFourWorldBodyRowsVerbatim=[r for r in d['bodyWorldRows'] if r['originalBody']==bid],
   allFourWorldFailureRowsVerbatim=[r for r in d['failureRows'] if r['originalBody']==bid],
   completeFailureFacetPlaneBindings=[dict(actorLocalOriginalFace=r['actorLocalOriginalFace'],mode=r['mode'],
      origin=r['completeActualWorldFacet'][0],exactUnnormalisedNormal=r['fullFiniteProofVerbatim']['exactUnnormalisedNormal'],
      planeDefinition='n dot (X - origin) = 0; complete facet vertices retained verbatim')
      for r in d['failureRows'] if r['originalBody']==bid],image=record))
  pulse(True)
 save(DOC/'historical-byte-resolution-and-present-module-bindings.json',dict(exactHistoricalResolutions=resolutions,
  integrationContract=ref(INTEGRATION),preHeyaContract=ref(HISTORY),presentModuleVersionsNotUsedAsHistoricalRuntimeProof=current_modules,
  historicalWorldsNotRecaptured=True,currentRuntimeAcceptance=False))
 save(DOC/'isolated-source-witness-inspection.json.gz',dict(uids=UIDS,completeOriginalPairFaces=19681,
  completeOriginalRetainedFaces=40865,completeOriginalBodies=25,completeOriginalZerosRetainedUncredited=d['completeOriginalZeroGlobalFacesRetainedUncredited'],
  full25FourWorldBodyRowsVerbatim=d['bodyWorldRows'],all920FailureRowsVerbatim=d['failureRows'],savedFiniteWitnessesVerbatim=witnesses,
  namedLowPatchIDs=LOW,sheets=sheets,images=image_rows,completeActorContextImagesVerbatim=d['images'],
  sourceGLTFProviderMetadataRef=ref(CONTEXT/'source-gltf-documents-and-provider-poses.json.gz'),
  fullCapturedGroundProvenanceRef=ref(CONTEXT/'complete-ground-facet-provenance.json.gz'),
  noClearanceContactOrRolePredicatesRecomputed=True,noSupportRootNativeOrInstallationCredit=True))
 refs.extend([ref(DOC/'historical-byte-resolution-and-present-module-bindings.json'),
              ref(DOC/'isolated-source-witness-inspection.json.gz')])
 for pin in refs: exact(pin)
 assert ref(manifest)==start
 pulse(True)
 spec=importlib.util.spec_from_file_location('sparkle_isolated_source_views_freezer',FREEZER)
 freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 freezer.freeze(BATCH,'sparkle-isolated-source-failure-witness-views-v1',[exact(r) for r in refs],
   dict(uids=UIDS,completeOriginalBodies=25,completeOriginalSourceZeroFaces=150,completeFailedFaceWorldRows=920,
        completeBodyWorldRows=100,isolatedBodySheets=5,sourceOnly=True,historicalWorldsOnly=True,
        currentRuntimeAcceptance=False,noRoleRootOrNativeAcceptance=True,newlyInstalled=0))

def main():
 if '--owned' in sys.argv: return owned()
 assert not DOC.exists() and not LOCAL.exists()
 resources=['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('sparkle-isolated-source-views-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
 assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),
                 '--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__': main()
