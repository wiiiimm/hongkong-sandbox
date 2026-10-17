from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013 as a
P=Path(__file__).parent
pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])==43 and len(pins['inputRefs'])==99
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists()
commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013;print('isolated import PASS; no worker/lease/DB')"],'actual-isolated-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
s=json.loads((P/'actual-schema-only.log').read_text());assert s['passed']and s['targetEdges']==[[381,0],[382,0]]and s['ancestorTINFace']==35677 and s['completeCandidateFacets']==11575 and s['completeSourceFacets']==122721 and s['completeCurrentFacets']==9214 and s['savedNegativeRows']==357 and s['areaRowsUnlocated']==257
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.prior.prior.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),commands=commands,declaredCodePins=43,declaredInputPins=99,allPinsVerifiedBeforeAndEnd=True,currentManifestSHA256=a.prior.prior.prior.CURRENT,currentExpectedNativeCount=6650,schemaVerbatim=s,noDOCOrLOCAL=True,noWorkerLeaseOrDB=True)
path=P/'actual-readonly-preparation.json';assert not path.exists();a.save(path,summary);print(json.dumps(summary,sort_keys=True))
