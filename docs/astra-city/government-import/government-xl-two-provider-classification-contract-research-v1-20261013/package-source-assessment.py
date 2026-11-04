"""Package two existing held source records and official contract evidence.

Standard-library metadata/hash checks only: no model decoding, GIS query,
project imports, database, reservations, geometry or acceptance computation.
"""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
B = ROOT / 'docs/astra-city/government-import'
EXPECTED = {
    'landsd/229852:0': ('B397070873201063C0', '5d92d9d44da6261830820fdf22a794c392df6f9adf08f9551980067a1048507b', '3970708732T20080306', 'Open-sided Structure'),
    'landsd/270876:0': ('B357421737102063C0', '3a40860e5302240d814f907d2f1edabc4b3c7becab1c90d37f406d2a4ce631f2', '3574217371T20050430', 'Tower'),
}
PINS = {}

def pin(path):
    path = path.resolve()
    assert path.is_relative_to(ROOT)
    raw = path.read_bytes()
    value = hashlib.sha256(raw).hexdigest()
    key = str(path.relative_to(ROOT))
    if key in PINS:
        assert PINS[key] == value
    PINS[key] = value
    return raw

def load(path):
    raw = pin(path)
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def one(rows, uid):
    found = [row for row in rows if row['uid'] == uid]
    assert len(found) == 1
    return found[0]

