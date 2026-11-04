"""Prove all78 complete original/runtime ledge shapes; full acceptance withheld."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from mei_yat_original_named_visual_mounts_v1_20261010 import verify,canonical,DETAILS,PANELS,LEDGES,WORLD,ACTUAL,SOURCE
BATCH='xl-terrain-recovery-20261010-mei-yat-all-named-original-visual-mounts-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;assert not DOC.exists()
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010';SUP=BASE/'xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1';FINITE=BASE/'xl-terrain-recovery-20261010-mei-yat-complete-paired-column-v1';EDGE=BASE/'xl-terrain-recovery-20261010-mei-yat-all-boundary-euclidean-diagnostic-v1';g=read(SUP/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz')['rows'][0];refs=[]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
for folder in [PHYS,SUP,FINITE,EDGE]:
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs.append(ref(folder/'result.json'))
r=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());runtime=read(HERE/'local'/PHYS.name/'runtime-geometry.json.gz')['rows'][0];world=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
assert finite['completeOriginalWorldSHA256']==digest(t.tobytes()) and finite['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and finite['completeGroundSHA256']==digest(ground.tobytes());assert not finite['unprovedOriginalFaces'] and not finite['unprovedActualRenderedFaces'];assert g['binding']['completeOriginalWorldTrianglesSHA256']==digest(t.tobytes())
roles=[]
for k in DETAILS:
 kind=('original-eight-face-open-ended-facade-ledge' if k in LEDGES else 'original-projecting-panel-complete-mounted-front-facets' if k in [76,77] else 'original-panel-two-complete-mounted-open-boundaries' if k in PANELS else 'original-complete-corner-trim-and-two-open-ended-ledges')
 roles.append(dict(component=k,kind=kind,completeOriginalFaces=g['components'][k]['globalOriginalFaces']))
provider=dict(contract='mei-yat-authored-panels-open-ended-ledges-and-corner-trim-visual-only-v1',sourceSHA256=SOURCE,completeOriginalWorldSHA256=WORLD,roles=roles,interpretation='AI-assisted interpretation of unchanged exact provider geometry and source renders, conditional only. No structural root/bridge/closed solid; complete original and literal finite mounts plus every independent current gate mandatory.',visualRoleAccepted=False,structuralRootCredit=False,fullAcceptance=False)
save(DOC/'conditional-provider-roles.json',provider)
finite_full=read(FINITE/'diagnostic.json.gz')
binding=dict(completeOriginalWorldSHA256=WORLD,completeLiteralWorldSHA256=ACTUAL,completeGraphSHA256=canonical(g),completeFiniteContextsSHA256=canonical(finite_full),providerRolesSHA256=canonical(provider))
proof=verify(t,world,g,finite_full,provider,expected_binding=binding,current_binding=binding)
save(DOC/'conditional-typed-mounts.json.gz',proof)
print('ALL121 original/literal named visual mounts PASS; fullAcceptance remains false',flush=True)
refs += [ref(p) for p in [Path(__file__),asset,PHYS/'selection.json.gz',SUP/'diagnostic.json.gz',FINITE/'diagnostic.json.gz',EDGE/'diagnostic.json.gz',HERE/'local'/PHYS.name/'runtime-geometry.json.gz',HERE/'mei_yat_original_named_visual_mounts_v1_20261010.py',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'test_exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'mei_yat_original_open_ended_ledge_geometry_v2_20261010.py',HERE/'test_mei_yat_original_open_ended_ledge_geometry_v2_20261010.py',HERE/'mei_yat_original_open_ended_ledge_geometry_20261010.py',HERE/'test_mei_yat_original_open_ended_ledge_geometry_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
save(DOC/'diagnostic.json.gz',dict(uids=[r['uid']],sourceSHA256=SOURCE,completeOriginalWorldSHA256=WORLD,completeLiteralRenderedWorldSHA256=ACTUAL,completeCurrentGroundSHA256=digest(ground.tobytes()),sourceGeometryChanges=0,conditionalCompleteNamedVisualMounts=121,conditionalTypedProof=proof,stillStructurallyUnrootedComponents=DETAILS,visualRoleAccepted=False,structuralRootCredit=False,fullAcceptance=False,evidenceRefs=refs))
spec=importlib.util.spec_from_file_location('visual_mount_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete121original-rendered-source-specific-visual-mounts-conditional-v1',[ROOT/p['path'] for p in refs],dict(uids=[r['uid']],conditionalCompleteNamedVisualMounts=121,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,fullAcceptance=False))
