"""Exact whole credited-component edge census; no historical vertex-group acceptance."""
import importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_original_shared_edge_component_census_20261011 import census
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-cullinan-west-credited-complete-shared-edge-census-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows'];runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(runtimepath);assets=[ROOT/r['candidate']['path']for r in selected]
 for r,p in zip(selected,assets):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']]);assert original.shape==literal.shape==(154603,3,3)and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 ids=[i for i,c in enumerate(g['components'])if c['actorUID']!='landsd/262871:0' or i in [0,25,51]];assert len(ids)==35;rows=[]
 for mode,t in [('providerOriginal',original),('actualLiteral',literal)]:
  results=[]
  for i in ids:
   faces=g['components'][i]['globalOriginalFaces'];proof=census(t,faces);results.append(dict(historicalVertexComponent=i,actorUID=g['components'][i]['actorUID'],completeOriginalFaces=len(faces),sharedEdgeProof=proof));print(dict(mode=mode,historicalComponent=i,completeFaces=len(faces),exactEdgeComponents=len(proof['sharedEdgeConnectedComponents'])),flush=True)
  assert sum(r['completeOriginalFaces']for r in results)==129544
  rows.append(dict(mode=mode,completeWorldSHA256=digest(t.tobytes()),allCreditedOriginalFaces=129544,rows=results,splitHistoricalComponents=[dict(historicalComponent=r['historicalVertexComponent'],edgeComponents=len(r['sharedEdgeProof']['sharedEdgeConnectedComponents']))for r in results if len(r['sharedEdgeProof']['sharedEdgeConnectedComponents'])>1]))
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,PROBE/'selection.json.gz',PROBE/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',HERE/'exact_original_shared_edge_component_census_20261011.py',HERE/'test_exact_original_shared_edge_component_census_20261011.py',HERE/'exact_packed_world_geometry_20261009.py']]
 for p in [PROBE,GRAPH]:
  receipt=read(p/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 result=dict(uids=[r['uid']for r in selected],rows=rows,historicalVertexComponentsRetained=True,pointOnlyStructuralCredit=False,fullAcceptance=False,diagnosticOnly=True,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-literal-credited-cullinan-exact-shared-edge-census-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],completeCreditedFaces=129544,splitHistoricalComponents={r['mode']:r['splitHistoricalComponents']for r in rows},nativeReacceptance=False,fullAcceptance=False))
if __name__=='__main__':main()
