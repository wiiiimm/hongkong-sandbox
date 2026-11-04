"""Pin complete original provider streams and named visual interfaces before acceptance."""
import collections,importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from festival_original_named_visual_mount_roles_v1_20261010 import WORLD,SOURCES,FACADE,ROOF,BACK_OUTER_FACES,canonical
BATCH='xl-terrain-recovery-20261010-festival-complete-original-provider-visual-mount-roles-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-festival-pair-finite-sampler-current-original-support-v4';PHYS=BASE/'government-xl-terrain-recovery-festival-pair-finite-sampler-current-v4-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');receipt=read(GRAPH/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 rs=read(PHYS/'selection.json.gz')['rows'];assets=[ROOT/r['candidate']['path'] for r in rs];assert {r['uid']:r['sourceSHA256'] for r in rs}==SOURCES
 for r,a in zip(rs,assets):assert digest(a.read_bytes())==r['sourceSHA256']
 tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==WORLD==g['binding']['completeOriginalWorldTrianglesSHA256'];roles=[]
 for k in sorted(FACADE+ROOF+[219]):
  ids=g['components'][k]['globalOriginalFaces'];edges=collections.defaultdict(list)
  for i in ids:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
  boundary=[e for e,v in sorted(edges.items()) if len(v)==1]
  if k in FACADE:kind='named-original-facade-sign-complete-open-boundary';chosen=boundary
  elif k in ROOF:kind='named-original-roof-rail-or-trim-complete-lowest-edges';low=tri[ids,:,1].min();chosen=[e for e in sorted(edges) if e[0][1]==e[1][1]==low]
  else:kind='named-original-extruded-glyph-complete-outer-back-opening';chosen=[e for e in boundary if edges[e][0] in BACK_OUTER_FACES]
  roles.append(dict(component=k,kind=kind,actorUID=g['components'][k]['actorUID'],completeOriginalFaces=ids,completeOriginalPartSHA256=digest(tri[ids].tobytes()),completeOriginalMountEdges=[[list(v) for v in e] for e in chosen],completeOriginalGeometricBoundary=[[list(v) for v in e] for e in boundary],sourceRoleInterpretation='Named original non-load-bearing facade sign glyph' if k in FACADE+[219] else 'Named original roof rail or roof-edge trim visual detail',noClosedSolidClaim=True,noStructuralRootOrBridgeCredit=True))
 provider=dict(contract='festival-original-sign-rails-trim-complete-visual-mount-roles-v1',sourceSHA256s=SOURCES,completeOriginalWorldSHA256=WORLD,completeOriginalActors=g['actors'],completeOriginalComponentsSHA256=canonical(g['components']),completeOriginalProviderRootAndStreams={r['uid']:source_stream_binding(p.read_bytes()) for r,p in zip(rs,assets)},roles=roles,sourceGeometryChanges=0,rawStructuralFailuresRetained=True,sourceRoleInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False)
 save(DOC/'provider-role.json.gz',provider);refs=[ref(p) for p in [Path(__file__),GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PHYS/'selection.json.gz',*assets,HERE/'festival_original_named_visual_mount_roles_v1_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py']]
 sp=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.freeze(BATCH,'complete-provider-original-source-named-48-visual-interface-role-pins-v1',[ROOT/r['path'] for r in refs],dict(uids=sorted(SOURCES),sourceGeometryChanges=0,completeOriginalFaces=35006,namedVisualInterfaces=48,providerRole=ref(DOC/'provider-role.json.gz'),visualRolesVerified=False,structuralRootCredit=False,installationApproved=False))
if __name__=='__main__':main()
