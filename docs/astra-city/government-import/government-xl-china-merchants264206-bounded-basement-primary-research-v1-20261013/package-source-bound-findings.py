"""Standard-library metadata/provenance packaging; no model decoding or predicates."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
B = ROOT / 'docs/astra-city/government-import'
SOURCE = '0ff5adae4dae90e856af6fb6f40112a24198668ca9dfc66e9570b058739b50fb'
UID = 'landsd/264206:0'
PINS = {}

def pin(path):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    raw = path.read_bytes()
    key = str(path.relative_to(ROOT))
    sha = hashlib.sha256(raw).hexdigest()
    if key in PINS:
        assert PINS[key] == sha
    PINS[key] = sha
    return raw

def load(path):
    raw = pin(path)
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def write(name, value):
    with (HERE / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def main():
    assert not (HERE / 'source-bound-findings.json').exists()
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert hashlib.sha256(pin(manifest)).hexdigest() == 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
    selection = load(B / 'government-xl-retained-group-central-wrapper-20261009-264206-0/selection.json.gz')
    rows = [r for r in selection['rows'] if r['uid'] == UID]
    assert len(rows) == 1
    row = rows[0]
    assert row['modelId'] == 'B336901655802063C1' and row['sourceSHA256'] == SOURCE
    assert hashlib.sha256(pin(ROOT / row['candidate']['path'])).hexdigest() == SOURCE
    assert row['source']['building']['buildingCSUID'] == '3369016558P20060312'
    tile = load(ROOT / '3d-viewer' / row['source']['tile'])
    forms = [r for r in tile['buildings'] if r['uid'] == UID]
    assert len(forms) == 1 and forms[0] == row['source']['building']
    triage = load(B / 'government-xl-citywalk-china-merchants-readonly-recovery-triage-v1-20261013/recovery-plan.json')
    old = B / 'government-xl-china-merchants-wrapper-foundation-result-20261009'
    foundation = load(old / 'foundation.json')
    result = load(old / 'result.json')
    prior_receipt = load(old / 'neon-sync.json')
    pin(old / 'README.md')
    followup = load(B / 'government-xl-two-current-lower-component-followups-20261008/264206-0.json')
    assert foundation['uid'] == UID and foundation['sourceSHA256'] == SOURCE
    assert foundation['foundation']['fullyBuriedUpwardTriangles'] == 102
    assert foundation['strictFoundationAccepted'] is False and foundation['publication'] is False
    retrieval = load(HERE / 'retrieval.json')
    allowed = {'date','etag','last-modified','content-type','content-length','content-disposition'}
    for source in retrieval['sources']:
        assert set(k.lower() for k in source.get('provenanceHeaders', {})) <= allowed
        if source['saved']:
            assert hashlib.sha256(pin(HERE / 'primary-documents' / source['filename'])).hexdigest() == source['sha256']
    exports = load(HERE / 'document-page-exports.json')
    for page in exports['pages']:
        assert hashlib.sha256(pin(HERE / page['png'])).hexdigest() == page['pngSHA256']
        assert hashlib.sha256(pin(HERE / page['text'])).hexdigest() == page['textSHA256']
        assert max(page['width'], page['height']) == 2400
    contact = (HERE / 'primary-documents/china-merchants-owner-contact.html').read_bytes().decode('utf-8')
    assert '香港干诺道中168—200号信德中心' in contact and '招商局大厦40楼' in contact
    search_queries = [
        '"China Merchants Tower" "East" "basement" Shun Tak',
        '"招商局大廈" "東座" "地下" 圖',
        'site:shuntakcentre.com.hk floor plan basement',
        '"Shun Tak Centre" architect section podium basement',
        'site:shuntakgroup.com "Shun Tak Centre" basement',
        'site:shuntakcentre.com "floor" "plan"',
        'site:srarchitects.com "Shun Tak"',
        'site:mtr.com.hk "Shun Tak Centre" pdf',
        '"Shun Tak Centre" "basement" "plan" site:gov.hk',
        '"Shun Tak Centre" "floor plan" site:shuntakgroup.com',
        '"Shun Tak Centre" "basement" "B01" plan',
        '"Spence Robinson" "Shun Tak Centre" plans',
        'site:cmhk.com "招商局大厦" "信德"',
        'site:mtr.com.hk archive "Sheung Wan" "layout"',
    ]
    write('bounded-search-record.json', {
        'queriesIssuedDuringThisTask': search_queries,
        'individualQueryTimestampsNotCaptured': True,
        'rawRetrievalIsLimitedToFiveListedURLs': True,
        'wrongSiteExcluded': 'Beijing China Merchants Tower annual-report result',
        'wrongContextExcluded': 'WKCD EIA references to distant Shun Tak Centre; not site plans',
        'noExactBasementGroundFloorPlanOrSectionObtained': True,
        'failedRetrievalsNotRetried': [s for s in retrieval['sources'] if not s['saved']],
        'searchStoppedAfterUsefulSiteAndBasementInventoryEvidence': True,
    })
    write('source-bound-findings.json', {
        'recordedUTC': datetime.now(timezone.utc).isoformat(),
        'uid': UID, 'modelId': row['modelId'], 'sourceSHA256': SOURCE,
        'sourceCSUID': row['source']['building']['buildingCSUID'],
        'originalSelectionRowVerbatim': row, 'currentFormVerbatim': forms[0],
        'currentFormEqualsHistoricalSelection': True,
        'currentManifestSHA256': PINS[str(manifest.relative_to(ROOT))],
        'HEADObserved': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'priorFoundationVerbatim': foundation,
        'priorFoundationResultVerbatim': result,
        'priorReceiptVerbatimHistoricalOnlyNoFreshNeonRead': prior_receipt,
        'priorLowerInterfaceResultVerbatim': followup,
        'priorTriageChinaMerchantsVerbatim': triage['chinaMerchants'],
        'primaryFinding': {
            'source': 'primary-documents/shun-tak-owner-circular-20200826.pdf',
            'sourceSHA256': '4a2f120c350861db503be2c4f2f3122d7cbfe733d63f78ff463e90bc19dba0dd',
            'documentDate': '2020-08-26', 'valuationDate': '2020-05-31',
            'physicalPagesOneBasedActuallyViewed': [1,85,86],
            'printedPages': ['V-5','V-6'],
            'address': 'Shun Tak Centre (Podium), 168–200 Connaught Road Central, Sheung Wan',
            'lot': 'Inland Lot 8517', 'conditionsOfGrant': 'UB11612',
            'registeredOwnerAsReportedIn2020': 'Shun Tak Centre Limited',
            'basementLettableAreaM2': 4231.51, 'groundLettableAreaM2': 661.74,
            'landSearchBasementUnitIdentifiers': 'B01–B10', 'landSearchGroundUnitIdentifiers': 'G01 and G01A',
            'scopeCaveat': 'Document concerns acquired units, not a complete registered building plan; reported lettable areas do not give geometric correspondence.',
        },
        'ownerAddressCorroboration': {'source': 'primary-documents/china-merchants-owner-contact.html', 'sourceSHA256': '435f7b970a0ed301a92af7a9c967aed015638f15b29c89c21b33e0c7ce9bbedf', 'observedAddress': '香港干诺道中168—200号信德中心 • 招商局大厦40楼'},
        'mtrLayoutActuallyViewed': {'source': 'primary-documents/mtr-sheung-wan-layout.pdf', 'sourceSHA256': 'aa8299af8b9b1298f68e87e072087083b811fd5bbf9237975235fd5633111ecc', 'finding': 'Schematic station concourses, platforms and exits including D; no Shun Tak basement unit plan, registered site coordinates or floor-level elevations.'},
        'limitedSourceConclusion': 'A real basement at the exact named site is documented by a primary owner circular; neither failed low group is identified as a basement component.',
        'exactCorrespondenceNotEstablished': {
            'threeFaceGroupUpwardAreaM2': 127.56332951808271,
            'eightFaceGroupUpwardAreaM2': 13.696135520935059,
            'failedSourceFaceIDsAndXZNotPresentInSixGroupFoundationSummary': True,
            'sitePlanSectionAndComponentRegistrationMissing': True,
            'sourceCSUIDDateAndPrimaryValuationDateDifferent': True,
            'noAbsoluteHKPDLevelOrSurveyedFloorGradeFromRetrievedPages': True,
        },
        'nextConcreteAction': {
            'primaryDocumentTarget': 'Approved basement/GF plan plus section or datum-level schedule for Inland Lot 8517, Shun Tak Centre, Conditions of Grant UB11612; identify B01–B10 and G01/G01A.',
            'potentialCustodiansNotContacted': ['Shun Tak Centre Limited / owner building records', 'Buildings Department approved building-plan records', 'Spence Robinson project archive (builder search lead only; raw builder retrieval denied)'],
            'prerequisiteSourceOnlyMapping': 'Locate exact original face IDs and complete original connected-body coordinates for the saved 3- and 8-face groups from existing completed source data; do not rerun foundation or assign roles from height.',
            'decisionChangingEvidence': 'A genuine plan/section whose site and datum can be tied to those complete original low bodies could support a bounded basement role proposal. A generic basement inventory alone cannot.',
        },
        'noModelDecode': True, 'noNumericalModelWorker': True, 'noFoundationRerun': True,
        'noDatabaseOrReservationActivity': True, 'noGeometryOrPoseChange': True,
        'noSourceRoleApproval': True, 'physicalAccepted': False, 'currentAcceptance': False,
        'noInstallationOrPublication': True,
    })
    closed_logs = HERE / 'closed-execution-logs'
    closed_logs.mkdir(exist_ok=False)
    for name in ('primary-retrieval','primary-page-exports'):
        shutil.copyfile(Path('/tmp') / f'china-merchants264206-{name}-20261013.log', closed_logs / f'{name}.log')
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            pin(path)
    for relative, sha in PINS.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == sha
    write('review-file-pins.json', {'kind': 'source-only-primary-research-exact-literal-inputs', 'allInputHashes': PINS, 'allPinsVerifiedAfterPackaging': True})
    print(json.dumps({'sourceSHA256': SOURCE, 'literalPins': len(PINS), 'actualCurrentFormEqualsHistorical': True, 'primaryDocumentsSaved': sum(s['saved'] for s in retrieval['sources']), 'limitedRetrievalFailures': sum(not s['saved'] for s in retrieval['sources']), 'actualDocumentPagesExported': len(exports['pages']), 'allInputHashesUnchanged': True, 'sourceRoleAcceptance': False}))

if __name__ == '__main__':
    main()
