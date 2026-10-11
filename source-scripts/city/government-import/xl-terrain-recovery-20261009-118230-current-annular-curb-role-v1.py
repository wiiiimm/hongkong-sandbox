"""Source-specific original curb role, independently pinned current whole physics.

No structural root/bridge or installation credit. Complete provider/source and
current actor scope are independently read, rather than caller-declared labels.
"""
import importlib.util,json,uuid,collections
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations,connect
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_open_annular_curb_accounting_20261009 import verify,canonical
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261009-118230-current-annular-curb-role-v1';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
CONTEXT=BASE/'xl-terrain-recovery-20261009-118230-boundary-current-complete-context-v3/diagnostic.json.gz'
PROVIDER=BASE/'xl-terrain-recovery-20261009-118230-provider-source-inventory-v2'
CAP=BASE/'xl-terrain-recovery-20261009-118230-current-cap-paths-v1'
SOURCE='0e9740f9b9b3061aa4f4bbe26b397db58f870476aa0716745339e505a79c51ff'
UID='landsd/118230:0'
PART=[17702,17703,17704,17705,17708,17709,17710,17711,17712,17713,17714,17715,17716,17717,17718,17719,17720,17721,17722,17723,17724,17725,17726,17727,17728,17729,17730,17731,17732,17733,17734,17735,17736,17737,17738,17739,17842,17843,17844,17845,17846,17847,17848,17849,17850,17851,17852,17853,17854,17855,17856,17857,17858,17859]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def receipt(p):
 r=read(p/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for item in r['evidenceRefs']:assert ref(ROOT/item['path'])==item
 return r
def original_component(tri,seed):
 edges=collections.defaultdict(list)
 for i,face in enumerate(tri):
  for a,b in zip(face,np.roll(face,-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 seen={seed};todo=[seed]
 while todo:
  i=todo.pop()
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   for j in edges[tuple(sorted((tuple(a),tuple(b))))]:
    if j not in seen:seen.add(j);todo.append(j)
 return sorted(seen)
def recheck():
 physical=receipt(PHYSICAL);provider=receipt(PROVIDER);cap_receipt=receipt(CAP)
 selected=read(PHYSICAL/'selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0]
 assert row['uid']==UID and row['sourceSHA256']==SOURCE and row['native']['model']['modelId']=='B378291822401063C0'
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 role=read(PROVIDER/'expected-role.json');assert role['uid']==UID and role['sourceSHA256']==SOURCE and role['originalFaceCount']==19438 and role['lowAncillaryCompleteOriginalFaces']==PART
 streams=source_stream_binding(raw);assert streams==role['providerExteriorProvenanceBinding']['exactPackedSourceStreams']
 provenance=read(PROVIDER/'original-source-provenance.json')
 for item in provenance['evidenceRefs']:assert ref(ROOT/item['path'])==item
 tri=decode_original_world_triangles(raw);assert len(tri)==19438 and original_component(tri,PART[0])==PART,'Incomplete authored source component'
 ctx=read(CONTEXT);geom=read(GEOMETRY);g=geom['rows'][0];world=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert g['uid']==ctx['uid']==UID and g['sourceSHA256']==ctx['sourceSHA256']==SOURCE and world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
 assert ctx['wholeSourceFaces']==19438 and ctx['wholeSourceUncoveredFaces']==0 and not ctx['otherAffectedFaces']
 assert ctx['originalOpenExteriorPaths']['sourceAndPhysicalBindings']['decodedWorldTrianglesSHA256']==digest(world.tobytes())
 for path,sha in geom['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']
 f=read(PHYSICAL/'foundation.json')['rows'][0];assert f['uid']==UID and f['sourceSHA256']==SOURCE and f['strictFoundationAccepted'] is True
 assert f['foundation']['triangles']==f['foundation']['completeTerrainTriangles']==19438 and f['foundation']['fullyBuriedTriangles']==f['foundation']['fullyBuriedUpwardTriangles']==0
 checks=read(PHYSICAL/'neighbour-checks.json');assert all(not r['reasons'] for r in checks['rows'])
 native_checks=read(PHYSICAL/'native-neighbour-checks.json');assert not(set(native_checks['blocked'])-set(native_checks['resolved'])) and all(r['passed'] for r in native_checks['rows'])
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');assert set(neighbours['candidateIds'])=={UID} and len(neighbours['rows'])==len(checks['rows'])==3
 forms={}
 for path,sha in neighbours['inputHashes'].items():
  assert digest((ROOT/path).read_bytes())==sha;forms.update({f['uid']:f for f in read(ROOT/path)['buildings']})
 projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in tri[PART]])
 actors=[]
 for nr in neighbours['rows']:
  form=nr['building'];assert forms[form['uid']]==form
  if form['uid']==UID:continue
  assert not nr['existingNative'] and not form.get('modelGeometry'),'Actual foreign native/embedded mesh export required'
  rings=form['rings'];p=shapely.Polygon(rings[0],rings[1:]);assert p.is_valid and projection.disjoint(p),'Original curb touches foreign current form'
  actors.append(dict(uid=form['uid'],completeCurrentFormSHA256=canonical(form),completeCurrentFootprintSHA256=digest(p.wkb),sourceProjectionDistanceM=float(projection.distance(p))))
 catalogues=[];native_bounds=[]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for e in read(p)['models']:
   bounds=np.asarray(e['worldBounds'],float);assert bounds.shape==(2,3) and np.isfinite(bounds).all() and (bounds[1]>=bounds[0]).all() and e['sha256']
   assert projection.disjoint(shapely.box(bounds[0,0],bounds[0,2],bounds[1,0],bounds[1,2])),'Actual complete native export required on overlapping bounds'
   native_bounds.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalBounds=e['worldBounds']))
 binding=dict(sourceSHA256=SOURCE,completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx['faces']),completeOriginalPartFacesSHA256=canonical(PART),completeRenderedWorldTrianglesSHA256=digest(world.tobytes()),currentPhysicalSHA256=digest((PHYSICAL/'result.json').read_bytes()),currentManifestSHA256=digest(manifest.read_bytes()),currentSourceProvenanceSHA256=digest((PROVIDER/'expected-role.json').read_bytes()),currentNeighbourScopeSHA256=digest((PHYSICAL/'neighbour-inputs.json.gz').read_bytes()),allNativeOriginalBoundsSHA256=canonical(native_bounds))
 typed=verify(tri,ctx['faces'],PART,ground,expected_binding=binding,current_binding=binding)
 refs=[ref(p) for p in [Path(__file__),asset,CONTEXT,GEOMETRY,manifest,PROVIDER/'expected-role.json',PROVIDER/'original-source-provenance.json',PROVIDER/'result.json',CAP/'result.json',CAP/'diagnostic.json.gz',PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'foundation.json',PHYSICAL/'neighbour-inputs.json.gz',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',HERE/'original_open_annular_curb_accounting_20261009.py',HERE/'test_original_open_annular_curb_accounting_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']]+catalogues+provenance['evidenceRefs']
 typed.update(uid=UID,sourceSHA256=SOURCE,binding=binding,completeOriginalSourceFaceCount=19438,completeActualSourceComponentMembershipVerified=True,providerSourceRootStreams=streams,sourceRenderedMaximumRoundoffM=float(np.max(np.abs(world-tri))),completeCurrentForeignActors=actors,allCurrentNativeCompleteBoundsChecked=len(native_bounds),rawPhysicalReasonsPreserved=physical['reasons'],currentStrictWholeFoundationPassed=True,currentAllNeighbourChecksPassed=True,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']))
 return typed
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-current-curb-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str))
 try:
  proof=recheck();save(DOC/'typed-role.json.gz',proof)
  spec=importlib.util.spec_from_file_location('curb_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.freeze(BATCH,'source-specific-current-original-annular-curb-visual-role-v1',[ROOT/r['path'] for r in proof['evidenceRefs']],dict(uids=[UID],sourceSHA256=SOURCE,originalLowExteriorRoleVerified=True,structuralRootCredit=False,maySupportOtherComponents=False,originalPartFaceCount=54,affectedOriginalWallFaces=proof['affectedOriginalWallFaces'],rawPhysicalReasonsPreserved=proof['rawPhysicalReasonsPreserved'],fullAcceptance=False,installationApproved=False,nextStep='Complete independently anchored original body/component graph, unchanged runtime/full physical acceptance, staged/live browser and guarded publication.'))
  print(json.dumps(dict(originalPartFaces=54,affectedWallFaces=proof['affectedOriginalWallFaces'],exactGradeInterfaces=len(proof['exactActualGradeInterfaces']),structuralRootCredit=False,fullAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
