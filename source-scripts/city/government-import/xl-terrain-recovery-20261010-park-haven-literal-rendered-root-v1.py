"""Independent actual-JavaScript footing replay for Park genuine source root0.

The unchanged production support-interface kernel tests literal rendered vertices
and all literal current drawn ground. No transform-roundoff parity is credited.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-park-haven-v4-complete-original-support-v1'
BATCH='government-xl-terrain-recovery-park-haven-literal-rendered-root-v1-20261010';DOC=BASE/BATCH
UID='landsd/246467:0';SOURCE='de104bedd64810cec4253142280fa27e4c91d4d98807667852ec1073419c840d'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def inputs():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);selected=read(PHYS/'selection.json.gz');assert selected['manifestSHA256']==start['sha256']
 for folder in [PHYS,GRAPH]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 g=read(GRAPH/'diagnostic.json.gz');assert g['ordinaryGroundRootComponents']==[0] and g['supportInterfaceAccepted'] and len(g['resolvedOriginalComponents'])==554
 component=g['components'][0];assert component['actorUID']==UID
 row=next(r for r in selected['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCE
 source=decode_original_world_triangles(raw);runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath);r=next(r for r in runtime['rows']if r['uid']==UID);position=np.asarray(r['position'],float).reshape(-1,3);index=np.asarray(r['index'],np.uint32).reshape(-1,3);actual=position[index];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert source.shape==actual.shape==(636,3,3)
 actor=next(a for a in g['actors']if a['uid']==UID);assert actor['originalWorldTrianglesSHA256']==digest(source.tobytes()) and actor['globalFaceRange']==[0,636]
 faces=component['globalOriginalFaces'];assert len(faces)==len(set(faces)) and all(type(i)is int and 0<=i<636 for i in faces)
 ids=sorted(set(index[faces].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(ids)};partindex=np.asarray([[mapping[int(v)]for v in f]for f in index[faces]],np.uint32);partposition=position[ids];assert np.array_equal(partposition[partindex],actual[faces]);bottom=float(partposition[:,1].min())
 data=dict(uid=UID,sourceSHA256=SOURCE,manifestSHA256=start['sha256'],component=0,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),part=dict(position=partposition.reshape(-1).tolist(),index=partindex.reshape(-1).tolist(),bottomHKPD=bottom,component=0,originalFaceIds=faces),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3))))
 refs=[ref(p)for p in [Path(__file__),manifest,PHYS/'result.json',PHYS/'selection.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',asset,runtimepath,HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs',HERE/'support-interface.mjs']]
 assert ref(manifest)==start;return data,refs

def recheck():
 data,refs=inputs();path=DOC/'component-0-input.json.gz';assert read(path)==data
 proof=json.loads(subprocess.check_output(['node',str(HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'),str(path)],cwd=ROOT,text=True));assert proof['passed']is True
 return dict(contract='park-haven-complete-literal-rendered-root0-unchanged-js-support-interface-v1',uids=[UID,'landsd/320705:0'],manifestSHA256=data['manifestSHA256'],component=0,strictLiteralRenderedRoot=True,sourceSHA256=SOURCE,completeOriginalSourceFaces=636,completeRootOriginalFaces=len(data['part']['originalFaceIds']),completeLiteralRenderedWorldSHA256=data['completeLiteralRenderedWorldSHA256'],completeDrawnGroundSHA256=data['completeDrawnGroundSHA256'],productionJavaScriptSupport=proof,input=ref(path),arithmeticParityCredit=False,sourceGeometryChanges=0,publication=False,newlyInstalled=0,fullAcceptance=False,evidenceRefs=refs+[ref(path)])

def main():
 assert not DOC.exists();data,_=inputs();save(DOC/'component-0-input.json.gz',data);r=recheck();save(DOC/'diagnostic.json.gz',r)
 s=importlib.util.spec_from_file_location('park_literal_root_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);f.freeze(BATCH,'independent-literal-rendered-root0-production-js-footing-v1',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=r['uids'],strictLiteralRenderedRoot=True,arithmeticParityCredit=False,fullAcceptance=False,sourceGeometryChanges=0));print(dict(literalRootPassed=True,faces=r['completeRootOriginalFaces'],proof=r['productionJavaScriptSupport']),flush=True)
if __name__=='__main__':main()
