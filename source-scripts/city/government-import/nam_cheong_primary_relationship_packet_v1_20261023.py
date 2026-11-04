"""Preserve primary pair identity and bridge context; no model acceptance."""
import gzip
import sys
from pathlib import Path
import fitz
from run import ROOT, HERE, read, save, digest
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

BATCH = 'government-xl-nam-cheong-primary-relationship-packet-v1-20261023'
SOURCES = [
    ('link-2025-valuation', 'https://www.linkreit.com/-/media/linkreit/investor-relations/financial-reports-and-presentations/financial-report/2025/annual-report-2425-e-book-2.pdf'),
    ('government-2009-footbridge-notice', 'https://www.info.gov.hk/gia/general/200910/23/P200910230095.htm'),
    ('legco-2021-footbridge-plan', 'https://www.legco.gov.hk/yr20-21/english/panels/dev/papers/dev20210126cb1-447-3-e.pdf'),
    ('cedd-2026-footbridge-progress', 'https://www.districtcouncils.gov.hk/ssp/doc/2024_2027/en/dc_meetings_doc/31835/SSP_DC_2026_15_tc_annex.pdf'),
]


def main():
    doc = ROOT / 'docs/astra-city/government-import' / BATCH
    assert not doc.exists()
    doc.mkdir()
    reports = []
    refs = [Path(__file__), HERE.parent / 'landsd-territory/source.py']
    for name, url in SOURCES:
        raw, provenance = request(url, json_expected=False)
        decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
        ext = '.pdf' if decoded.startswith(b'%PDF') else '.html'
        assert (ext == '.pdf') == url.endswith('.pdf')
        path = doc / (name + ext)
        path.write_bytes(decoded)
        save(doc / (name + '-request.json'), dict(provenance, decodedSHA256=digest(decoded)))
        refs.append(path)
        record = dict(name=name, url=url, path=str(path.relative_to(ROOT)), sha256=digest(decoded))
        if ext == '.pdf':
            pdf = fitz.open(stream=decoded, filetype='pdf')
            pages = []
            for n, page in enumerate(pdf):
                text = page.get_text()
                match = ((name == 'link-2025-valuation' and 'Nam Cheong Place' in text and 'Fu Yun House' in text)
                         or (name == 'legco-2021-footbridge-plan' and 'SITE PLAN' in text)
                         or name == 'cedd-2026-footbridge-progress')
                if match:
                    stem = name + '-page-' + str(n + 1)
                    (doc / (stem + '.txt')).write_text(text)
                    page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).save(str(doc / (stem + '.png')))
                    pages.append(dict(pageNumber=n + 1, textPath=str((doc / (stem + '.txt')).relative_to(ROOT)), imagePath=str((doc / (stem + '.png')).relative_to(ROOT))))
            assert pages, name
            record.update(totalPages=len(pdf), relevantPages=pages)
        reports.append(record)
        print(dict(source=name, bytes=len(decoded), relevantPageCount=len(record.get('relevantPages', []))), flush=True)
    report = dict(uids=['landsd/268867:0', 'landsd/270874:0'], sources=reports,
                  sourceEvidenceDiscoveryUsedAI=True, sourceIdentityReviewComplete=False,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Independent primary-source acquisition and rendered relevant pages only. Valuation membership does not establish component support or acceptable foreign intersections. 2021 proposed works and 2026 progress must not be mistaken for the 2009 bridge or installed source identity; precise geometry comparison and ROOT page inspection remain required.')
    save(doc / 'summary.json', report)
    module('nam_primary_relationship_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'nam-cheong-primary-owner-and-bridge-source-packet', refs, report)


if __name__ == '__main__':
    main()
