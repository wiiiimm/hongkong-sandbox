from pathlib import Path
import sys,json,subprocess,hashlib,base64,os
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import'
sys.path.insert(0,str(HERE))
import upton_v6_saved_coverage_failure_attribution_draft_v1_20261013 as a
P=Path(__file__).parent
def run(cmd,name):
    p=P/name;assert not p.exists()
    r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    p.write_bytes(r.stdout);assert r.returncode==0,(cmd,r.returncode,p)
    return dict(command=cmd,exitCode=r.returncode,log=a.ref(p))
pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
for q in refs:a.check(q)
commands=[]
commands.append(run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_v6_saved_coverage_failure_attribution_draft_v1_20261013 as a;print(a.ref(Path(a.__file__)) if False else 'import PASS; no worker or lease')"],'actual-import.log'))
commands.append(run([sys.executable,str(HERE/'upton_v6_saved_coverage_failure_attribution_draft_v1_20261013.py'),'--schema-only'],'actual-schema-only.log'))
_,_,output,_,replay,_,_,_,main,basic=a.load()
b=basic['findings'];assert b['uid']==basic['uid']=='landsd/79883:0'
assert len(b['worlds'])==1 and b['worlds'][0]['mode']=='capturedConstructorFloat32World'
w=b['worlds'][0];assert w['findings']['currentClearCandidateUnproved']==[17]
assert len({r['mode']for r in main['worlds']})==4
patch=a.read(a.prior.HERE/'local'/a.prior.MAX.name/'private-upton-v6-geometry-bound-overlap-reviewed.json')
mesh=patch['nativeMesh'];position=np.asarray(mesh['position'],dtype=np.float32).reshape(-1,3);index=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)
assert len(index)==11575 and replay['actualNativeHeightIndexProjectedDeterminantThreshold']==1e-10
source=(ROOT/'3d-viewer/city/native-terrain.js').read_text()
expression='const determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz);'
assert expression in source and 'if(Math.abs(determinant)<1e-10)continue;'in source
py=[]
for ai,bi,ci in index:
    ax,az=map(float,position[ai,[0,2]]);bx,bz=map(float,position[bi,[0,2]]);cx,cz=map(float,position[ci,[0,2]])
    py.append((bz-cz)*(ax-cx)+(cx-bx)*(az-cz))
py=np.asarray(py,dtype='<f8')
js="""let s='';for await(const c of process.stdin)s+=c;const m=JSON.parse(s),position=new Float32Array(m.position),index=m.index;const out=Buffer.alloc(index.length/3*8);for(let t=0;t<index.length;t+=3){const a=index[t]*3,b=index[t+1]*3,c=index[t+2]*3;const ax=position[a],az=position[a+2],bx=position[b],bz=position[b+2],cx=position[c],cz=position[c+2];const determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz);out.writeDoubleLE(determinant,t/3*8);}process.stdout.write(out.toString('base64'));"""
js_path=P/'actual-determinant-operator-smoke.mjs';assert not js_path.exists();js_path.write_text(js)
rr=subprocess.run(['node',str(js_path)],input=json.dumps(mesh).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=ROOT)
assert rr.returncode==0,rr.stderr.decode();node=base64.b64decode(rr.stdout,validate=True)
assert node==py.tobytes(),'binary64 determinant or signed-zero mismatch'
js_values=np.frombuffer(node,dtype='<f8');assert np.array_equal(np.abs(js_values)>=1e-10,np.abs(py)>=1e-10)
proof=dict(passed=True,completeCandidateFaces=len(index),production=a.ref(ROOT/'3d-viewer/city/native-terrain.js'),actualNodeScript=a.ref(js_path),exactExpression=expression,pythonAndNodeBinary64BytesEqual=True,signedZeroBytesPreserved=True,projectedDeterminantSHA256=hashlib.sha256(node).hexdigest(),heightIndexed=int(np.count_nonzero(np.abs(py)>=1e-10)),heightIndexExcluded=int(np.count_nonzero(np.abs(py)<1e-10)),basicUID=b['uid'],basicMode=w['mode'],basicCurrentClearRegressions=[17],noCoverageFiniteOrAcceptanceProof=True)
proof_path=P/'actual-basic-schema-and-js-operator-contract.json';assert not proof_path.exists();a.save(proof_path,proof)
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.CURRENT
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),commands=commands,declaredCodePins=len(pins['codeRefs']),declaredInputPins=len(pins['inputRefs']),allBeforeEndPinsVerified=True,productionDeterminantAndBasicSchema=a.ref(proof_path),currentManifestSHA256=a.CURRENT,noFiniteCoverageProofLeaseOrDB=True)
out=P/'actual-readonly-preparation.json';assert not out.exists();a.save(out,summary);print(json.dumps(summary,sort_keys=True))
