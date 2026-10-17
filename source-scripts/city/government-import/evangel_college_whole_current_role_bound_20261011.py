"""Current byte-bound complete original Evangel role replay for private staging.

No migration, live write, catalogue mutation or historical-global-hash waiver.
Only the exact old source capture/graph manifest pin resolves to its archive;
all fresh numerical/current/module/source/actor pins remain strict raw bytes.
"""
import copy,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from evangel_college_whole_current_role_policy_20261011 import compose,UID,SOURCE_SHA,GROUND_SHA
from evangel_college_post_elements_current_bound_wing_extension_identity_v3_20261011 import verify_files as verify_identity,source_proposal_pin_path
B=ROOT/'docs/astra-city/government-import'
DOCS={k:B/n for k,n in dict(identity='government-xl-evangel-college-91306-post-elements-current-wing-extension-identity-v2-20261011',source='government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011',finite='government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011',graph='government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011',grade='government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011',qualification='government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011',standing='government-xl-evangel-college-91306-four-standing-current-grade-skin-proposal-v2-20261011',remaining='government-xl-evangel-college-91306-remaining-original-lower-skin-and-two-strip-proposal-v3-20261011',physical='government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011',native='government-xl-evangel-college-91306-all-current6645-native-actual-separation-v1-20261011',domain='government-xl-evangel-college-91306-complete-altered-terrain-domain-native-census-v1-20261011',foreign='government-xl-evangel-college-91306-complete-current16-foreign-basic-context-v2-20261011',native_input='government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011').items()}
MANIFEST_SHA='df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def pin_path(label,pin):return source_proposal_pin_path(pin)if label in {'source','graph'}else ROOT/pin['path']
def verify_files(local):
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==MANIFEST_SHA;current=ref(manifest);receipts={};cache={};allpins=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for label,folder in DOCS.items():
   receipt=read(folder/'result.json');assert receipt['newlyInstalled']==0 and c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   receipts[label]=receipt
   for pin in receipt['evidenceRefs']:
    path=pin_path(label,pin);key=(str(path),pin['sha256'])
    if key not in cache:assert digest(path.read_bytes())==pin['sha256'];cache[key]=True
    allpins.append((path,pin['sha256']))
  assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchone()
  selection=read(DOCS['identity']/'selection.json.gz');assert len(selection['rows'])==1 and selection['manifestSHA256']==MANIFEST_SHA;own=selection['rows'][0];assert own['uid']==UID and own['sourceSHA256']==SOURCE_SHA and own['triangles']==13960
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key)WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,own['native']['cacheKey'])).fetchall()==[(own['native']['resultSha'],)]
 captured=read(DOCS['source']/'complete-current-actual-source-and-ground.json.gz');data=read(DOCS['source']/'complete-four-stream-ground-inputs.json.gz');physical_selection=read(DOCS['physical']/'selection.json.gz');assert len(physical_selection['rows'])==1;physical_own=physical_selection['rows'][0]
 assert captured['uid']==physical_own['uid']==UID and captured['sourceSHA256']==physical_own['sourceSHA256']==SOURCE_SHA
 assert captured['entry']==own['candidate']['entry']==physical_own['candidate']['entry']and next(f for f in captured['completeCurrentForms']if f['uid']==UID)==own['source']['building']
 for p,h in captured['inputHashes'].items():assert digest(source_proposal_pin_path(dict(path=p,sha256=h)).read_bytes())==h
 asset=ROOT/own['candidate']['path'];source=asset.read_bytes();assert digest(source)==SOURCE_SHA and (ROOT/physical_own['candidate']['path']).read_bytes()==source
 original=decode_original_world_triangles(source);assert original.shape==(13960,3,3)and np.array_equal(original,np.asarray(data['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8'))
 catalogue_refs=[ref(ROOT/'3d-viewer'/url)for url in json.loads(before)['officialModelCatalogues']];assert len(catalogue_refs)==215
 entries=[e for p in catalogue_refs for e in read(ROOT/p['path'])['models']];assert len(entries)==len({e['uid']for e in entries})==6645 and UID not in {e['uid']for e in entries}
 composition=read(DOCS['native_input']/'composition.json.gz');assert composition['currentManifest']==current and composition['completeCurrentNativeActors']==6645 and composition['allDeclaredActualLiteralLeftBalancedBoundsComplete']is True and composition['allUnusedPositionVerticesIncluded']is True
 runtime_path=HERE/'local'/DOCS['physical'].name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert len(runtime['rows'])==1;rt=runtime['rows'][0];assert rt['uid']==UID and rt['sourceSHA256']==SOURCE_SHA
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 actual=np.asarray(rt['position'],dtype='<f8').reshape(-1,3)[np.asarray(rt['index'],dtype=np.int64).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 assert np.array_equal(actual,np.asarray(data['completeWorldStreams']['actualLiteral']['completeWorldTriangles'],dtype='<f8'))and ground.shape==(1849,3,3)and digest(ground.tobytes())==GROUND_SHA
 identity=verify_identity(own,read(DOCS['identity']/'context.json.gz')['rows'][0],local/'fresh-current-identity');assert identity==read(DOCS['identity']/'identity.json')
 docs={k:read(p/('proposal.json.gz'if k in {'standing','remaining'}else'diagnostic.json.gz'))for k,p in DOCS.items()if k not in {'source','identity','native_input'}}
 physical=DOCS['physical'];guards={k:read(physical/n)for k,n in dict(metrics='metrics.json',validation='validation.json',foundation='foundation.json',neighbours='neighbour-checks.json',native_checks='native-neighbour-checks.json').items()}
 role=compose(data=data,ground=ground,identity=identity,current_manifest=current,**docs,**guards)
 role.update(exactWholeCurrentSourceFormEntryLoaderTupleBound=True,actualLiteralEqualsCompleteProductionRuntimeExactly=True,completeCurrentActualDrawnGroundFacets=1849,rawMetricTerrainTrianglesRetained=guards['metrics']['rows'][0]['terrainTriangles'],completeCurrentCatalogueRefs=catalogue_refs,independentCompletedProofJobs={k:r['jobId']for k,r in receipts.items()},mathematicalProofsReusedOnlyForIdenticalWholeInputs=True)
 entry=copy.deepcopy(own['candidate']['entry']);assert entry['uid']==UID and entry['sha256']==SOURCE_SHA and not entry.get('supportDependencies')and not entry.get('suppressesBuildingUids')and not entry.get('footprintScope')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[],placementReview='Complete unchanged Evangel College13960 original facets,226 real source components and33 zero-area records retained in all four complete arithmetic streams.216 envelope bodies are connected by exact positive-dimensional original interfaces excluding buried closures, point and zero glue, to genuine actual grade walls with strictly clear original source cap paths.20 horizontal original column-base closures and two sloping original undersides remain separately interpreted lower source skins with their raw132 finite measurements retained. Four independent original standing skins have genuine lateral grade contacts and strict-clear complete original upper perimeter; body90 passes the unchanged ordinary strict footing. Three original roof parts have every authored boundary associated to the qualified envelope within the unchanged .1m band; two original upper strips have lower and side backing with their authored free-upper edge failures retained. All visuals are nonstructural and supply no roots or bridges. The bounded changed authentic-source terrain proposal preserves the independent neighbour old parent; all17 current actors,16 complete actual BASIC collision meshes and6645 actual native source/altered-terrain-domain obligations pass independently. No source reconstruction, geometry/pose/scale change, mechanical function, legal ownership, engineering closed-solid or load-bearing claim.')
 assert manifest.read_bytes()==before and asset.read_bytes()==source
 for p,h in allpins:assert digest(p.read_bytes())==h
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 return role,entry