def main():
    assert not (HERE / 'source-bound-assessment.json').exists()
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = load(manifest_path)
    assert PINS[str(manifest_path.relative_to(ROOT))] == 'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
    catalogue_rows = []
    for rel in manifest['officialModelCatalogues']:
        catalogue_rows.extend(load(ROOT / '3d-viewer' / rel)['models'])
    assert len(catalogue_rows) == 6650
    inventory = load(B / 'government-xl-current-fixed-inventory-audit-v1-20261012/inventory.json.gz')
    assert len(inventory['rows']) == 521
    selection = load(B / 'government-xl-sustained-100-inputs-20261006/check-selection.json.gz')
    assert isinstance(selection['rows'], list)
    identity = load(B / 'government-xl-identity-search-20261009/result.json')
    ledger = load(B / 'government-xl-identity-190-actionable-ledger-20261010/result.json')
    directory = load(B / 'government-xl-held-current-directory-audit-20261007/directory-audit.json')
    siblings = load(B / 'government-xl-held-exact-georef-sibling-inventory-20261007/lookup.json')
    pin(ROOT / 'source-scripts/city/government-import/government_owned_identity.py')
    pdf = B / 'xl-terrain-recovery-20261009-provider-exterior-provenance/government-nontextured-exterior-information-sheet.pdf'
    assert hashlib.sha256(pin(pdf)).hexdigest() == '15c820434117b0598f603859f2a9a58c9ba18f6768603bc6a9caf614513db522'
    load(pdf.parent / 'receipt.json')
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            pin(path)
    rows = []
    for uid, (model, sha, csuid, block_type) in EXPECTED.items():
        original = one(selection['rows'], uid)
        later = one(identity['rows'], uid)
        assert original['modelId'] == later['modelId'] == model
        assert original['sourceSHA256'] == later['sourceSHA256'] == sha
        assert hashlib.sha256(pin(ROOT / original['candidate']['path'])).hexdigest() == sha
        assert original['source']['building']['buildingCSUID'] == csuid
        assert original['source']['building']['structureType'] == block_type
        tile = load(ROOT / '3d-viewer' / original['source']['tile'])
        actual_form = one(tile['buildings'], uid)
        assert actual_form['buildingCSUID'] == csuid and actual_form['structureType'] == block_type
        assert not [r for r in catalogue_rows if r['uid'] == uid or r['sha256'] == sha]
        indexed = load(B / f"government-xl-sustained-100-20261006-{uid.split('/')[1].split(':')[0]}-0/indexed-preflight.json")
        early = load(indexed_path := B / f"government-xl-sustained-100-20261006-{uid.split('/')[1].split(':')[0]}-0/result.json")
        ownership = load(B / 'government-xl-source-ownership-196-20261006' / (uid.split('/')[1].replace(':', '-') + '.json.gz'))
        section = load(B / 'government-xl-source-sections-196-20261006' / (uid.split('/')[1].replace(':', '-') + '.json.gz'))
        rows.append({
            'uid': uid, 'modelId': model, 'sourceSHA256': sha,
            'originalSelectionRow': original,
            'currentTileForm': actual_form,
            'currentFormExactlyEqualsHistoricalSelectionForm': actual_form == original['source']['building'],
            'fixed521HistoricalInventoryRow': one(inventory['rows'], uid),
            'savedIdentitySearchRowVerbatim': later,
            'savedActionableLedgerRowVerbatim': one(ledger['rows'], uid),
            'savedPackageDirectoryRowVerbatim': one(directory['rows'], uid),
            'savedExactSiblingRowVerbatim': one(siblings['rows'], uid),
            'earlyResultJobId': early['jobId'], 'earlyResultPath': str(indexed_path.relative_to(ROOT)),
            'indexedPreflightVerbatim': indexed, 'sourceOwnershipVerbatim': ownership,
            'sourceSectionsVerbatim': section,
            'notInstalledAtCapturedCurrentManifest': True,
            'observedModelSubtype': model[11:13], 'observedGISBlockType': block_type,
            'classificationCrosswalkFound': False, 'revisionMismatchProved': False,
            'identityAccepted': False, 'physicalAccepted': False, 'installationApproved': False,
        })
    for rel, expected_sha in PINS.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected_sha
    result = {
        'scope': 'two held original government sources; primary classification contracts only',
        'createdAtUTC': datetime.now(timezone.utc).isoformat(),
        'initialResearchHEAD': '73b76384eb136e1da0f1f06e0192bb53b0b15227',
        'completionHEAD': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'currentManifestSHA256': PINS[str(manifest_path.relative_to(ROOT))],
        'currentNativeEntries': len(catalogue_rows), 'fixedInventoryRows': 521,
        'historicalOfficialQueriesNotReplayed': True,
        'newEvidence': 'January 2026 Building FSDT English/Chinese specifications plus exact official GIS metadata/schema; actual specification pages visually reviewed',
        'contractAssessment': {
            '3DInformationSheet': 'September 2025 naming table defines building subtype 01=Tower, 02=Podium; version character changes for model/texture revisions.',
            'olderB1000': 'Building polygon layer contains open-sided outlines and its automatic POLY_TYPE is T. This historical layer description explains possible semantic lineage but establishes no source-specific 3D/GIS equivalence.',
            'currentFSDT': 'January 2026 v1.1 lists four BuildingBlockType examples separately and describes CSUID T as Tower, P as Podium. This newer explicit specification prevents treating the older layer wording alone as a current type crosswalk.',
            'revision': 'Current metadata has monthly revision semantics; DateStamp is record import/modification date and model version is model/texture revision code. Their values do not establish common epoch or direction of source classification change.',
            '229852': '01 and CSUID T agree, but exact GIS Open-sided differs. No published contract explicitly maps this Open-sided record to subtype01. Retain source-specific interpretation/revision hold.',
            '270876': '02 explicitly Podium disagrees with exact GIS Tower and CSUID T. No alternate 02 meaning, published successor or exact historical crosswalk found in the bounded evidence.',
            'proposedAcceptanceCorrection': None,
            'whyNoCorrection': 'The actual primary contracts do not justify a type-equivalence exception. Keep all original classifier and spatial gates unchanged.',
            'genuineNextEvidence': 'Provider-maintained exact modelID-to-CSUID/type crosswalk or dated exact revision lineage for these two identifiers, or a corrected provider original model/revision. Near-identical footprint and owner imagery alone cannot resolve this type discrepancy.',
        },
        'rows': rows, 'inputHashes': PINS,
        'databaseAccess': False, 'reservationClaims': 0, 'numericalModelWorkers': 0,
        'modelGeometryChanges': 0, 'sourcePoseChanges': 0, 'terrainChanges': 0,
        'identityAccepted': False, 'physicalAccepted': False, 'newlyInstalled': 0,
        'publication': False, 'currentAcceptance': False, 'permanentRejection': False,
    }
    with (HERE / 'source-bound-assessment.json').open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({'rows': len(rows), 'literalPins': len(PINS),
                      'currentManifestSHA256': result['currentManifestSHA256'],
                      'currentNativeEntries': len(catalogue_rows),
                      'classificationCrosswalkFound': False, 'acceptanceCorrectionProposed': False,
                      'SHA256': hashlib.sha256((HERE / 'source-bound-assessment.json').read_bytes()).hexdigest()}))

if __name__ == '__main__':
    main()
