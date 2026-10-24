"""Source-only conditional named visual proposal; never fresh current acceptance."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from cullinan_original_named_visual_details_v1_20261010 import verify,sha,canonical
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-cullinan-west-three-named-original-visual-details-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
ROOTS=[BASE/f'government-xl-terrain-recovery-cullinan-west-literal-ordinary-rendered-root-{i}-v1-20261010'for i in [11,51]]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fixture():
 g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows'];assets=[ROOT/next(r for r in selected if r['uid']==a['uid'])['candidate']['path']for a in g['actors']]
 for asset,a in zip(assets,g['actors']):assert digest(asset.read_bytes())==a['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath);literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position']).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index']).reshape(-1,3)]for a in g['actors']]);f32=literal.astype(np.float32).astype(float)
 roots=[read(p/'diagnostic.json.gz')for p in ROOTS];context=dict(independentLiteralOrdinaryNativeRoots=[11,51],literalRootProofs=roots,providerSourceRootStreams=[source_stream_binding(p.read_bytes())for p in assets],baselineManifestSHA256=read(PROBE/'selection.json.gz')['manifestSHA256'],postMetadataMutationRequiresFreshCurrentCapture=True)
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',PROBE/'result.json',HERE/'cullinan_original_named_visual_details_v1_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py']]
 for p in ROOTS:refs.extend(ref(p/n)for n in ['diagnostic.json.gz','result.json'])
 binding=dict(originalWorldSHA256=sha(original),literalWorldSHA256=sha(literal),float32WorldSHA256=sha(f32),strictGraphSHA256=canonical(g),frozenContextSHA256=canonical(context),originalProviderSourceSHA256s=[a['sourceSHA256']for a in g['actors']])
 return original,literal,f32,g,context,binding,refs

def main():
 assert not DOC.exists()
 for folder in [PROBE,GRAPH,*ROOTS]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 o,l,f,g,c,b,refs=fixture();result=verify(o,l,f,g,frozen_context=c,expected_binding=b,current_binding=b)
 for r in refs:assert ref(ROOT/r['path'])==r
 result.update(uids=[a['uid']for a in g['actors']],evidenceRefs=refs,sourceOnlyFrozenCapturedBaseline=True,postMetadataMutationRequiresFreshCurrentCapture=True,sourceGeometryChanges=0,newlyInstalled=0,publication=False)
 save(DOC/'diagnostic.json.gz',result);spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'source-only-named-cullinan-three-original-visual-detail-proposal-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnlyNamedVisualProposal=True,nativeReacceptance=False,fullAcceptance=False,sourceGeometryChanges=0));print(dict(proposalVerified=True,representations=3,originalVisualParts=3,fullAcceptance=False),flush=True)
if __name__=='__main__':main()
