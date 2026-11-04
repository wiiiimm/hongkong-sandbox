"""ROOT-reviewed exact pair property membership from primary owner records.

No extension, bridge ownership, collision, engineering support or installation credit.
"""
from pathlib import Path
import fitz
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-nam-cheong-primary-pair-membership-review-v1-20261023'
PACKET = 'government-xl-nam-cheong-primary-relationship-packet-v1-20261023'
CAPTURE = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
PRIMARY = 'government-xl-nam-cheong-primary-records-v1-20261023'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc, packet = base / BATCH, base / PACKET
    assert not doc.exists() and not (packet / 'result.json').exists()
    refs = [Path(__file__), HERE / 'nam_cheong_primary_relationship_packet_v1_20261023.py']
    pins = {}
    for name in [CAPTURE, PRIMARY]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    rows = take(CAPTURE, base / CAPTURE / 'selection.json.gz')
    selection = {r['uid']: r for r in rows['rows']}
    assert set(selection) == {'landsd/268867:0', 'landsd/270874:0'}
    official = take(PRIMARY, base / PRIMARY / 'footprints.json')['features']
    bycsuid = {r['attributes']['BuildingCSUID']: r['attributes'] for r in official}
    for uid, name in [('landsd/268867:0', 'Nam Cheong Place'), ('landsd/270874:0', 'Fu Yun House')]:
        row = selection[uid]
        record = bycsuid[row['source']['building']['buildingCSUID']]
        assert record['GeoRefNo'] == row['modelId'][1:11]
        assert record['BuildingNameEN'] == name
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
    source = packet / 'link-2025-valuation.pdf'
    request = read(packet / 'link-2025-valuation-request.json')
    assert digest(source.read_bytes()) == request['sha256'] == request['decodedSHA256']
    assert request['url'] == 'https://www.linkreit.com/-/media/linkreit/investor-relations/financial-reports-and-presentations/financial-report/2025/annual-report-2425-e-book-2.pdf'
    pdf = fitz.open(source)
    page = pdf[200]
    text = page.get_text()
    assert 'Nam Cheong Place' in text and 'Fu Yun House (Ancillary Facilities Block)' in text
    assert 'formerly known as Fu Cheong Shopping Centre' in text
    image = packet / 'link-2025-valuation-page-201.png'
    assert image.read_bytes() == page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).tobytes('png')
    refs.extend([source, packet / 'link-2025-valuation-request.json', image, packet / 'link-2025-valuation-page-201.txt'])
    notice = packet / 'government-2009-footbridge-notice.html'
    nrequest = read(packet / 'government-2009-footbridge-notice-request.json')
    assert digest(notice.read_bytes()) == nrequest['sha256'] == nrequest['decodedSHA256']
    refs.extend([notice, packet / 'government-2009-footbridge-notice-request.json'])
    failurepath = doc / 'prior-packet-fetch-failure.txt'
    failurepath.parent.mkdir(parents=True)
    failurepath.write_text(Path('/tmp/nam-cheong-primary-relationship-packet-v1.log').read_text())
    assert 'CERTIFICATE_VERIFY_FAILED' in failurepath.read_text() and 'legco.gov.hk' in failurepath.read_text()
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == rows['manifestSHA256']
    refs.append(manifest)
    report = dict(uids=sorted(selection), sourceSHA256ByUid={u:r['sourceSHA256'] for u,r in selection.items()},
                  currentManifestSHA256=rows['manifestSHA256'], sourceIdentityReviewUsedAI=True,
                  samePropertyMembershipAccepted=True, fullOriginalIdentityAccepted=False,
                  reviewedSource=dict(path=str(source.relative_to(ROOT)), sha256=digest(source.read_bytes()), pdfPageNumber=201, printedPageNumber=199, propertyEntry=45),
                  reviewedImage=dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes())),
                  reviewer='Codex ROOT', interpretation='The exact official Nam Cheong Place and Fu Yun House records are consistent with the owner valuation listing Fu Yun House as an ancillary facilities block within Nam Cheong Place. This supports pair property attribution only.',
                  limits=['No identity credit for source extensions or other actors.', 'V Walk and Fu Cheong open-sided actor remain foreign and retained.', 'No support, ground-crossing wall, collision, visual/runtime publication or installation approval.', '2009 bridge notice establishes a scheme only; no exact source bridge geometry or built-status approval.', 'LegCo 2021 PDF acquisition failed certificate verification; no insecure retry, PDF evidence or source rejection inferred. 2026 plan was not fetched.'],
                  physicalAccepted=False, installationApproved=False, sourceGeometryChanges=0)
    save(doc / 'summary.json', report)
    module('nam_pair_membership_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-nam-cheong-fu-yun-primary-property-membership-review', refs, report)


if __name__ == '__main__':
    main()
