"""Complete owned component path proof through only the actually qualified native chain.

Retained90 native unresolved parts remain unchanged. Three named visual parts
provide no root/bridge. Every credited interface recomputed in original/literal.
"""
import importlib.util,collections
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-cullinan-west-complete-owned-current-carrier-paths-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1';EXPOSURE=BASE/'xl-terrain-recovery-20261011-cullinan-west-current-carrier-interface-exposure-v1';ROOTPROOF=BASE/'government-xl-terrain-recovery-cullinan-west-literal-ordinary-rendered-root-51-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROBE,GRAPH,EXPOSURE,ROOTPROOF]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.extend(ref(folder/n)for n in ['result.json', 'diagnostic.json.gz'] if(folder/n).exists())
 g=read(GRAPH/'diagnostic.json.gz');e=read(EXPOSURE/'diagnostic.json.gz');root=read(ROOTPROOF/'diagnostic.json.gz');assert root['component']==51 and root['ordinaryLiteralSampleRootVerified'] and not root['nativeReacceptance'];assert all(r['allWholePositiveInterfacesStrictlyExposed']for r in e['rows'])
 selection=read(PROBE/'selection.json.gz');assets=[ROOT/r['candidate']['path']for r in selection['rows']];runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(runtimepath);o=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);l=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']]);assert o.shape==l.shape==(154603,3,3);assert digest(o.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 for r,p in zip(selection['rows'],assets):assert digest(p.read_bytes())==r['sourceSHA256']
 visual={270,294,295};owned={i for i,c in enumerate(g['components'])if c['actorUID']!='landsd/262871:0'};assert len(owned)==32;allowed=(owned-visual)|{0,25,51};adj={i:set()for i in allowed};pairs={}
 for contact in g['contactWitnesses']:
  a,b=contact['components']
  if a in allowed and b in allowed:adj[a].add(b);adj[b].add(a);pairs[tuple(sorted([a,b]))]=contact
 parents={51:None};queue=collections.deque([51])
 while queue:
  a=queue.popleft()
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;queue.append(b)
 assert set(parents)==allowed,'Every nonvisual owned component must reach genuine native51 without any other native actor/component'
 paths=[]
 for child,parent in sorted(parents.items()):
  if parent is None:continue
  contact=pairs[tuple(sorted([child,parent]))];a,b=contact['globalOriginalFaces'];assert {next(i for i,c in enumerate(g['components'])if a in c['globalOriginalFaces']),next(i for i,c in enumerate(g['components'])if b in c['globalOriginalFaces'])}==set(contact['components']);modes=[]
  for name,t in [('providerOriginal',o),('actualLiteral',l)]:
   ps=intersection_points(rational_face(t[a]),rational_face(t[b]));assert len(ps)>=2,'No rounded/welded source contact credit';modes.append(dict(mode=name,exactPositiveInterfacePoints=[[str(x)for x in p]for p in ps]))
  if any(i in {0,25,51}for i in contact['components']):
   assert any(r['originalContact']['components']==contact['components']for r in e['rows'][0]['interfaces']),'Every credited native edge requires independent finite exposure proof'
  paths.append(dict(child=child,parent=parent,components=contact['components'],globalOriginalFaces=[a,b],independentSourceAndLiteralContacts=modes))
 refs.extend(ref(p)for p in [*assets,runtimepath,PROBE/'selection.json.gz',GRAPH/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'])
 result=dict(uids=[r['uid']for r in selection['rows']],completeOriginalWorldSHA256=digest(o.tobytes()),completeLiteralWorldSHA256=digest(l.tobytes()),completeOriginalFaces=154603,completeOriginalComponents=296,completeOwnedComponents=32,independentlySupportedOwnedStructuralComponents=sorted(owned-visual),conditionallyNonstructuralOriginalVisualComponents=sorted(visual),completeCreditedNativeComponents=[0,25,51],actualGroundRoot=51,completeOwnedParents=parents,completeQualifiedPositivePaths=paths,allOwnedStructuralComponentsReached=True,all90NativeUnresolvedComponentsPreserved=[i for i,c in enumerate(g['components'])if c['actorUID']=='landsd/262871:0'and i not in g['resolvedOriginalComponents']],addedRoots=[],addedBridges=[],nativeReacceptance=False,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-owned-current-original-literal-qualified-exposed-native-carrier-paths-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],allOwnedStructuralComponentsReached=True,completeOwnedStructuralComponents=len(owned-visual),visualComponents=sorted(visual),nativeReacceptance=False,fullAcceptance=False))
 print(dict(completePaths=len(paths),ownedStructuralComponents=len(owned-visual),nativeComponents=[0,25,51],nativeReacceptance=False),flush=True)
if __name__=='__main__':main()
