"""Save complete original support progress and precise remaining compute holds.

The entire unchanged government source is retained. Support investigation is
complete for this terrain proposal; current whole-model acceptance is separate.
"""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-man-fuk-v7-complete-source-support-checkpoint-20261010';DOC=BASE/BATCH
PHYS=BASE/'government-xl-man-fuk-complete-retained-original-physical-v7-20261010'
NAMES=[PHYS.name,'government-xl-man-fuk-v7-complete-conservative-clearance-20261010',
       'government-xl-man-fuk-v7-complete-paired-finite-clearance-20261010',
       'government-xl-man-fuk-v7-complete-finite-wall-contexts-v2-20261010',
       'government-xl-man-fuk-v7-complete-original-support-20261010',
       'government-xl-man-fuk-v7-complete-finite-wall-grade-source-20261010',
       'government-xl-man-fuk-v7-literal-rendered-four-post-footings-v2-20261010']

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists();refs=[Path(__file__)];receipts={}
    for name in NAMES:
        folder=BASE/name;r=read(folder/'result.json');receipts[name]=r
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        # Source/terrain proofs remain immutable. Current manifest context may
        # later change only through unrelated installation; archive that exact
        # context explicitly rather than assigning this proposal new acceptance.
        for item in r['evidenceRefs']:
            p=ROOT/item['path']
            assert p.is_file() and digest(p.read_bytes())==item['sha256']
            refs.append(p)
        refs.extend(p for p in folder.rglob('*') if p.is_file())
    graph=read(BASE/NAMES[4]/'diagnostic.json.gz');grade=read(BASE/NAMES[5]/'diagnostic.json.gz')
    context=read(BASE/NAMES[3]/'diagnostic.json.gz');literal=read(BASE/NAMES[6]/'diagnostic.json.gz')
    assert graph['completeOriginalFaces']==10661 and graph['completeOriginalComponentCount']==93
    assert graph['ordinaryGroundRootComponents']==[2,3,4,5]
    assert grade['resolvedOriginalComponents']==list(range(93)) and grade['unresolvedOriginalComponents']==[] and grade['exactExposedWallGradeRootComponents']==[0]
    assert literal['strictLiteralRenderedFourPostFootings'] and not literal['arithmeticParityCredit']
    assert context['buriedUpwardOriginalFaces']==[] and context['unexposedIndividualWallFaces']==[]
    assert len(context['affectedOriginalFaces'])==97
    physical=receipts[PHYS.name];held=sorted(r.split(':',1)[1] for r in physical['reasons'] if r.startswith('terrain-regresses-neighbour:'))
    assert len(held)==11
    native=read(PHYS/'native-neighbour-checks.json');assert native['resolved']==['landsd/75697:0'] and native['rows'][0]['passed']
    selection=read(PHYS/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256']
    DOC.mkdir();archive=DOC/'captured-manifest.json';archive.write_bytes(manifest.read_bytes());refs.append(archive)
    result=dict(uids=['landsd/266062:0'],sourceSHA256=selection['rows'][0]['sourceSHA256'],
        completeOriginalFaces=10661,completeOriginalComponents=93,sourceSupportComponentsResolved=93,
        genuineOrdinaryPostRoots=[2,3,4,5],exactExposedWallGradeRoot=[0],
        independentLiteralRenderedPostFootingsPassed=True,affectedExposedSteepWalls=97,
        buriedUpwardOriginalFaces=[],wholeFoundationPassed=True,retainedManOiPassed=True,
        remainingNeighbourIntegrationUids=held,rawPhysicalReasonsPreserved=physical['reasons'],
        humanStatus='held-for-compute',humanDecisionRequired=False,aiGeometryModellingRequired=False,
        currentRegionalRebindRequired=True,currentAcceptancePassed=False,publication=False,newlyInstalled=0,
        modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,
        capturedManifestSHA256=selection['manifestSHA256'],capturedManifest=ref(archive),
        receiptJobIds={name:r['jobId'] for name,r in receipts.items()},
        nextStep='Integrate recovered neighbouring original sources with the platform, retain current-source identity and all whole-source/current-neighbour runtime gates; Man Hei needs a separately bounded original-platform identity. Rebind current acceptance after any intervening map publication.',
        qualification='All93 original components have strict source support for the explicit changed-terrain proposal. Four ordinary footings additionally pass independent literal-rendered production support checks. No structural role is guessed, no original geometry is changed, and no whole-model acceptance or installed credit is granted.')
    save(DOC/'diagnostic.json',result)
    s=importlib.util.spec_from_file_location('man_fuk_support_checkpoint_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.freeze(BATCH,'complete-original-man-fuk-source-support-actionable-hold-v1',sorted(set(refs)),result)
    print(json.dumps(dict(supportComponentsResolved=93,neighbourIntegrationsRemaining=len(held),publication=False,newlyInstalled=0)),flush=True)

if __name__=='__main__':main()
