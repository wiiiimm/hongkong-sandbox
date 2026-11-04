"""UNEXECUTED ROOT-reviewed preparation only; no source proof/DB/lease."""
from pathlib import Path
import ast,hashlib,json,os,re,subprocess,sys

PROPOSAL=Path(__file__).resolve().parent
ROOT=PROPOSAL.parents[3]
HERE=ROOT/'source-scripts/city/government-import'
PY='/tmp/astra-city-venv/bin/python'
CALLER=HERE/'polyu_saved_parent_cell_repacking_caller_v1_draft_20261014.py'
HELPER=HERE/'polyu_computed_parent_cell_enclosure_v1_draft_20261014.py'
TEST=HERE/'test_polyu_computed_parent_cell_enclosure_v1_draft_20261014.py'
sys.path.insert(0,str(HERE))
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    pins=json.loads((PROPOSAL/'draft-pins.json').read_text());assert pins['caller']==ref(CALLER)
    def fence():
        for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):assert ref(ROOT/q['path'])==q,q['path']
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==pins['currentManifestSHA256']
    fence();folder=PROPOSAL/'closed-readonly-preparation';folder.mkdir()
    commands=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    def run(name,cmd):
        log=folder/(name+'.log')
        with log.open('xb')as f:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        commands.append(dict(command=cmd,exitCode=p.returncode,log=ref(log)));return p.returncode,log
    rc,log=run('eight-parent-packing-fixtures',[PY,str(TEST)]);fence()
    assert rc==0 and re.search(r'Ran 8 tests\b',log.read_text()),'preserve actual fixture failure; do not proceed'
    validation=PROPOSAL/'helper-validation.json'
    write(validation,dict(passedTests=8,failedTests=0,exitCode=rc,executedCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(TEST),ref(log)]))
    rc,_=run('isolated-import',[PY,'-c',"import sys,importlib.util;sys.path.insert(0,sys.argv[1]);s=importlib.util.spec_from_file_location('polyu_saved_hole_draft',sys.argv[2]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print('isolated import PASS; no owned/main call')",str(HERE),str(CALLER)]);fence();assert rc==0
    rc,_=run('schema-only',[PY,str(CALLER),'--schema-only']);fence();assert rc==0
    # Literal local Python imports only. Dynamic freezer paths remain exactly
    # bound by inherited declared codeRefs; no permissive dependency resolution.
    declared={q['path']:q['sha256']for q in pins['codeRefs']};pending=[CALLER,HELPER,TEST];seen=set();imports=[]
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);q=ref(p);assert declared[q['path']]==q['sha256'];imports.append(q)
        tree=ast.parse(p.read_text(),filename=str(p))
        for n in ast.walk(tree):
            names=([a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[])
            for name in names:
                local=HERE/(name.split('.')[0]+'.py')
                if local.is_file():pending.append(local)
    fence();write(PROPOSAL/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),helperValidationRef=ref(validation),commands=commands,transitiveLiteralPythonRefs=sorted(imports,key=lambda q:q['path']),currentManifestSHA256=pins['currentManifestSHA256'],beforeEndAllDeclaredPinsVerified=True,noDBLeaseWorkerSourceMathOrProductionImport=True,evidenceRefs=distinct_refs([ref(Path(__file__)),ref(validation)]+[q['log']for q in commands]+imports)))
    print(json.dumps(dict(passed=True,preparation=ref(PROPOSAL/'actual-readonly-preparation.json'),fixturesPassed=8,actualCommands=len(commands))))
if __name__=='__main__':main()
