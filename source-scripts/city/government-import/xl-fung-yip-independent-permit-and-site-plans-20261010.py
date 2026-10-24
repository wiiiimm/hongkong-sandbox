"""Freeze separate primary permit/address and site-plan evidence, no acceptance."""
import importlib.util
import json
from pathlib import Path
import urllib.request
from datetime import datetime, timezone
import fitz
from run import ROOT, HERE, read, save, digest

BATCH = 'government-xl-fung-yip-independent-permit-and-site-plans-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
RELATIONS = DOC.parent / 'government-xl-fung-yip-three-podium-primary-relationships-20261010'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    assert not DOC.exists(), 'Frozen evidence is immutable'
    DOC.mkdir(parents=True)
    primary = module('fung_independent_permit_source', 'xl-man-fuk-man-oi-primary-relations-20261010.py')
    primary.DOC = DOC
    url = 'https://www.bd.gov.hk/en/resources/codes-and-references/notices-and-reports/GFA_2015.html'
    request = urllib.request.Request(url, headers={'User-Agent': 'HongKongSandbox-source-provenance/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        receipt = dict(url=url, resolvedURL=response.url, status=response.status,
            responseHeaders=dict(response.headers), retrievedAtUTC=datetime.now(timezone.utc).isoformat(),
            sha256=digest(raw), bytes=len(raw))
    (DOC / 'bd-2015-permit-address-list.html').write_bytes(raw)
    save(DOC / 'bd-2015-permit-address-list.request.json', receipt)
    text = raw.decode('utf-8')
    assert 'HK 32/2015(OP)' in text and '345 Des Voeux Road West' in text
    plans = [primary.fetch_pdf('bd-hk32-2015-gfa.pdf',
        'https://www.bd.gov.hk/doc/en/resources/codes-and-references/notices-and-reports/GFA/GFA_c/HK2015032GFACe.pdf'),
        primary.fetch_pdf('tpb-h3-444-2022-site-plan.pdf',
        'https://www.tpb.gov.hk/sc/plan_application/Attachment/20220610/s17s16_A_H3_444_0_gist.pdf')]
    for plan, name in zip(plans, ['bd-hk32-2015-gfa.pdf', 'tpb-h3-444-2022-site-plan.pdf']):
        if not plan.get('isPDF'):
            continue
        document = fitz.open(DOC / name)
        save(DOC / (name + '.text.json'), [dict(page=i+1, text=p.get_text()) for i, p in enumerate(document)])
        for i, page in enumerate(document):
            page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(DOC / (name + f'.page-{i+1}.png'))
    prior = read(RELATIONS / 'diagnostic.json')
    save(DOC / 'diagnostic.json', dict(uids=prior['uids'], exactSourceRelationshipInput=prior,
        primaryPermitAddressList=receipt, plans=plans,
        facts=dict(permit='HK 32/2015(OP)', address='179-180 Connaught Road West & 345 Des Voeux Road West',
            grantDate='2015-07-22', relatedSourceUID='landsd/12728:0',
            distinctOtherPermits=['H234/75', 'H29/86']),
        identityAccepted=False, physicalAccepted=False, installationApproved=False,
        qualification='Distinct permits remain distinct. The primary permit address is an explicit source-version lineage clue. The TPB plan is independent geographic context, not cadastral boundary, common ownership, structure support or tolerance credit. No geometry edits.'))
    result = module('fung_permit_plan_fence', 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'distinct-fung-yip-primary-permit-and-site-plan-evidence-v1',
        [Path(__file__), HERE / 'xl-man-fuk-man-oi-primary-relations-20261010.py',
            RELATIONS / 'result.json', RELATIONS / 'diagnostic.json'],
        dict(uids=prior['uids'], identityAccepted=False, physicalAccepted=False,
            distinctPermits=True, primaryPermitAddress='179-180 Connaught Road West & 345 Des Voeux Road West',
            nextStep='Register actual plan context against exact original intersections before proposing a narrow source-boundary identity. Preserve all separate actors and physical gates.'))
    print(json.dumps(dict(jobId=result['jobId'], plans=[dict(url=p['url'], isPDF=p.get('isPDF')) for p in plans])), flush=True)


if __name__ == '__main__':
    main()
