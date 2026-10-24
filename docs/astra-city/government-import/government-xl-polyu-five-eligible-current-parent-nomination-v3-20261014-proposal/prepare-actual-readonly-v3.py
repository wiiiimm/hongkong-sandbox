"""Authorised isolated import/schema preparation only; no lease/source math.

Reuses ROOT's closed8fixtures and saved891 fixture; never stops V2 or repartitions.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[4]
HERE=ROOT/'source-scripts/city/government-import'
PROPOSAL=Path(__file__).resolve().parent
CALLER=HERE/'polyu_five_eligible_current_parent_nomination_v3_20261014.py'


def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def check(q):
    p=ROOT/q['path'];assert ref(p)==q;return p


def read(p):return json.loads(p.read_text())


def import_child():
    sys.path.insert(0,str(HERE));spec=importlib.util.spec_from_file_location('polyu_v3_readonly_preparation_import',CALLER)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    files={}
    for item in tuple(sys.modules.values()):
        name=getattr(item,'__file__',None)
        if not name:continue
        p=Path(name).resolve()
        if p.is_file()and p.is_relative_to(ROOT):files[str(p.relative_to(ROOT))]=ref(p)
    print(json.dumps(dict(importPassed=True,caller=ref(CALLER),transitiveLocalPythonCodeRefs=[files[k]for k in sorted(files)],
         prefixPackingOrPartitionCalled=False,databaseQueries=0,reservationsClaimed=0),sort_keys=True))


def prepare():
    output=PROPOSAL/'actual-readonly-preparation.json'
    assert not output.exists();logs=PROPOSAL/'closed-actual-readonly-preparation';logs.mkdir(exist_ok=False)
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(CALLER)
    declared=pins['codeRefs']+pins['inputRefs'];known={q['path']:q for q in declared}
    validation_path=PROPOSAL/'ROOT-integration-validation.json';validation=read(validation_path)
    assert (validation['passedTests'],validation['failedTests'],validation['exitCode'])==(8,0,0)
    assert validation['executedCodeRefs']==[ref(HERE/'polyu_v3_computed_outside_enclosure_adapter_draft_20261014.py'),ref(HERE/'test_polyu_v3_computed_outside_enclosure_adapter_draft_20261014.py')]
    saved_log=PROPOSAL/'ROOT-actual-saved891-adapter-fixture.log';fixture=json.loads(saved_log.read_text().strip())
    assert fixture['passed']and fixture['outsideRegions']==143 and fixture['packedPieces']==753
    assert fixture['orderedPackedSHA256']=='fb6b7a468010fceea83b81c8f91ba07328cdcd6bfc014478e790c683f96e8c65'
    assert fixture['actualMaskPartitionCalls']==0 and not fixture['physicalAccepted']
    extras=[ref(validation_path),ref(saved_log)]+validation['evidenceRefs'];all_pins=declared+extras
    commands=[];failure=None;closure=[];schema=None;end_failures=[]
    try:
        for q in all_pins:check(q)
        for label,command in [('import',[sys.executable,__file__,'--import-child']),('schema',[sys.executable,str(CALLER),'--schema-only'])]:
            log=logs/(label+'.log')
            with log.open('wb')as stream:completed=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=False)
            commands.append(dict(label=label,command=command,exitCode=completed.returncode,logRef=ref(log)))
            assert completed.returncode==0,'Actual '+label+' failed; preserve log, no worker'
            result=json.loads(log.read_text().strip())
            if label=='import':
                assert result['importPassed']and result['caller']==ref(CALLER)
                closure=result['transitiveLocalPythonCodeRefs']
                for q in closure:
                    # This driver is newly bound in preparation itself. Other
                    # local imports must already have declared immutable pins.
                    if q['path']==str(Path(__file__).resolve().relative_to(ROOT)):continue
                    assert known.get(q['path'])==q,'Unpinned transitive import: '+q['path']
                    check(q)
            else:schema=result
        assert schema['passed']and schema['savedPrefixRows']==832 and schema['savedPrefixCandidateFaces']==1485
        assert len(schema['complete25Actors'])==25 and len(schema['canonicalResources'])==51
    except BaseException as error:failure=dict(type=type(error).__name__,message=str(error))
    finally:
        for q in all_pins+closure:
            try:check(q)
            except (AssertionError,OSError)as error:end_failures.append(dict(ref=q,error=str(error)))
    passed=failure is None and not end_failures
    evidence={q['path']:q for q in extras+closure+[ref(Path(__file__).resolve()),ref(PROPOSAL/'draft-pins.json')]+[c['logRef']for c in commands]}
    result=dict(passed=passed,caller=ref(CALLER),integrationValidationRef=ref(validation_path),
        saved891FixtureRef=ref(saved_log),saved891FixtureVerbatim=fixture,commands=commands,schemaVerbatim=schema,
        transitiveLocalPythonCodeRefs=closure,declaredCodeRefs=len(pins['codeRefs']),declaredInputRefs=len(pins['inputRefs']),
        beforeAndEndDeclaredPinsVerified=passed,endPinFailures=end_failures,actualFailure=failure,
        prefixProofSHA256Reused='8cc3e885d26958a640069012d5aca9b9d2df4eb0eae03bff41e1046f2165e0c8',
        prefixPackedSHA256Reused='e6f33d8f75803d8178eb4310d7d40498f4d3881be40e36c3ae40b911c294de21',
        prefixPackingOrPartitionReplayed=False,V2NeverStoppedEditedOrLeaseClaimed=True,
        ROOTSerialV2TerminalReleaseReadinessStillRequired=True,databaseQueries=0,reservationsClaimed=0,
        evidenceRefs=[evidence[k]for k in sorted(evidence)])
    target=output if passed else PROPOSAL/'actual-readonly-preparation-failure.json'
    assert not target.exists();target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,preparationRef=ref(target),actualFailure=failure,endPinFailures=len(end_failures),localImportRefs=len(closure),commands=commands),sort_keys=True))
    return 0 if passed else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--import-child',action='store_true');mode.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    if args.import_child:import_child()
    else:sys.exit(prepare())
