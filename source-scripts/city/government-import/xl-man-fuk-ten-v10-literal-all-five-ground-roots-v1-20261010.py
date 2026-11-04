"""Independently check all five complete literal roots with production JS.

No source-to-renderer parity is root credit. Complete original source parts
already independently proved roots; every literal part now receives its own
unchanged production support-interface check on its complete drawn ground.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-man-fuk-ten-original-coupled-physical-v3-20261010';GRAPH=BASE/'government-xl-man-fuk-ten-v10-complete-original-support-20261010';BATCH='government-xl-man-fuk-ten-v10-literal-all-five-ground-roots-v1-20261010';DOC=BASE/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
 selection=read(PHYSICAL/'selection.json.gz');assert selection['manifestSHA256']==start['sha256']
 for folder in [PHYSICAL,GRAPH]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 graph=read(GRAPH/'diagnostic.json.gz');assert graph['supportInterfaceAccepted'] and graph['ordinaryGroundRootComponents']==[2,3,4,5,105] and len(graph['resolvedOriginalComponents'])==131
 runtime_path=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';runtime=read(runtime_path)['rows'];helper=HERE/'xl-tung-sing-three-original-footing-readonly-replay-20261010.mjs'
 outputs=[];inputs=[];assets=[]
 for i in graph['ordinaryGroundRootComponents']:
  component=graph['components'][i];uid=component['actorUID'];actor=next(a for a in graph['actors'] if a['uid']==uid);row=next(r for r in selection['rows'] if r['uid']==uid)
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==actor['sourceSHA256'];assets.append(asset)
  source=decode_original_world_triangles(raw);assert digest(source.tobytes())==actor['originalWorldTrianglesSHA256']
  r=next(r for r in runtime if r['uid']==uid);actual=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index'],np.uint32).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3)
  ids=[j-actor['globalFaceRange'][0] for j in component['globalOriginalFaces']];assert all(0<=j<len(actual) for j in ids)
  part=actual[ids];data=dict(uid=uid,sourceSHA256=row['sourceSHA256'],manifestSHA256=start['sha256'],component=i,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),part=dict(position=part.reshape(-1).tolist(),index=list(range(part.size//3)),bottomHKPD=float(part[:,:,1].min()),component=i,originalFaceIds=ids),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3))))
  path=DOC/('component-'+str(i)+'-input.json.gz');save(path,data);inputs.append(path)
  proof=json.loads(subprocess.check_output(['node',str(helper),str(path)],cwd=ROOT,text=True));assert proof['passed'] is True
  outputs.append(dict(uid=uid,component=i,originalFaceIds=ids,input=ref(path),result=proof,strictLiteralRenderedCurrentGroundAnchor=True));print(dict(uid=uid,component=i,passed=True),flush=True)
 refs=[Path(__file__),manifest,PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',runtime_path,helper,HERE/'support-interface.mjs',*inputs,*assets]
 result=dict(rows=outputs,manifestSHA256=start['sha256'],strictAllFiveLiteralRenderedCurrentGroundAnchors=True,arithmeticParityCredit=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',result);assert ref(manifest)==start
 s=importlib.util.spec_from_file_location('literal_roots_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-literal-rendered-all-five-ground-root-support-interfaces-v1',sorted(set(refs)),dict(uids=graph['uids'],strictAllFiveLiteralRenderedCurrentGroundAnchors=True,arithmeticParityCredit=False,sourceGeometryChanges=0,fullAcceptance=False))
if __name__=='__main__':main()
