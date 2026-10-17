"""Independently test actual native HKDI root parts; no foreign re-acceptance.

Only six genuine complete original footing parts are replayed with literal
current rendered coordinates and actual full ground using production JS math.
Unrooted native parts/A actors remain excluded from structural root credit.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-hkdi-native-and-block-b-complete-original-support-v1'
BATCH='government-xl-terrain-recovery-hkdi-current-native-literal-ground-roots-v3-20261010';DOC=BASE/BATCH
UID='landsd/22089:0';SOURCE='5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40';ROOTS=[134,135,144,156]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def inputs():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);selected=read(PHYS/'selection.json.gz');assert selected['manifestSHA256']==start['sha256']
 for folder in [PHYS,GRAPH]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 g=read(GRAPH/'diagnostic.json.gz');assert g['ordinaryGroundRootComponents']==[134,135,144,147,155,156] and g['newOwnedOriginalBAllComponentsRooted']is True and len(g['newOwnedOriginalBComponents'])==345 and g['everyUninstalledOriginalAContactExcluded']is True and len(g['retainedCurrentNativeUnrootedComponents'])==27
 row=next(r for r in selected['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCE
 matches=[(ROOT/'3d-viewer'/u,e)for u in read(manifest)['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/u)['models']if e['uid']==UID];assert len(matches)==1;catalogue,entry=matches[0];currentasset=catalogue.parent/entry['asset'];assert digest(currentasset.read_bytes())==entry['sha256']==SOURCE
 source=decode_original_world_triangles(raw);runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath);r=next(r for r in runtime['rows']if r['uid']==UID);position=np.asarray(r['position'],float).reshape(-1,3);index=np.asarray(r['index'],np.uint32).reshape(-1,3);actual=position[index];ground=np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3);assert source.shape==actual.shape==(3965,3,3)
 actor=next(a for a in g['actors']if a['uid']==UID);assert actor['originalWorldTrianglesSHA256']==digest(source.tobytes()) and actor['globalFaceRange']==[0,3965]
 data=[]
 for k in ROOTS:
  component=g['components'][k];assert component['actorUID']==UID;faces=component['globalOriginalFaces'];assert len(faces)==len(set(faces)) and all(type(i)is int and 0<=i<3965 for i in faces)
  ids=sorted(set(index[faces].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(ids)};pi=np.asarray([[mapping[int(v)]for v in f]for f in index[faces]],np.uint32);pp=position[ids];assert np.array_equal(pp[pi],actual[faces]);bottom=float(pp[:,1].min())
  data.append(dict(uid=UID,sourceSHA256=SOURCE,manifestSHA256=start['sha256'],component=k,completeLiteralRenderedWorldSHA256=digest(actual.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),part=dict(position=pp.reshape(-1).tolist(),index=pi.reshape(-1).tolist(),bottomHKPD=bottom,component=k,originalFaceIds=faces),terrain=dict(position=ground.reshape(-1).tolist(),index=list(range(ground.size//3)))))
 refs=[ref(p)for p in [Path(__file__),manifest,PHYS/'result.json',PHYS/'selection.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',asset,currentasset,catalogue,runtimepath,HERE/'xl-terrain-recovery-20261010-hkdi-literal-root-finite-readonly-v1.mjs',HERE/'support-interface.mjs',HERE/'support-contact.mjs',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/exact-finite-triangle-projection.js']];assert ref(manifest)==start;return data,refs

def recheck():
 data,refs=inputs();rows=[]
 negative=BASE/'government-xl-terrain-recovery-hkdi-current-native-literal-ground-roots-v1-20261010';receipt=read(negative/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 rejected=[r['component']for r in read(negative/'failed-original-six-literal-root-replay.json')['rows']if r['result']['passed']is False];assert rejected==[147,155]
 refs.extend([ref(negative/'result.json'),ref(negative/'failed-original-six-literal-root-replay.json')])
 for d in data:
  path=DOC/('component-'+str(d['component'])+'-input.json.gz');assert read(path)==d;proof=json.loads(subprocess.check_output(['node',str(HERE/'xl-terrain-recovery-20261010-hkdi-literal-root-finite-readonly-v1.mjs'),str(path)],cwd=ROOT,text=True));assert proof['passed']is True
  rows.append(dict(component=d['component'],completeOriginalFaces=d['part']['originalFaceIds'],literalInput=ref(path),productionJavaScriptSupport=proof));refs.append(ref(path))
 return dict(contract='hkdi-existing-native-four-qualified-literal-finite-genuine-anchor-roots-v3',uids=[UID,'landsd/89613:0'],manifestSHA256=data[0]['manifestSHA256'],strictLiteralRenderedRoots=True,sourceSHA256=SOURCE,rootComponents=ROOTS,rejectedRootComponentsPreserved=[147,155],rows=rows,completeLiteralRenderedWorldSHA256=data[0]['completeLiteralRenderedWorldSHA256'],completeDrawnGroundSHA256=data[0]['completeDrawnGroundSHA256'],arithmeticParityCredit=False,existingNativeReacceptance=False,uninstalledOriginalAExcluded=True,sourceGeometryChanges=0,fullAcceptance=False,publication=False,newlyInstalled=0,evidenceRefs=refs)

def main():
 assert not DOC.exists();data,_=inputs()
 for d in data:save(DOC/('component-'+str(d['component'])+'-input.json.gz'),d)
 r=recheck();save(DOC/'diagnostic.json.gz',r);s=importlib.util.spec_from_file_location('hkdi_literal_roots_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);f.freeze(BATCH,'independent-current-native-four-qualified-literal-rendered-production-js-footings-v2',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=r['uids'],strictLiteralRenderedRoots=True,rootComponents=ROOTS,arithmeticParityCredit=False,existingNativeReacceptance=False,fullAcceptance=False));print(dict(actualRootsPassed=True,roots=ROOTS),flush=True)
if __name__=='__main__':main()
