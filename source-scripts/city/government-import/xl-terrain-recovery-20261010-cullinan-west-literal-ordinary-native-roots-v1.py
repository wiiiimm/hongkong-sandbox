"""Independent actual-JavaScript footing replay for CITIC retained native genuine source root1.

The stricter JS failure is preserved. Independently recreated literal samples
use the unchanged ordinary -.5/1/true +/- .1 anchor kernel on the complete
944-face carrier. No source/runtime arithmetic parity or native reacceptance.
"""
import importlib.util,json,subprocess,argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_ordinary_ground_root_graph_20261009 import verify as ordinary_graph
from xl_source_stream_binding_20261009 import source_stream_binding
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v1-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
parser=argparse.ArgumentParser();parser.add_argument('--component',type=int,choices=[11,51],required=True);args=parser.parse_args();K=args.component
BATCH=f'government-xl-terrain-recovery-cullinan-west-literal-ordinary-rendered-root-{K}-v1-20261010';DOC=BASE/BATCH
UID='landsd/262871:0';SOURCE='e98936729981df7e618478258f486ff5faaa98fcfa57937b2d3f5a11dc2277f8'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def inputs():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);selected=read(PHYS/'selection.json.gz');assert selected['manifestSHA256']==start['sha256']
 for folder in [PHYS,GRAPH]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 g=read(GRAPH/'diagnostic.json.gz');assert g['ordinaryGroundRootComponents']==[11,51] and not g['supportInterfaceAccepted'] and len(g['components'])==296 and next(p for p in g['ordinaryRootProofs']if p['component']==K)['accepted']is True
 component=g['components'][K];assert component['actorUID']==UID
 row=next(r for r in selected['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCE
 source=decode_original_world_triangles(raw);runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath);r=next(r for r in runtime['rows']if r['uid']==UID);position=np.asarray(r['position'],float).reshape(-1,3);index=np.asarray(r['index'],np.uint32).reshape(-1,3);actual=position[index];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert source.shape==actual.shape==(132291,3,3)
 actor=next(a for a in g['actors']if a['uid']==UID);assert actor['originalWorldTrianglesSHA256']==digest(source.tobytes()) and actor['globalFaceRange']==[0,132291]
 faces=component['globalOriginalFaces'];assert len(faces)==len(set(faces)) and all(type(i)is int and 0<=i<132291 for i in faces)
 ids=sorted(set(index[faces].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(ids)};partindex=np.asarray([[mapping[int(v)]for v in f]for f in index[faces]],np.uint32);partposition=position[ids];assert np.array_equal(partposition[partindex],actual[faces]);bottom=float(partposition[:,1].min())
 data=dict(uid=UID,sourceSHA256=SOURCE,manifestSHA256=start['sha256'],component=K,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),part=dict(position=partposition.reshape(-1).tolist(),index=partindex.reshape(-1).tolist(),bottomHKPD=bottom,component=K,originalFaceIds=faces),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3))))
 refs=[ref(p)for p in [Path(__file__),manifest,PHYS/'result.json',PHYS/'selection.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',asset,runtimepath,HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs',HERE/'support-interface.mjs']]
 assert ref(manifest)==start;return data,refs

def recheck():
 data,refs=inputs();path=DOC/f'component-{K}-input.json.gz';assert read(path)==data
 strictproof=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(path)],cwd=ROOT,text=True))
 part=data['part'];position=np.asarray(part['position'],float).reshape(-1,3);index=np.asarray(part['index'],np.uint32).reshape(-1,3);literal=position[index];ground=np.asarray(data['terrain']['position'],float).reshape(-1,3,3);n=len(literal);assert n=={11:24,51:49}[K]
 raw=(ROOT/next(x for x in read(PHYS/'selection.json.gz')['rows']if x['uid']==UID)['candidate']['path']).read_bytes();assert digest(raw)==SOURCE
 indexed=[dict(uid=UID,sourceSHA256=SOURCE,position=position.reshape(-1).tolist(),index=index.reshape(-1).tolist())];binding=dict(completeOriginalWorldTrianglesSHA256=digest(literal.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(path)['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=digest(json.dumps(indexed,sort_keys=True,separators=(',',':')).encode()))
 actors=[dict(uid=UID,sourceSHA256=SOURCE,globalFaceRange=[0,n],completeOriginalFaceCount=n,originalWorldTrianglesSHA256=digest(literal.tobytes()),originalStreamBindingSHA256=digest(json.dumps(source_stream_binding(raw),sort_keys=True,separators=(',',':')).encode()))];components=[dict(actorUID=UID,globalOriginalFaces=list(range(n)))];proof=ordinary_graph(literal,actors,components,[],indexed,ground,expected_binding=binding,current_binding=binding);assert proof['ordinaryGroundRootComponents']==[0] and proof['supportInterfaceAccepted']
 refs.extend(ref(HERE/x)for x in ['original_ordinary_ground_root_graph_20261009.py','original_ordinary_rim_accounting_20261009.py','original_wall_rim_accounting_20261009.py','original_multi_actor_support_graph_20261009.py','exact_original_shell_intersections_20261009.py','xl_source_stream_binding_20261009.py'])
 return dict(contract='cullinan-bounded-complete-native-ordinary-root-literal-existing-samples-v1',uids=[UID,'landsd/161931:0','landsd/120158:0'],manifestSHA256=data['manifestSHA256'],component=K,ordinaryLiteralSampleRootVerified=True,strictLiteralRenderedRoot=strictproof['passed'],nativeReacceptance=False,unresolvedOriginalGraphNegativesPreserved=True,sourceSHA256=SOURCE,completeOriginalSourceFaces=132291,completeRootOriginalFaces=len(data['part']['originalFaceIds']),completeLiteralRenderedWorldSHA256=data['completeLiteralRenderedWorldSHA256'],completeDrawnGroundSHA256=data['completeDrawnGroundSHA256'],rawProductionJavaScriptStrictSupportVerbatim=strictproof,independentLiteralOrdinarySamples=proof,literalSamplesIndependentlyRecreated=True,originalSourceTopologyAuthority=ref(GRAPH/'diagnostic.json.gz'),completePartOriginalFaceMembership=data['part']['originalFaceIds'],input=ref(path),arithmeticParityCredit=False,sourceGeometryChanges=0,publication=False,newlyInstalled=0,fullAcceptance=False,evidenceRefs=refs+[ref(path)])

def main():
 assert not DOC.exists();data,_=inputs();save(DOC/f'component-{K}-input.json.gz',data);r=recheck();save(DOC/'diagnostic.json.gz',r)
 s=importlib.util.spec_from_file_location('park_literal_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);f.freeze(BATCH,'independent-complete-native-ordinary-root-literal-existing-sample-v1',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=r['uids'],ordinaryLiteralSampleRootVerified=True,rawStrictJavaScriptFailuresPreserved=True,arithmeticParityCredit=False,fullAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0));print(dict(literalRootPassed=True,faces=r['completeRootOriginalFaces'],strictJavaScriptPassed=r['rawProductionJavaScriptStrictSupportVerbatim']['passed'],ordinarySamples=r['independentLiteralOrdinarySamples']['ordinaryRootProofs'][0]['ordinaryRim']),flush=True)
if __name__=='__main__':main()
