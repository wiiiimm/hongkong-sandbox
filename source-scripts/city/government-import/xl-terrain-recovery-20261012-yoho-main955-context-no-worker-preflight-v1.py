"""Offline saved schema/hash checks only: no imports of the caller or geometry."""
from pathlib import Path
import ast,gzip,hashlib,json

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import'
REVIEW=BASE/'government-xl-yoho-main955-ground-residual-context-method-draft-20261012'
CALLER=HERE/'xl-terrain-recovery-20261012-yoho-main955-ground-residual-context-v1.py'
METHOD=REVIEW/'METHOD.md'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/146396:0','landsd/231756:0']
MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(p):
 q=ROOT/p['path'];assert q.is_file()and ref(q)==p,p
 return q
def main():
 ast.parse(CALLER.read_text());ast.parse(Path(__file__).read_text())
 folders=[BASE/('xl-terrain-recovery-20261012-'+n)for n in ['yoho-eight-original-pair-current-capture-v1','yoho-eight-original-pair-current-attributes-v1','yoho-eight-pair-four-stream-finite-edge-interfaces-v1']]
 jobs=[('6da18fbe3cb5a91c8fa1b24e5f9f6b8ed378eb09607299e0b8aeca4ec3691a1e','778c6658ea3eced67f90fdbc5d02bcef631def48d509e57e896e1bcddc99dd06'),('368ed4a50d83f7912ee585334877d163f1740d25d271015c551832844786198d','659f67cb25797fa6b4063826bd5098ef6ba85eecb00bc6d728ff9440b0424e9c'),('693e02926f1181b890f4fb2adb46b0c030ee2e604e585931c8c56f02ca0461b2','ba62d8c36b91fc070a881fae8d7a759f76bf00f349b2ebc522a1f1675c3bd3dc')]
 pins=[ref(CALLER),ref(METHOD),ref(Path(__file__))];count=0
 for folder,(job,sha)in zip(folders,jobs):
  r=read(folder/'result.json');assert r['jobId']==job and ref(folder/'result.json')['sha256']==sha and r['newlyInstalled']==0
  for p in r['evidenceRefs']:check(p);count+=1
  pins.append(ref(folder/'result.json'))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==CURRENT;pins.append(ref(manifest))
 selection=read(folders[0]/'selection.json.gz')['rows'];runtime=read(HERE/'local'/folders[0].name/'runtime-geometry.json.gz')['rows'];attrs=read(folders[1]/'actual-render-attributes.json.gz')
 assert [r['uid']for r in selection]==[r['uid']for r in runtime]==UIDS
 assert [r['triangles']for r in selection]==[14792,7731]
 for r in selection:
  assert 'entry'in r['candidate']and 'completeOriginalPOSITIONProof'in r
  assert ref(ROOT/r['candidate']['path'])['sha256']==r['sourceSHA256']
 d=read(folders[2]/'diagnostic.json.gz');assert d['completeOriginalFaces']==22523 and [r['mode']for r in d['interfaceRows']]==MODES
 b=d['interfaceRows'][0]['bodies'];assert len(b)==1068 and b[955]['uid']==UIDS[1]and len(b[955]['globalOriginalFaces'])==4019 and b[135]['uid']==UIDS[0]and len(b[135]['globalOriginalFaces'])==2084
 ids=[i for r in b for i in r['globalOriginalFaces']];assert sorted(ids)==list(range(22523))
 sets=[];failed=[]
 for g in d['interfaceRows']:
  assert [(r['uid'],r['globalOriginalFaces'])for r in g['bodies']]==[(r['uid'],r['globalOriginalFaces'])for r in b]
  pairs=g['onePositiveDimensionalWitnessPerContactingBodyPair'];sets.append({tuple(p['bodies'])for p in pairs})
  cross=[p for p in pairs if b[p['bodies'][0]]['uid']!=b[p['bodies'][1]]['uid']]
  assert len(cross)==1 and cross[0]['bodies']==[135,955]and cross[0]['globalOriginalFaces']==[11323,21253]
  for uid,i in [(UIDS[0],11323),(UIDS[1],6461)]:
   f=next(x for x in d['finiteRows']if x['uid']==uid and x['mode']==g['mode']);face=f['allFaces'][i]
   assert face['sourceFace']==i and face['groundProjectionCovered']and face['ordinaryBoundProved']and isinstance(face['finalFiniteProof'],dict)
 assert len(sets[0]-sets[1])==67 and not sets[1]-sets[0]and len(set.intersection(*sets))==1288
 assert len(d['finiteRows'])==8
 for f in d['finiteRows']:
  assert f['uid']in UIDS and f['mode']in MODES
  assert len(f['allFaces'])==(14792 if f['uid']==UIDS[0]else 7731)
  assert len(f['ordinaryUnprovedSourceFaces'])==(166 if f['uid']==UIDS[0]else 315)
  for i in f['ordinaryUnprovedSourceFaces']:assert f['allFaces'][i]['sourceFace']==i
  failed.append(dict(uid=f['uid'],mode=f['mode'],unproved=len(f['ordinaryUnprovedSourceFaces']),uncovered=len(f['uncoveredSourceFaces'])))
 assert [len(r['drawnGroundGeometry'])//9 for r in runtime]==[274,1696]
 for folder,name in [(folders[0],'selection.json.gz'),(folders[1],'actual-render-attributes.json.gz'),(folders[2],'diagnostic.json.gz')]:pins.append(ref(folder/name))
 log=REVIEW/'no-worker-schema-pin-preflight.log';assert not log.exists()
 log.write_text('PASS: AST, saved UID/mode/body/face/contact schemas, three terminal receipt SHAs and every evidenceRef. No caller import, geometry predicate, rendering, DB, lease or worker.\n')
 pins.append(ref(log));out=REVIEW/'no-worker-schema-pin-preflight.json';assert not out.exists()
 result=dict(passed=True,workerOrDatabaseStarted=False,caller=ref(CALLER),method=ref(METHOD),preflight=ref(Path(__file__)),checkedRefs=pins,verifiedReceiptEvidenceRefVersions=count,currentManifestSHA256=CURRENT,completeOriginalFaces=22523,completeBodies=1068,mainPodium955Faces=4019,mainTower135Faces=2084,lostLiteralPositivePairs=67,allFourCommonPositivePairs=1288,finiteRows=failed,geometryDecoded=False,numericalPredicatesExecuted=False)
 out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(dict(passed=True,preflight=ref(out),caller=ref(CALLER),method=ref(METHOD),verifiedReceiptEvidenceRefVersions=count),sort_keys=True))
if __name__=='__main__':main()
