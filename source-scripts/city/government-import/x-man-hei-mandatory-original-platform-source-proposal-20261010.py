"""Freeze a source-only proposed Man Hei identity route, not current acceptance."""
import importlib.util,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from man_hei_named_mandatory_original_platform_identity_20261010 import named_proof,UID,PLATFORM,PLAN_URL,PLAN_SHA

BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-man-hei-mandatory-original-platform-source-proposal-20261010';DOC=BASE/BATCH
UPPER=BASE/'government-xl-man-fuk-nine-current-identity-75694-0-20261010';LOWER=BASE/'government-xl-man-fuk-complete-retained-original-physical-v7-20261010'
PRIMARY=BASE/'government-xl-man-hei-man-fuk-primary-platform-context-20261010';CONTEXT=BASE/'government-xl-man-fuk-current-bound-envelope-inputs-v3-20261010'

def main():
    assert not DOC.exists()
    ur=read(UPPER/'selection.json.gz')['rows'][0];pr=read(LOWER/'selection.json.gz')['rows'][0]
    pidentity=read(LOWER/'owned-source-identity.json')['rows'][0];forms=read(CONTEXT/'current-inputs.json.gz')['forms']
    a=decode_original_world_triangles((ROOT/ur['candidate']['path']).read_bytes());b=decode_original_world_triangles((ROOT/pr['candidate']['path']).read_bytes())
    primary=read(PRIMARY/'exact-current-primary.json')['features']
    assert digest((PRIMARY/'ha-man-hei-block-h.pdf').read_bytes())==PLAN_SHA
    text=read(PRIMARY/'ha-man-hei-block-h.pdf.text.json');assert len(text)==1 and 'Chun Man Court Man Hei House (Block H)' in text[0]['text']
    named=dict(url=PLAN_URL,sha256=PLAN_SHA,namedEstate='Chun Man Court',namedBlock='H',namedBuilding='Man Hei House',role='reference-typical-floor-plan-1F-15F')
    proof=named_proof(read(UPPER/'identity.json'),pidentity,ur,pr,a,b,forms,primary,named)
    # Identity verdict is a proposed historical source-fixture verdict only.
    # No current/global manifest or physical acceptance is granted here.
    assert proof['passed'] and proof['reasons']==[] and proof['physicalAccepted'] is False
    save(DOC/'proposed-source-identity.json.gz',proof)
    command=[sys.executable,'-m','unittest','test_man_hei_named_mandatory_original_platform_identity_20261010','-v']
    test=subprocess.run(command,cwd=HERE,text=True,capture_output=True)
    save(DOC/'actual-source-tests.json',dict(command=command,exitCode=test.returncode,stdout=test.stdout,stderr=test.stderr,testsReusedBoundImmutableContactFixture=True,productionRecomputedCompleteContacts=True))
    assert test.returncode==0
    files=[Path(__file__),HERE/'man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'test_man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'source_closed_components.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'lei_tung_named_original_lower_platform_identity_20261010.py',UPPER/'selection.json.gz',UPPER/'identity.json',LOWER/'selection.json.gz',LOWER/'owned-source-identity.json',CONTEXT/'current-inputs.json.gz',BASE/'government-xl-man-fuk-nine-original-platform-interfaces-20261010/diagnostic.json.gz',BASE/'government-xl-man-hei-authored-lower-floor-role-diagnostic-20261010/result.json',BASE/'government-xl-man-hei-mandatory-original-platform-spatial-diagnostic-v2-20261010/result.json']
    files += [ROOT/r['candidate']['path'] for r in [ur,pr]]+[p for p in PRIMARY.iterdir() if p.is_file()]
    visual=BASE/'government-xl-man-hei-original-platform-primary-visuals-20261010';files += [p for p in visual.iterdir() if p.is_file()]
    spec=importlib.util.spec_from_file_location('manhei_source_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
    f.freeze(BATCH,'man-hei-complete-original-mandatory-platform-source-identity-proposal-v1',files,dict(uids=[UID,PLATFORM],sourceFixtureProposalPassed=True,currentIdentityAccepted=False,identityAccepted=False,physicalAccepted=False,completeOriginalFaceCounts=proof['completeOriginalFaceCounts'],completeOriginalPartCounts=proof['completeOriginalPartCounts'],originalPositiveInterfaces=len(proof['completeOriginalPositiveInterfaces']),rawStandaloneCoverageReasonsRetained=proof['rawStandaloneUpperCoverageReasonsRetained'],completeMissingFloorClaim=False,sourceEvidenceInterpretationUsedAI=True,currentBindingRequired=True,nextStep='Root review proposed named contract; replay fresh complete original/current/native/primary receipts and independently accepted platform identity after atomic publication. Both unchanged originals mandatory runtime. Every source physical/foreign/support/foundation/browser gate stays independent.',qualification='Historical source-only fixture. Real partial gaps explicitly retained; no current manifest, standalone import, complete floor coverage, ownership or physical acceptance claimed.'))

if __name__=='__main__':main()
