"""Preserve complete unchanged Man Fuk/Man Oi research and actionable holds."""
import importlib.util, json
from pathlib import Path
from run import ROOT,HERE,read,save,digest

BATCH='government-xl-man-fuk-original-investigation-checkpoint-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
NAMES=['government-xl-man-fuk-complete-foreign-context-20261010',
       'government-xl-man-fuk-man-oi-original-recovery-20261010',
       'government-xl-man-fuk-man-oi-complete-original-contacts-20261010']

def main():
    assert not DOC.exists(),'Fresh immutable checkpoint required'
    base=DOC.parent
    context=read(base/NAMES[0]/'diagnostic.json.gz')
    recovered=read(base/NAMES[1]/'selection.json.gz')
    contacts=read(base/NAMES[2]/'diagnostic.json.gz')
    assert contacts['completeOriginalFaceCounts']==[10661,2160]
    assert contacts['completeOriginalComponentCounts']==[93,4]
    assert contacts['completeOriginalContacts']['allPairsExamined']
    rows=contacts['completeOriginalContacts']['contacts']
    assert len(rows)==12 and all(r['dimension']==1 and r['componentA']==r['componentB']==0 for r in rows)
    paths=[Path(__file__)]
    for name in NAMES:paths.extend(p for p in (base/name).rglob('*') if p.is_file())
    for obj in [context,contacts]:
        for p,h in obj['inputHashes'].items():
            q=ROOT/p
            # The captured current manifest is historical after Glorious Peak;
            # it is frozen below, never silently rebound to today's bytes.
            if p=='3d-viewer/city/data/manifest.json':continue
            assert digest(q.read_bytes())==h,p
            paths.append(q)
    for r in recovered['rows']:
        p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];paths.append(p)
    manifest=context['manifestSHA256']
    import subprocess
    old=subprocess.check_output(['git','show','d4589bce:3d-viewer/city/data/manifest.json'],cwd=ROOT)
    assert digest(old)==manifest
    DOC.mkdir(parents=True)
    (DOC/'historical-manifest.json').write_bytes(old)
    (DOC/'README.md').write_text('''# Man Fuk original platform and Man Oi investigation

Produced by Codex on 10 October 2026 from unchanged Lands Department sources. No historical Lantau map reference is used. Both original government assets retain their complete indexed graph, pose and compressed hashes: Man Fuk podium B364461960802063C0 has 10,661 faces/93 parts; Man Oi tower B364721945401063C0 has 2,160 faces/4 parts. Exact native run membership and stable government candidate identity were checked during recovery. The already cached platform required no transfer; the tower required 29,925 transfer bytes.

Every original face was tested against every current local form at the captured manifest. The broad platform covers 98.5679396522% of its own current footprint and extends at most 1.8632758971m. Its largest excess is 1.7224253748m² into Man Oi. All 23 positive-area original faces in that overlap belong to the platform's original main component; every smaller foreign overlap remains recorded too.

Complete exact rational source-pair contact enumeration found 12 line contacts, all between the two main components at original height43.375m. These are source interfaces only: they do not establish a ground root, legal ownership, collision exemption or whole-model acceptance. No surface-area contact was found. All 12,821 original faces and97 components remain unchanged.

The official Housing Authority Block A typical 1/F–15/F floor-plan PDF identifies Man Fuk House by name. Its original URL, bytes, hash and request metadata are saved alongside the image. It is not an estate site plan, surveyed placement, platform ownership or support proof. Do not infer a shared-envelope waiver from the estate name.

Actionable hold: obtain exact primary source identity/component coverage for the platform/Man Oi relationship, then complete independent current whole-source terrain, foundation, all neighbouring actors, component support, runtime, staged/live browser and guarded publication gates. None is installed or permanently rejected by this checkpoint. All zero-area contacts, absence results and raw failures stay queryable; do not repeat recovery or contact enumeration without changed inputs. The captured manifest is explicitly archived because a later unrelated installation changed the global manifest.
''')
    spec=importlib.util.spec_from_file_location('man_fuk_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.freeze(BATCH,'complete-original-platform-counterpart-identity-investigation-v1',paths,
        dict(uids=contacts['uids'],sourceSHA256s=contacts['sourceSHA256s'],completeOriginalFaces=12821,
             completeOriginalComponents=97,completePositiveOriginalLineContacts=12,
             completePositiveOriginalAreaContacts=0,capturedManifestSHA256=manifest,
             historicalManifestAlias=dict(originalPath='3d-viewer/city/data/manifest.json',sha256=manifest,
                 archive=dict(path=str((DOC/'historical-manifest.json').relative_to(ROOT)),sha256=manifest)),
             identityAccepted=False,physicalAccepted=False,scriptFullAcceptancePassed=False,
             currentHeldReason='exact-primary-platform-counterpart-identity-and-complete-current-physical-gates-pending',
             heldRequires='source-investigation-and-scripted-physical-checks',humanDecisionRequired=False,
             aiGeometryModellingRequired=False,sourceEvidenceInterpretationUsedAI=True,
             nextStep='Capture exact active primary records and primary site/component relationship; all97parts and complete current physical/runtime/browser gates must pass independently.'))
    scope=dict(paths=sorted({str(DOC.relative_to(ROOT)),*[str(p.relative_to(ROOT)) for p in paths]}),
               aliases=[dict(path='3d-viewer/city/data/manifest.json',sha256=manifest,archivePath=str((DOC/'historical-manifest.json').relative_to(ROOT)))])
    Path('/tmp/man-fuk-root-original-investigation-scope-20261010.json').write_text(json.dumps(scope,indent=2))
    print(dict(jobId=result['jobId'],newlyInstalled=0,closedPaths=len(scope['paths'])),flush=True)

if __name__=='__main__':main()
